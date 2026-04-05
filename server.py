from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from scalar_fastapi import get_scalar_api_reference
from pydantic import BaseModel
from typing import Optional, Any
from env import CyberSOCEnv
from models import Observation, Action, RewardInfo, State

DESCRIPTION = """
<div align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/1/13/Shield-security.svg/200px-Shield-security.svg.png" width="100" />
  <h1>🛡️ Project Aegis : Advanced Cyber SOC</h1>
</div>

Welcome to the **Next-Generation Incident Response Engine**. 
This OpenEnv environment trains AI agents to handle real-world Advanced Persistent Threats (APTs) in a simulated Blue Team operation.

### ✨ Platform Capabilities
* 🔴 **Live Threat Streaming**: Real-time evaluation of network alerts.
* 🧠 **Autonomous Mitigation**: Intelligent actions ranging from isolation to routing.
* 📊 **Comprehensive State Tracking**: Real-time metrics and reward scaling.
"""

app = FastAPI(
    title="SOC Operator Terminal // PROJECT AEGIS",
    description=DESCRIPTION,
    version="v2.0.0-HACKATHON-EDITION",
    contact={
        "name": "Project Aegis Security Team",
        "url": "https://github.com/scalar"
    },
    docs_url=None, 
    redoc_url=None
)

@app.get("/", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
        dark_mode=True,
        custom_css="""
            @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&family=JetBrains+Mono:wght@400;700&display=swap');

            :root {
                --scalar-color-accent: #00ffcc;
                --scalar-background-1: #050510;
                --scalar-background-2: #080b18;
                --scalar-background-3: #111526;
                --scalar-color-1: #e0f2ff;
                --scalar-color-2: #84a5cd;
                --scalar-color-3: #4b668f;
                --scalar-border-color: rgba(0, 255, 204, 0.15);
                --scalar-font: 'Outfit', sans-serif !important;
                --scalar-font-code: 'JetBrains Mono', monospace !important;
            }

            body {
                background: radial-gradient(circle at 50% -20%, #11203A, #050510 80%) !important;
                background-attachment: fixed !important;
            }

            .scalar-card {
                background: rgba(11, 14, 25, 0.6) !important;
                backdrop-filter: blur(16px) !important;
                -webkit-backdrop-filter: blur(16px) !important;
                border: 1px solid rgba(0, 255, 204, 0.1) !important;
                border-radius: 16px !important;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5), inset 0 0 0 1px rgba(255, 255, 255, 0.02) !important;
                transition: all 0.3s ease;
            }

            .scalar-card:hover {
                border-color: rgba(0, 255, 204, 0.3) !important;
                box-shadow: 0 8px 32px rgba(0, 255, 204, 0.1), inset 0 0 0 1px rgba(255, 255, 255, 0.05) !important;
            }

            .scalar-button {
                background: linear-gradient(135deg, rgba(0,255,204,0.2) 0%, rgba(0,255,204,0.05) 100%) !important;
                border: 1px solid rgba(0, 255, 204, 0.4) !important;
                border-radius: 8px !important;
                box-shadow: 0 4px 15px rgba(0,255,204,0.1) !important;
                text-transform: uppercase !important;
                letter-spacing: 1px !important;
                font-weight: 600 !important;
            }

            .scalar-button:hover {
                background: rgba(0, 255, 204, 0.15) !important;
                box-shadow: 0 4px 20px rgba(0,255,204,0.3) !important;
            }

            h1, h2, h3 {  
                font-family: 'Outfit', sans-serif !important; 
                font-weight: 600 !important;
                letter-spacing: -0.5px !important;
                text-shadow: 0 0 20px rgba(0, 255, 204, 0.2);
            }
        """
    )

env_instance = CyberSOCEnv(difficulty="medium")

class ResetRequest(BaseModel):
    difficulty: str = "medium"
    num_alerts: int = 5

class StepResponse(BaseModel):
    observation: Observation
    reward: float
    done: bool
    info: RewardInfo

@app.post("/reset", response_model=Observation)
def reset_env(req: Optional[ResetRequest] = None):
    global env_instance
    if req is None:
        req = ResetRequest()
    env_instance = CyberSOCEnv(difficulty=req.difficulty, num_alerts=req.num_alerts)
    return env_instance.reset()

@app.post("/step", response_model=StepResponse)
def step_env(action: Action):
    global env_instance
    obs, reward, done, info = env_instance.step(action)
    return StepResponse(observation=obs, reward=reward, done=done, info=info)

@app.get("/state", response_model=State)
def get_state():
    global env_instance
    return env_instance.state()

@app.get("/health")
def health_check():
    return {"status": "ok"}

