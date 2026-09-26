#!/usr/bin/env python3
"""测 BigModel 标准 API 各文本模型的流式吐字速度。key 从 provider_config.json 读取，不打印。"""
import json, time, urllib.request, sys

CFG = "/Users/jacksun/.zcode/v2/provider_config.json"
URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

cfg = json.load(open(CFG))
key = None
for rule in cfg["config"]["providerConfigRules"]["providerRules"]:
    if rule.get("providerId") == "bigmodel-standard-api":
        key = rule["config"]["access"]["apiKey"]
if not key:
    sys.exit("没找到 key")

MODELS = [
    "GLM-5.3", "GLM-5.3-Flash", "glm-5.3-flashx",
    "GLM-5.1", "GLM-5.1-Highspeed",
    "GLM-5", "GLM-5-Turbo",
    "GLM-4.7", "GLM-4.7-FlashX", "GLM-4.7-Flash",
    "GLM-4.6", "GLM-4.5-Air", "GLM-4.5",
    "GLM-4-FlashX-250414", "GLM-4-Flash-250414",
]

PROMPT = "请从1连续数到400，用顿号分隔，直接开始，不要任何前言、解释或总结。"

def bench(model, disable_thinking):
    body = {
        "model": model,
        "messages": [{"role": "user", "content": PROMPT}],
        "stream": True,
        "max_tokens": 2048,
        "stream_options": {"include_usage": True},
        "temperature": 0,
    }
    if disable_thinking:
        body["thinking"] = {"type": "disabled"}
    req = urllib.request.Request(
        URL,
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    t0 = time.perf_counter()
    ttft = None
    chunks = 0
    usage = None
    t_last = t0
    with urllib.request.urlopen(req, timeout=120) as resp:
        for raw in resp:
            line = raw.decode("utf-8").strip()
            if not line.startswith("data:"):
                continue
            payload = line[5:].strip()
            if payload == "[DONE]":
                break
            obj = json.loads(payload)
            choices = obj.get("choices") or []
            delta = choices[0].get("delta", {}) if choices else {}
            content = delta.get("content")
            reasoning = delta.get("reasoning_content")
            t_now = time.perf_counter()
            if (content or reasoning) and ttft is None:
                ttft = t_now - t0
            if content:
                chunks += 1
                t_last = t_now
            if obj.get("usage"):
                usage = obj["usage"]
                t_last = t_now
    total = time.perf_counter() - t0
    ct = usage["completion_tokens"] if usage else None
    # 纯吐字速度：首包之后到收尾
    decode_speed = ct / (t_last - t0 - ttft) if (ct and ttft and t_last > t0 + ttft) else None
    return {"ttft": ttft, "total": total, "completion_tokens": ct, "decode_speed": decode_speed, "chunks": chunks}

results = []
for m in MODELS:
    note = ""
    try:
        try:
            r = bench(m, True)
        except urllib.error.HTTPError as e:
            err = e.read().decode("utf-8", "ignore")[:200]
            if disable_thinking_ok := ("thinking" in err):
                r = bench(m, False)
                note = "不支持thinking参数，已带默认模式重测"
            else:
                r = None
                note = f"HTTP {e.code}: {err}"
    except Exception as e:
        r = None
        note = f"{type(e).__name__}: {str(e)[:150]}"
    if r:
        ds = f"{r['decode_speed']:.1f}" if r["decode_speed"] else "?"
        tt = f"{r['ttft']*1000:.0f}" if r["ttft"] else "?"
        ct = r["completion_tokens"] if r["completion_tokens"] else "?"
        results.append((m, tt, ds, ct, f"{r['total']:.1f}s", note))
        print(f"{m:26s} 首字 {tt:>6}ms  吐字 {ds:>7} tok/s  输出 {ct:>5} tok  总耗时 {r['total']:.1f}s {note}", flush=True)
    else:
        results.append((m, None, None, None, None, note))
        print(f"{m:26s} 失败  {note}", flush=True)

print("\n=== 按吐字速度排名 ===")
ok = [x for x in results if x[2]]
for i, (m, tt, ds, ct, tot, note) in enumerate(sorted(ok, key=lambda x: -float(x[2])), 1):
    print(f"{i}. {m:26s} {ds} tok/s (首字 {tt}ms)")
