"""Jev 快速上手(OpenRouter 版):一次调用混问 Noul / Choice / Score 三种判断。

跑法:  ./run.sh quickstart.py
"""

import json
import os
import urllib.request

API_URL = "https://openrouter.ai/api/alpha/decisions"
API_KEY = os.environ.get("OPENROUTER_API_KEY")
if not API_KEY:
    raise SystemExit("缺少 OPENROUTER_API_KEY —— 请确认通过 ./run.sh 运行(它会读取 .env)")

payload = {
    "model": "typesafe/jev-1.13",
    "state": (
        "Hi, I've been trying to connect my Stripe account for 3 days and the "
        "integration keeps failing. I'm losing sales. Please help ASAP."
    ),
    "questions": {
        "department": {
            "type": "choice",
            "instructions": "Which team should handle this?",
            "criteria": {
                "billing": "Payment or subscription issues.",
                "technical": "Bugs or integration problems.",
                "sales": "Pricing or account questions.",
            },
        },
        "frustration": {
            "type": "score",
            "instructions": "How frustrated does the customer appear?",
            "criteria": [
                "Calm, just stating facts",
                "Frustrated but civil",
                "Very angry, strong language",
            ],
        },
        "is_urgent": {
            "type": "noul",
            "instructions": "The message conveys urgency or time-sensitivity.",
        },
    },
}

req = urllib.request.Request(
    API_URL,
    data=json.dumps(payload).encode("utf-8"),
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    },
)

try:
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8", "replace")[:300]
    raise SystemExit(f"API 返回 {e.code}: {body}")

answers = data.get("answers", {})
dept = answers.get("department", {})
frus = answers.get("frustration", {})
urg = answers.get("is_urgent", {})

print("部门      :", dept.get("choice"), f"(置信度 {dept.get('confidence')})")
print("愤怒打分  :", frus.get("score"), f"(置信度 {frus.get('confidence')})")
print("紧急概率  :", urg.get("noul"), "(0~1,是紧急的概率)")
print("用量      :", data.get("usage"))
