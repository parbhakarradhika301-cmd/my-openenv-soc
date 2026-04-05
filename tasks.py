import random
from models import SecurityAlert

VALID_MITIGATIONS = ['ignore', 'block_ip', 'isolate_host', 'escalate_tier2']

EASY_ALERTS = [
    {"source_ip": "192.168.1.5", "target_ip": "10.0.0.8", "alert_type": "Failed Login", "payload_snippet": "ssh_login_failed: admin", "user_agent": "Nmap NSE", "mitigation": "ignore"},
    {"source_ip": "45.33.22.11", "target_ip": "10.0.0.22", "alert_type": "Port Scan", "payload_snippet": "SYN Stealth Scan on ports 22, 80, 443", "user_agent": "-", "mitigation": "block_ip"},
    {"source_ip": "10.0.0.50", "target_ip": "10.0.0.50", "alert_type": "Antivirus Signature", "payload_snippet": "EICAR Test File Detected", "user_agent": "system", "mitigation": "ignore"},
    {"source_ip": "203.0.113.5", "target_ip": "10.0.2.14", "alert_type": "Brute Force", "payload_snippet": "450 failed logins in 2 minutes", "user_agent": "Hydra", "mitigation": "block_ip"},
    {"source_ip": "192.168.1.100", "target_ip": "8.8.8.8", "alert_type": "DNS Query", "payload_snippet": "google.com", "user_agent": "Chrome/114", "mitigation": "ignore"},
]

MEDIUM_ALERTS = [
    {"source_ip": "172.16.5.9", "target_ip": "10.0.3.15", "alert_type": "SQL Injection", "payload_snippet": "' OR 1=1 --", "user_agent": "Mozilla/5.0 (Windows NT)", "mitigation": "block_ip"},
    {"source_ip": "10.0.4.4", "target_ip": "198.51.100.22", "alert_type": "Suspicious Download", "payload_snippet": "GET /malware.exe", "user_agent": "curl/7.88.1", "mitigation": "escalate_tier2"},
    {"source_ip": "192.168.2.10", "target_ip": "10.0.0.5", "alert_type": "Unusual Internal Login", "payload_snippet": "Successful login via RDP at 3:00 AM", "user_agent": "Remote Desktop", "mitigation": "escalate_tier2"},
    {"source_ip": "130.211.0.0", "target_ip": "10.0.2.20", "alert_type": "XSS Attempt", "payload_snippet": "<script>alert('XSS')</script>", "user_agent": "Python-urllib/3.9", "mitigation": "block_ip"},
    {"source_ip": "10.0.1.20", "target_ip": "10.0.1.20", "alert_type": "High CPU Usage", "payload_snippet": "Process 'crypto_miner.exe' utilizing 99% CPU", "user_agent": "crypto_miner.exe", "mitigation": "isolate_host"},
]

HARD_ALERTS = [
    {"source_ip": "10.0.0.8", "target_ip": "10.0.0.200", "alert_type": "Lateral Movement", "payload_snippet": "invoke-mimikatz.ps1 via WinRM", "user_agent": "PowerShell", "mitigation": "isolate_host"},
    {"source_ip": "10.0.5.55", "target_ip": "104.21.5.10", "alert_type": "Command and Control beacon", "payload_snippet": "SSL handshake to known DGA domain xzqwyk.com", "user_agent": "svchost.exe", "mitigation": "isolate_host"},
    {"source_ip": "192.168.1.20", "target_ip": "192.168.1.50", "alert_type": "Data Exfiltration", "payload_snippet": "Archiving /var/www using tar, transferring 50GB over port 443", "user_agent": "rsync", "mitigation": "isolate_host"},
    {"source_ip": "192.168.1.5", "target_ip": "10.0.0.15", "alert_type": "Possible Phishing", "payload_snippet": "Found macro inside 'Invoice_Q3.xlsm' calling WScript.Shell", "user_agent": "Outlook", "mitigation": "escalate_tier2"},
    {"source_ip": "203.0.113.99", "target_ip": "10.0.0.1", "alert_type": "Zero-Day Exploit Attempt", "payload_snippet": "Heap spray pattern detected in incoming RPC request", "user_agent": "Custom RPC client", "mitigation": "escalate_tier2"},
]

def generate_task_alerts(difficulty: str, num_alerts: int = 5) -> list[dict]:
    """Generates a list of SIEM alerts based on difficulty."""
    if difficulty == "easy":
        pool = EASY_ALERTS
    elif difficulty == "medium":
        pool = MEDIUM_ALERTS
    elif difficulty == "hard":
        pool = HARD_ALERTS
    else:
        pool = EASY_ALERTS + MEDIUM_ALERTS + HARD_ALERTS

    alerts = []
    for i in range(num_alerts):
        template = random.choice(pool)
        alerts.append({
            "id": f"alert_{difficulty}_{i}",
            "source_ip": template["source_ip"],
            "target_ip": template["target_ip"],
            "alert_type": template["alert_type"],
            "payload_snippet": template["payload_snippet"],
            "user_agent": template["user_agent"],
            "correct_mitigation": template["mitigation"]
        })
    return alerts

class TaskGrader:
    def __init__(self, difficulty: str, alerts: list[dict]):
        self.difficulty = difficulty
        self.alerts = alerts
        self.total = len(alerts)
        self.correct = 0
    
    def grade(self) -> float:
        """Returns a score from 0.0 to 1.0"""
        if self.total == 0:
            return 1.0
        return self.correct / self.total
