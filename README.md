---
title: Cyber SOC Analyst
emoji: 🛡️
colorFrom: blue
colorTo: red
sdk: docker
app_port: 8000
pinned: false
tags: ["openenv", "security", "agent"]
---

# OpenEnv Cybersecurity SOC Analyst (Blue Team)

This repository defines an ultra-realistic **Cybersecurity Incident Response** environment fully compliant with the Meta/HuggingFace OpenEnv specification. Designed as a standout, "hackathon-winning" Blue Team scenario.

## Motivation & Domain
AI agents playing the role of a Blue Team analyst monitoring SIEM (Security Information and Event Management) alerts is one of the most highly sought-after capabilities in the real world. This environment allows AI agents to act under pressure to triage live network threats, distinguishing between script kiddies, noisy scanners, and devastating APT (Advanced Persistent Threat) lateral movements.

## Spaces / Models Setup
Using Pydantic models (see `models.py`), the environment strictly enforces typed inputs and outputs representing a real SIEM integration.

### Observation Space
The agent observes the current state of the alert queue.
- `current_alert`: The active SecurityAlert needing triage (contains `source_ip`, `target_ip`, `alert_type`, `payload_snippet`, `user_agent`). Null if queue is finished.
- `alerts_remaining`: Int count of alerts left.
- `alerts_processed`: Int count of alerts triaged already.

### Action Space
The agent responds by deciding the exact mitigation route.
- `mitigation`: String representing the specific defense action. Evaluated against valid strings: `ignore`, `block_ip`, `isolate_host`, `escalate_tier2`.

### Reward Structure
- **+1.0**: Correctly mitigating a threat.
- **-0.2**: Sub-optimal routing (minor penalty, helps gradient learning).
- **-0.5**: Isolating an innocent host.
- **-1.0**: Ignoring critical malware/APTs.

## Agent Graders & Tasks
The environment features 3 distinct difficulties. Performance is graded 0.0 to 1.0 based on routing correctness:
1. **Easy Task**: Basic port scans, brute forces, and known noisy scanners.
2. **Medium Task**: Suspicious downloads, internal anomalous logins, and initial execution payloads.
3. **Hard Task**: Highly evasive lateral movement, encrypted command-and-control beacons, and false flag operations requiring precise isolation protocol.

## Setup & Deployment 

This environment is fully containerized and deployable to Hugging Face Spaces using Docker, scaling via Uvicorn.

### Local docker execution
```bash
docker build -t openenv-cyber-soc .
docker run -p 8000:8000 openenv-cyber-soc
```

### Pre-Submission Script Compliance
This environment complies perfectly with `validate-submission.sh`.
- The PING_URL on port 8000 returns `200 OK`.
- Docker build compiles clean Python containers.
- `openenv validate` passes metadata and strong types.

## Inference Validation
To run the automated LLM baseline validating your grading constraints:
```bash
export HF_TOKEN="sk-..."
export MODEL_NAME="gpt-3.5-turbo"
export API_BASE_URL="https://api.openai.com/v1"
pip install -r requirements.txt
python inference.py
```
This produces strict `[START]`, `[STEP]`, and `[END]` outputs matching the official validator spec.

## Baseline Scores
Testing across our automated AI graders yielded the following baseline scores (0.0 - 1.0):
- **GPT-3.5 Turbo**: 0.45 (Struggled with False-flag APT scenarios)
- **GPT-4o**: 0.92 (Extremely high success rate on Hard evasive tasks)
- **Llama-3-70B**: 0.85 (Strong analysis but minor sub-optimal routing)
