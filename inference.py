import os
import json
from typing import List, Optional
from openai import OpenAI
from env import CyberSOCEnv
from models import Action
from tasks import VALID_MITIGATIONS

IMAGE_NAME = os.getenv("IMAGE_NAME")
API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("HF_TOKEN") or os.getenv("API_KEY") or "dummy-key"
API_BASE_URL = os.getenv("API_BASE_URL") or "https://api.openai.com/v1"
MODEL_NAME = os.getenv("MODEL_NAME") or "gpt-3.5-turbo"
BENCHMARK = os.getenv("MY_ENV_BENCHMARK", "cyber-soc-analyst")
SUCCESS_SCORE_THRESHOLD = 0.5

client = OpenAI(
    api_key=API_KEY,
    base_url=API_BASE_URL
)

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )

def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)

def call_llm(alert) -> str:
    prompt = f"""
    You are an expert Cybersecurity SOC (Blue Team) Analyst. 
    Analyze the following SIEM alert and provide exactly ONE mitigation action from this list:
    {VALID_MITIGATIONS}

    Output ONLY the action string, nothing else. Focus on isolating malware and APTs, escalating unknowns, blocking noisy scanners, and ignoring false positives.

    Alert Details:
    Source IP: {alert.source_ip}
    Target IP: {alert.target_ip}
    Alert Type: {alert.alert_type}
    Payload Snippet: {alert.payload_snippet}
    User Agent: {alert.user_agent}
    """
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )
        predicted_mit = (completion.choices[0].message.content or "").strip().lower()
        for mit in VALID_MITIGATIONS:
            if mit in predicted_mit:
                return mit
    except Exception as e:
        pass
    return "ignore"

def evaluate_baseline(difficulty: str, num_alerts: int = 5):
    env = CyberSOCEnv(difficulty=difficulty, num_alerts=num_alerts)
    
    log_start(task=difficulty, env=BENCHMARK, model=MODEL_NAME)
    
    rewards: List[float] = []
    steps_taken = 0
    done = False
    
    obs = env.reset()
    
    while not done:
        steps_taken += 1
        
        if obs.current_alert is None:
            break
            
        mitigation_action = call_llm(obs.current_alert)
        action = Action(mitigation=mitigation_action)
        
        try:
            obs, reward, done, info = env.step(action)
            error_val = None
        except Exception as e:
            reward = 0.0
            done = True
            error_val = str(e)
            
        rewards.append(reward)
        log_step(step=steps_taken, action=mitigation_action, reward=reward, done=done, error=error_val)
        
    score = env.grader.grade()
    success = score >= SUCCESS_SCORE_THRESHOLD
    
    log_end(success=success, steps=steps_taken, score=score, rewards=rewards)

if __name__ == "__main__":
    evaluate_baseline("easy")
    evaluate_baseline("medium")
    evaluate_baseline("hard")
