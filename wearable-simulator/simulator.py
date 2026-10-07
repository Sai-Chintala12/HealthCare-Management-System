"""Generates realistic fake wearable data for a patient and sends it to the API.
Usage: python simulator.py patient@example.com password123 [days]"""
import random
import sys
from datetime import datetime, timedelta, timezone
import requests

API = "http://localhost:5000/api"
email, password = sys.argv[1], sys.argv[2]
days = int(sys.argv[3]) if len(sys.argv) > 3 else 7

token = requests.post(f"{API}/auth/login", json={"email": email, "password": password}).json()["token"]
headers = {"Authorization": f"Bearer {token}"}

now = datetime.now(timezone.utc)
batch = []
for d in range(days):
    day = now - timedelta(days=d)
    for h in range(0, 24, 2):  # a heart-rate reading every 2 hours
        t = day.replace(hour=h, minute=0, second=0, microsecond=0)
        asleep = h < 6
        batch.append({"metric_type": "heart_rate", "unit": "bpm", "source": "simulator",
                      "value": round(random.gauss(55 if asleep else 75, 5)), "recorded_at": t.isoformat()})
    batch.append({"metric_type": "steps", "unit": "count", "source": "simulator",
                  "value": random.randint(3000, 12000), "recorded_at": day.isoformat()})
    batch.append({"metric_type": "sleep_hours", "unit": "h", "source": "simulator",
                  "value": round(random.uniform(5.5, 8.5), 1), "recorded_at": day.isoformat()})
    batch.append({"metric_type": "spo2", "unit": "%", "source": "simulator",
                  "value": random.randint(95, 99), "recorded_at": day.isoformat()})

r = requests.post(f"{API}/health/measurements", json=batch, headers=headers)
print(r.status_code, r.json())