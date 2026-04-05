from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field

class SecurityAlert(BaseModel):
    id: str = Field(description="Unique identifier for the alert")
    source_ip: str = Field(description="The IP address originating the traffic")
    target_ip: str = Field(description="The internal IP address targeted")
    alert_type: str = Field(description="The category of the alert from the SIEM")
    payload_snippet: str = Field(description="A sample of the network payload or command executed")
    user_agent: str = Field(description="HTTP User-Agent if applicable, or process name")

class Observation(BaseModel):
    current_alert: Optional[SecurityAlert] = Field(description="The active alert needing triage. Null if queue is empty.")
    alerts_remaining: int = Field(description="Number of alerts left in the backlog")
    alerts_processed: int = Field(description="Number of alerts already triaged in this episode")

class Action(BaseModel):
    mitigation: str = Field(
        description="The action to take. Valid options: 'ignore', 'block_ip', 'isolate_host', 'escalate_tier2'"
    )

class RewardInfo(BaseModel):
    is_correct: bool = Field(description="Whether the mitigation was the optimal choice")
    correct_mitigation: str = Field(description="The actual correct mitigation")
    penalty: float = Field(description="Any negative penalty applied (e.g., false positive block, invalid action format)")

class State(BaseModel):
    observation: Observation
    total_alerts: int
    correctly_mitigated: int
    incorrectly_mitigated: int
