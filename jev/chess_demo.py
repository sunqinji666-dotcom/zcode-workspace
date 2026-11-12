"""象棋场景演示:Jev 能不能判断局面?

三段对照测试:
1. 中国象棋·红方大优(自然语言描述)
2. 中国象棋·均势局面(自然语言描述)
3. 国际象棋·简单残局(FEN 格式,测它懂不懂 FEN)

跑法:  ./run.sh chess_demo.py
"""

import json
import os
import urllib.request

API_URL = "https://openrouter.ai/api/alpha/decisions"
API_KEY = os.environ["OPENROUTER_API_KEY"]


def ask(label, state, questions):
    payload = {"model": "typesafe/jev-1.13", "state": state, "questions": questions}
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        r = json.loads(resp.read().decode("utf-8"))
    a = r["answers"]
    print(f"===== {label} =====")
    print("  谁占优  :", a["who_better"]["choice"],
          "| 概率:", a["who_better"]["probabilities"],
          f"| 置信度 {a['who_better']['confidence']}")
    print("  优势概率:", a["advantage_prob"]["noul"])
    print("  复杂程度:", a["complexity"]["score"], "/ 3")
    print("  $" + f"{r['usage']['cost']:.7f}")
    print()


questions = {
    "who_better": {
        "type": "choice",
        "instructions": "当前局面哪一方占优?",
        "criteria": {
            "红方占优": "红方(先手描述方)有明显优势",
            "均势": "双方接近平衡,胜负未分",
            "黑方占优": "黑方有明显优势",
        },
    },
    "advantage_prob": {
        "type": "noul",
        "instructions": "描述中处于优势的一方(第一位)获胜的可能性明显大于对手。若局面均势则应偏低。",
    },
    "complexity": {
        "type": "score",
        "instructions": "局面的复杂程度(对棋手判断的要求)",
        "criteria": ["简单:少子残局,路线清晰", "中等:需要一定计算", "复杂:多子纠缠,容易走错"],
    },
}

# 1) 中国象棋 · 红方大优
ask(
    "中国象棋 · 红方大优(自然语言)",
    "中国象棋残局。红方剩:车、马、炮、两个兵;黑方只剩:一个车、一个卒。轮红方走,黑方将门已被打开。",
    questions,
)

# 2) 中国象棋 · 均势
ask(
    "中国象棋 · 均势(自然语言)",
    "中国象棋中局。双方子力都是车马炮各一、四个兵(卒)未过河,阵型工整,轮红方走,刚走完常规的巡河车。",
    questions,
)

# 3) 国际象棋 · FEN
ask(
    "国际象棋 · FEN(白王+车 vs 黑王)",
    "Chess endgame position in FEN: 8/8/8/4k3/8/8/4K3/7R w - - 0 1",
    questions,
)
