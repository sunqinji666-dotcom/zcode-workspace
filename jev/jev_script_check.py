"""稿子交付前质检 —— 用 Jev 一次性检查:品牌风险句、钩子强度、结构完整度。

跑法:  ./run.sh jev_script_check.py <稿子文件> [--context "vivo 发布会开场影片旁白"]
"""

import json
import os
import re
import sys
import urllib.request

API_URL = "https://openrouter.ai/api/alpha/decisions"
API_KEY = os.environ["OPENROUTER_API_KEY"]


def split_sentences(text):
    # 去掉 markdown 标题/引用行,按中文句末标点切句
    lines = [l for l in text.splitlines() if not l.strip().startswith(("#", ">", "---"))]
    body = "\n".join(lines)
    parts = re.split(r"(?<=[。！？!?；;])", body)
    sents = []
    for p in parts:
        p = p.strip().strip("\n")
        if not p:
            continue
        # 太短的与上句合并
        if sents and len(p) < 8:
            sents[-1] += p
        else:
            sents.append(p)
    return sents


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        raise SystemExit(__doc__)
    src = os.path.expanduser(args[0])
    context = "一条品牌宣传影片的旁白文案"
    if "--context" in sys.argv:
        context = sys.argv[sys.argv.index("--context") + 1]

    text = open(src, encoding="utf-8").read()
    sents = split_sentences(text)
    print(f"稿子:{os.path.basename(src)} | {len(sents)} 句 | 背景:{context}")
    print("发给 Jev 质检中…\n")

    state = f"背景:{context}\n\n文案全文:\n" + "\n".join(f"{i+1}. {s}" for i, s in enumerate(sents))

    questions = {
        "hook_strength": {
            "type": "score",
            "instructions": "开头三句抓住观众/建立悬念的能力",
            "criteria": ["平淡", "一般", "有吸引力", "很强", "极强"],
        },
        "structure": {
            "type": "score",
            "instructions": "整体结构的完整度(起承转合是否齐全)",
            "criteria": ["散乱", "偏散", "完整", "很完整", "教科书级"],
        },
        "tone_consistency": {
            "type": "score",
            "instructions": "全文调性的统一程度",
            "criteria": ["前后矛盾", "有跳脱", "基本统一", "统一", "浑然一体"],
        },
        "brand_risk_overall": {
            "type": "noul",
            "instructions": f"作为{context},全文存在需要交付方再审慎确认的表达吗?",
        },
    }
    # 逐句风险扫描
    for i in range(len(sents)):
        questions[f"risk_{i+1:03d}"] = {
            "type": "noul",
            "instructions": f"第 {i+1} 句作为{context}的正式台词,存在品牌风险、误读空间或不宜官方场合的表达。",
        }

    payload = {"model": "typesafe/jev-1.13", "state": state, "questions": questions}
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        r = json.loads(resp.read().decode("utf-8"))
    a = r["answers"]

    print("—— 总览 ——")
    print(f"  开头钩子 : {a['hook_strength']['score']:.1f}/4 (把握 {a['hook_strength']['confidence']:.2f})")
    print(f"  结构完整 : {a['structure']['score']:.1f}/4")
    print(f"  调性统一 : {a['tone_consistency']['score']:.1f}/4")
    print(f"  整体风险 : {a['brand_risk_overall']['noul']:.2f} (0~1)")

    risks = []
    for i in range(len(sents)):
        v = a[f"risk_{i+1:03d}"]["noul"]
        if v >= 0.4:
            risks.append((v, i + 1, sents[i]))
    risks.sort(reverse=True)
    print(f"\n—— 需再审慎确认的句子({len(risks)} 条,按风险降序)——")
    for v, no, s in risks:
        print(f"  [{v:.2f}] #{no}: {s[:60]}")
    if not risks:
        print("  (无)")

    print(f"\n成本: ${r['usage']['cost']:.6f} | 一次调用 {len(questions)} 个判断")


if __name__ == "__main__":
    main()
