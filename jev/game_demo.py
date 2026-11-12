"""Game demo: 潜行游戏里的守卫 NPC 决策,中英文对照。

跑法:  ./run.sh game_demo.py
"""

import json
import os
import urllib.request

API_URL = "https://openrouter.ai/api/alpha/decisions"
API_KEY = os.environ["OPENROUTER_API_KEY"]


def ask(state, questions):
    payload = {"model": "typesafe/jev-1.13", "state": state, "questions": questions}
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


# ---------- 中文场景 ----------
cn_state = {
    "场景": "潜行关卡。玩家蹲行在守卫背后约 3 米处,处于阴影中。2 秒前玩家撞倒了一个罐子,守卫没有回头。",
    "守卫状态": "普通巡逻中",
}
cn_questions = {
    "heard_sound": {
        "type": "noul",
        "instructions": "守卫听到了异响吗?",
    },
    "next_action": {
        "type": "choice",
        "instructions": "守卫接下来应该做什么?",
        "criteria": {
            "继续巡逻": "没有察觉,继续原路线",
            "回头查看": "起疑但不确定,回头检查",
            "呼叫增援": "认为有入侵者,呼叫支援",
            "进入战斗": "确认敌人在附近,立即进入战斗",
        },
    },
    "alert_level": {
        "type": "score",
        "instructions": "守卫的警觉程度",
        "criteria": ["放松", "起疑", "高度戒备", "战斗状态"],
    },
}

# ---------- 英文同款场景 ----------
en_state = {
    "scene": "Stealth level. The player is crouched ~3 meters behind a guard, in shadow. 2 seconds ago the player knocked over a can; the guard did not look back.",
    "guard_status": "On a regular patrol",
}
en_questions = {
    "heard_sound": {"type": "noul", "instructions": "Did the guard hear the noise?"},
    "next_action": {
        "type": "choice",
        "instructions": "What should the guard do next?",
        "criteria": {
            "keep_patrolling": "No suspicion, continue the route",
            "turn_and_check": "Suspicious but unsure, turn around and check",
            "call_backup": "Believes there is an intruder, calls for support",
            "engage_combat": "Confirmed enemy nearby, enters combat",
        },
    },
    "alert_level": {
        "type": "score",
        "instructions": "How alert is the guard?",
        "criteria": ["Relaxed", "Suspicious", "High alert", "Combat ready"],
    },
}

for label, state, questions in [("中文", cn_state, cn_questions), ("English", en_state, en_questions)]:
    r = ask(state, questions)
    a = r["answers"]
    print(f"===== {label} =====")
    print("  听到异响    :", a["heard_sound"]["noul"])
    print("  下一步行动  :", a["next_action"]["choice"], f"(置信度 {a['next_action']['confidence']})",
          "| 概率分布:", a["next_action"]["probabilities"])
    print("  警觉程度    :", a["alert_level"]["score"], f"(置信度 {a['alert_level']['confidence']})")
    print("  成本        : $%.7f" % r["usage"]["cost"])
    print()
