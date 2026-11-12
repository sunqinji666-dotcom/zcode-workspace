"""素材判决复核(可卖清单版) —— Jev 判断:上市风险 / 价值分级 / 挂牌类目。

用法:  ./run.sh jev_asset_review.py <可卖素材清单.csv> [--limit 8]
"""

import csv
import json
import os
import sys
import urllib.request

API_URL = "https://openrouter.ai/api/alpha/decisions"
API_KEY = os.environ["OPENROUTER_API_KEY"]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        raise SystemExit(__doc__)
    src = os.path.expanduser(args[0])
    limit = 8
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])

    rows = []
    with open(src, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if row.get("描述"):
                rows.append(row)
            if len(rows) >= limit:
                break
    print(f"清单:{os.path.basename(src)} | 取 {len(rows)} 条判读\n")

    state, questions = [], {}
    for i, row in enumerate(rows, 1):
        key = f"a{i:02d}"
        state.append(f"[{key}] 分辨率 {row.get('分辨率','?')} 时长 {row.get('时长s','?')}s\n画面:{row['描述']}")
        questions[f"{key}_risk"] = {
            "type": "noul",
            "instructions": f"{key} 这条素材直接挂牌销售存在风险(可识别的人脸/车牌/私人场所/品牌 logo/敏感场景)。",
        }
        questions[f"{key}_value"] = {
            "type": "choice",
            "instructions": f"{key} 的商业价值分级",
            "criteria": {"通用素材": "随处可见,量大", "优质素材": "构图/内容较好,有竞争力", "稀缺素材": "少见画面,强卖点"},
        }
        questions[f"{key}_cat"] = {
            "type": "choice",
            "instructions": f"{key} 最适合挂牌的类目",
            "criteria": {"城市风光": "街道/建筑/车流", "自然风景": "山/海/天空", "人文生活": "人物/婚礼/日常", "商业空间": "宴会厅/商场/室内", "活动记录": "会议/演出/仪式"},
        }

    payload = {"model": "typesafe/jev-1.13", "state": "\n\n".join(state), "questions": questions}
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        r = json.loads(resp.read().decode("utf-8"))
    a = r["answers"]

    print(f"{'素材':<22}{'上市风险':<9}{'价值':<7}{'类目'}")
    print("-" * 58)
    for i, row in enumerate(rows, 1):
        key = f"a{i:02d}"
        name = os.path.basename(row["路径"])[:20]
        risk = a[f"{key}_risk"]["noul"]
        flag = f"{risk:.2f}" + (" ⚠" if risk >= 0.5 else "")
        print(f"{name:<22}{flag:<9}{a[f'{key}_value']['choice']:<7}{a[f'{key}_cat']['choice']}")

    print(f"\n成本: ${r['usage']['cost']:.6f} | 一次调用 {len(questions)} 个判断")
    print(f"提示:全量 15815 条按此单价约 ${15815/len(rows)*r['usage']['cost']:.2f}")


if __name__ == "__main__":
    main()
