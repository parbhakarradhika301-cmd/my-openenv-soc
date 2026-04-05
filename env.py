from typing import Tuple, Dict, Any, Optional
from models import Observation, Action, RewardInfo, State, SecurityAlert
from tasks import generate_task_alerts, TaskGrader, VALID_MITIGATIONS

class CyberSOCEnv:
    def __init__(self, difficulty: str = "easy", num_alerts: int = 5):
        self.difficulty = difficulty
        self.num_alerts = num_alerts
        self._raw_alerts = []
        self._queue = []
        self._current_alert_data = None
        self.grader = None
        
        self.correctly_mitigated = 0
        self.incorrectly_mitigated = 0
        self.total_alerts = num_alerts
        
        self.reset()
        
    def reset(self) -> Observation:
        """Resets the environment to a new queue of alerts."""
        self._raw_alerts = generate_task_alerts(self.difficulty, self.num_alerts)
        self._queue = self._raw_alerts.copy()
        self.grader = TaskGrader(self.difficulty, self._raw_alerts)
        
        self.correctly_mitigated = 0
        self.incorrectly_mitigated = 0
        
        return self._get_observation()

    def _get_observation(self) -> Observation:
        if len(self._queue) > 0:
            self._current_alert_data = self._queue[0]
            current_alert = SecurityAlert(
                id=self._current_alert_data["id"],
                source_ip=self._current_alert_data["source_ip"],
                target_ip=self._current_alert_data["target_ip"],
                alert_type=self._current_alert_data["alert_type"],
                payload_snippet=self._current_alert_data["payload_snippet"],
                user_agent=self._current_alert_data["user_agent"]
            )
        else:
            self._current_alert_data = None
            current_alert = None

        return Observation(
            current_alert=current_alert,
            alerts_remaining=len(self._queue),
            alerts_processed=self.num_alerts - len(self._queue)
        )

    def state(self) -> State:
        """Returns the full internal state."""
        return State(
            observation=self._get_observation(),
            total_alerts=self.total_alerts,
            correctly_mitigated=self.correctly_mitigated,
            incorrectly_mitigated=self.incorrectly_mitigated
        )

    def step(self, action: Action) -> Tuple[Observation, float, bool, RewardInfo]:
        """Processes an action and returns (observation, reward, done, info)."""
        if self._current_alert_data is None:
            return self._get_observation(), 0.0, True, RewardInfo(is_correct=False, correct_mitigation="", penalty=0.0)

        correct_mit = self._current_alert_data["correct_mitigation"]
        predicted_mit = action.mitigation.lower().strip()
        
        penalty = 0.0
        is_correct = False
        reward = 0.0

        if predicted_mit not in VALID_MITIGATIONS:
            penalty = -0.5
            reward = penalty
        elif predicted_mit == correct_mit:
            is_correct = True
            reward = 1.0 # Significant reward for correct triage
            self.correctly_mitigated += 1
            if self.grader:
                self.grader.correct += 1
        else:
            is_correct = False
            # Specific penalties based on severity limits
            if correct_mit == 'isolate_host' and predicted_mit == 'ignore':
                reward = -1.0 # High penalty for ignoring malware
            elif predicted_mit == 'isolate_host' and correct_mit == 'ignore':
                reward = -0.5 # Medium penalty for isolating an innocent user
            else:
                reward = -0.2 # Slight penalty for sub-optimal routing
            self.incorrectly_mitigated += 1

        # Move queue forward
        self._queue.pop(0)
        
        done = len(self._queue) == 0
        obs = self._get_observation()
        
        info = RewardInfo(
            is_correct=is_correct,
            correct_mitigation=correct_mit,
            penalty=penalty
        )
        
        return obs, reward, done, info
