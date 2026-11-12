"""Jev 到底能干嘛 —— 3 个真实场景演示(全中文)。

跑法:  ./run.sh what_can_jev_do.py
"""

import json
import os
import urllib.request

API_URL = "https://openrouter.ai/api/alpha/decisions"
API_KEY = os.environ["OPENROUTER_API_KEY"]


def ask(title, state, questions):
    payload = {"model": "typesafe/jev-1.13", "state": state, "questions": questions}
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        r = json.loads(resp.read().decode("utf-8"))
    print("=" * 52)
    print("【" + title + "】")
    print("=" * 52)
    for name, ans in r["answers"].items():
        if ans["type"] == "noul":
            print(f"  {name}: {ans['noul']:.2f} (0=否 1=是)")
        elif ans["type"] == "choice":
            print(f"  {name}: {ans['choice']}  (把握 {ans['confidence']:.2f})")
        else:
            print(f"  {name}: {ans['score']} 分 (把握 {ans['confidence']:.2f})")
    print(f"  — 耗时体感<1秒, 花费 ${r['usage']['cost']:.6f}")
    print()


# 场景 1:直播弹幕实时判断(AI 虚拟人直播最需要的能力)
ask(
    "直播弹幕实时判断(一次判 6 项)",
    "刚过去的 10 秒里直播间收到 3 条弹幕:\n"
    "1. 主播这操作也太菜了吧哈哈哈\n"
    "2. 请问这个滤镜叫什么名字?\n"
    "3. 已举报,垃圾内容",
    {
        "弹幕1_恶意": {"type": "noul", "instructions": "第 1 条是恶意攻击还是单纯玩笑?"},
        "弹幕2_是提问": {"type": "noul", "instructions": "第 2 条是在提问吗?"},
        "弹幕3_是黑粉": {"type": "noul", "instructions": "第 3 条来自恶意用户吗?"},
        "优先回复哪条": {
            "type": "choice",
            "instructions": "主播现在最该回复哪一条?",
            "criteria": {"弹幕1": "应互动", "弹幕2": "应回答", "弹幕3": "应忽略", "都不理": "冷处理"},
        },
        "直播间氛围": {
            "type": "score",
            "instructions": "当前直播间氛围如何?",
            "criteria": ["冷清", "正常", "活跃", "火爆"],
        },
        "需要人工介入": {"type": "noul", "instructions": "需要真人主播或管理员介入处理吗?"},
    },
)

# 场景 2:短视频发布质检(发布前的把关)
ask(
    "短视频发布质检(发布前 200 毫秒把关)",
    "视频标题:今天我用 AI 给奶奶做了个会说话的相册,她哭了\n"
    "视频简介:AI 修复老照片 + 声音克隆,让照片里的人和奶奶对话。不含任何商业推广。",
    {
        "标题吸引力": {
            "type": "score",
            "instructions": "这个标题在抖音的吸引力如何?",
            "criteria": ["划走", "一般", "能停留", "很有吸引力", "爆款潜质"],
        },
        "违规风险": {"type": "noul", "instructions": "内容存在平台违规风险吗(如隐私、AI 冒充真人)?"},
        "是否需要标注AI": {"type": "noul", "instructions": "按平台惯例,这个视频需要显式标注'AI 生成'吗?"},
    },
)

# 场景 3:游戏/互动 —— 狼人杀式判断(演示'AI 玩游戏'的正确姿势)
ask(
    "游戏演示:狼人杀 AI 玩家(每轮 0.2 秒判断)",
    "第 2 天白天。玩家 C 的发言:\n"
    "'昨晚死亡的是玩家 A,我觉得是狼人刀了 A 想嫁祸给我,因为我昨天和 A 有过争论。"
    "我建议今天先投玩家 E,他从头到尾一句话没说,太可疑了。'\n"
    "背景:玩家 E 昨天全程未发言,玩家 C 昨天被 A 公开质疑过。",
    {
        "C像狼人吗": {"type": "noul", "instructions": "玩家 C 的发言像狼人在带节奏吗?"},
        "E像狼人吗": {"type": "noul", "instructions": "玩家 E 的不发言更像狼人装死吗?"},
        "建议投票": {
            "type": "choice",
            "instructions": "作为好人 AI,这轮该投谁?",
            "criteria": {"投C": "C 的发言有狼味", "投E": "E 装死不说话", "弃票": "信息不足", "再听一轮": "这轮先不投"},
        },
    },
)
