"""描述审查员 —— 用 Jev 检查「AI 画面描述」与「文件路径线索」的一致性,挑出可疑描述。

背景:素材判读时 AI 会对部分画面误读/串上下文(48 格小图同屏看),
本工具把「描述与目录名/文件名/时长矛盾」或「疑似没看清」的挑出来,
供人工或重新识图复核。

用法:
    ./run.sh jev_desc_audit.py <清单.csv> [--batch 150] [--limit N] [--start N]
    ./run.sh jev_desc_audit.py ~/Documents/素材判决_两盘/可卖素材清单.csv --limit 150

输出:
    同目录 <清单名>_审查结果.csv(全部条目 + 可信度/需复核/是否可疑,支持续跑)
"""

import csv
import json
import os
import sys
import urllib.request

API_URL = "https://openrouter.ai/api/alpha/decisions"


def load_api_key():
    key = os.environ.get("OPENROUTER_API_KEY")
    if key:
        return key
    env_path = os.path.expanduser("~/Documents/zcode/jev/.env")
    if os.path.exists(env_path):
        for line in open(env_path, encoding="utf-8"):
            line = line.strip()
            if line.startswith("OPENROUTER_API_KEY="):
                return line.split("=", 1)[1].strip()
    raise SystemExit("找不到 OPENROUTER_API_KEY")


def strip_vol(path):
    """去掉 /Volumes/<卷>/ 前缀,返回 (卷名, 剩余路径)"""
    parts = path.split("/")
    if len(parts) > 3 and parts[1] == "Volumes":
        return parts[2], "/".join(parts[3:])
    return "?", path


def audit_batch(items):
    """items: [(path, desc, dur)] → [(trust, recheck)]"""
    lines = []
    for i, (path, desc, dur) in enumerate(items, 1):
        vol, rest = strip_vol(path)
        d = os.path.dirname(rest)
        f = os.path.basename(rest)
        lines.append(f"[r{i:03d}] 盘:{vol} 目录:{d} 文件:{f} 时长:{dur}s\n描述:{desc}")
    state = "\n".join(lines)

    questions = {}
    for i in range(1, len(items) + 1):
        questions[f"r{i:03d}_t"] = {
            "type": "score",
            "instructions": f"r{i:03d} 这条描述与文件路径线索(目录名、文件名、时长)一致吗?描述可信度如何?",
            "criteria": ["明显矛盾/疑似编造", "存疑", "一般", "较可信", "高度可信"],
        }
        questions[f"r{i:03d}_c"] = {
            "type": "noul",
            "instructions": f"r{i:03d} 这条描述需要重新识图或人工复核。",
        }

    payload = {"model": "typesafe/jev-1.13", "state": state, "questions": questions}
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": f"Bearer {load_api_key()}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        r = json.loads(resp.read().decode("utf-8"))
    a = r["answers"]
    out = []
    for i in range(1, len(items) + 1):
        out.append((a[f"r{i:03d}_t"]["score"], a[f"r{i:03d}_c"]["noul"]))
    return out, r["usage"]["cost"]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        raise SystemExit(__doc__)
    src = os.path.expanduser(args[0])
    batch_size = 150
    if "--batch" in sys.argv:
        batch_size = int(sys.argv[sys.argv.index("--batch") + 1])
    limit = None
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])
    start = 0
    if "--start" in sys.argv:
        start = int(sys.argv[sys.argv.index("--start") + 1])

    rows = list(csv.DictReader(open(src, encoding="utf-8-sig")))
    dur_col = "时长s" if "时长s" in rows[0] else None
    print(f"清单:{os.path.basename(src)} 共 {len(rows)} 条")

    out_path = src.replace(".csv", "") + "_审查结果.csv"
    done = {}
    if os.path.exists(out_path):
        for r in csv.DictReader(open(out_path, encoding="utf-8-sig")):
            done[r["路径"]] = r
        print(f"续跑:已有 {len(done)} 条审查结果,跳过")

    todo = rows[start: (start + limit) if limit else None]
    todo = [r for r in todo if r["路径"] not in done]
    print(f"本批待审:{len(todo)} 条\n")

    # 结果文件表头
    if not os.path.exists(out_path):
        with open(out_path, "w", encoding="utf-8-sig", newline="") as f:
            csv.writer(f).writerow(["分级", "路径", "描述", "可信度", "需复核", "是否可疑"])

    total_cost = 0.0
    suspicious_total = 0
    for b in range(0, len(todo), batch_size):
        chunk = todo[b:b + batch_size]
        items = [(r["路径"], r["描述"], r.get(dur_col, "?") if dur_col else "?") for r in chunk]
        try:
            results, cost = audit_batch(items)
        except Exception as e:
            print(f"  批次 {b//batch_size+1} 失败: {str(e)[:100]}")
            continue
        total_cost += cost
        with open(out_path, "a", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f)
            for r, (trust, recheck) in zip(chunk, results):
                flag = "可疑" if (trust <= 1.0 or recheck >= 0.6) else ""
                if flag:
                    suspicious_total += 1
                w.writerow([r["分级"], r["路径"], r["描述"], f"{trust:.2f}", f"{recheck:.2f}", flag])
        n_sus = sum(1 for t, c in results if t <= 1.0 or c >= 0.6)
        done_n = min(b + batch_size, len(todo))
        print(f"  进度 {done_n}/{len(todo)} | 本批可疑 {n_sus} | 累计可疑 {suspicious_total} | 累计成本 ${total_cost:.4f}")

    print(f"\n完成。可疑 {suspicious_total} 条,总成本 ${total_cost:.4f}")
    print(f"结果:{out_path}")


if __name__ == "__main__":
    main()
