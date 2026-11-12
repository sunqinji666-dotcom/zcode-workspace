#!/usr/bin/env python3
"""博客素材采集脚本：扫描过去 N 天的 AI 对话，输出 markdown 素材文件给写文章用。

用法: python3 collect_day.py [天数]   # 默认 1（过去 24 小时）
输出: 本目录 material-YYYYMMDD.md

来源:
  1. Claude Code: ~/.claude/projects/*/*.jsonl
  2. Codex:       ~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl
  3. ZCode:       ~/.zcode/cli/db/db.sqlite (message + part 表)
"""
import json, glob, os, sqlite3, sys, datetime, re

HERE = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser('~')
DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 1
NOW = datetime.datetime.now()
SINCE = NOW - datetime.timedelta(days=DAYS)
SINCE_TS = SINCE.timestamp()

entries = []  # (datetime, source, text)

SKIP_MARKERS = ('system-reminder', '<command-name>', 'This session is being continued',
                'Caveat:', 'TODO', 'todo_reminder', 'prior /loop wakeups', '已交付待命',
                '[/loop', 'loop is healthy')
_seen = set()

def clean_text(t, limit=500):
    if not t: return ''
    t = re.sub(r'<system-reminder>.*?</system-reminder>', '', t, flags=re.S)
    t = re.sub(r'<[^>]{0,80}>', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t[:limit]

def wanted(text):
    if not text or len(text) < 4: return False
    for m in SKIP_MARKERS:
        if m in text[:300]: return False
    if text.startswith('[Image'): return False
    key = text[:120]
    if key in _seen: return False
    _seen.add(key)
    return True

# ---------- 1. Claude Code ----------
for path in glob.glob(f'{HOME}/.claude/projects/*/*.jsonl'):
    try:
        if os.path.getmtime(path) < SINCE_TS: continue
    except OSError:
        continue
    try:
        with open(path, encoding='utf-8', errors='ignore') as f:
            for line in f:
                if '"type":"user"' not in line and '"type": "user"' not in line: continue
                try: obj = json.loads(line)
                except Exception: continue
                if obj.get('type') != 'user': continue
                msg = obj.get('message', {})
                content = msg.get('content', '')
                text = ''
                if isinstance(content, str): text = content
                elif isinstance(content, list):
                    for c in content:
                        if isinstance(c, dict) and c.get('type') == 'text':
                            text += c.get('text', '')
                text = clean_text(text)
                if not wanted(text): continue
                ts = obj.get('timestamp', '')
                try:
                    dt = datetime.datetime.fromisoformat(ts.replace('Z', '+00:00')).astimezone().replace(tzinfo=None)
                except Exception:
                    dt = datetime.datetime.fromtimestamp(os.path.getmtime(path))
                if dt < SINCE: continue
                entries.append((dt, 'ClaudeCode', text))
    except Exception:
        continue

# ---------- 2. Codex ----------
d = SINCE.date()
while d <= NOW.date():
    for path in glob.glob(f'{HOME}/.codex/sessions/{d.year}/{d.month:02d}/{d.day:02d}/rollout-*.jsonl'):
        try:
            with open(path, encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if '"role":"user"' not in line: continue
                    try: obj = json.loads(line)
                    except Exception: continue
                    payload = obj.get('payload', {}) or {}
                    if payload.get('role') != 'user': continue
                    content = payload.get('content', [])
                    text = ''
                    if isinstance(content, list):
                        for c in content:
                            if isinstance(c, dict) and c.get('type') in ('input_text', 'text'):
                                text += c.get('text', '')
                    elif isinstance(content, str):
                        text = content
                    text = clean_text(text)
                    if not wanted(text): continue
                    ts = obj.get('timestamp', '')
                    try:
                        dt = datetime.datetime.fromisoformat(ts.replace('Z', '+00:00')).astimezone().replace(tzinfo=None)
                    except Exception:
                        dt = datetime.datetime.now()
                    if dt < SINCE: continue
                    entries.append((dt, 'Codex', text))
        except Exception:
            continue
    d += datetime.timedelta(days=1)

# ---------- 3. ZCode ----------
try:
    conn = sqlite3.connect(f'{HOME}/.zcode/cli/db/db.sqlite')
    cur = conn.execute(
        'SELECT m.time_created, p.data FROM message m JOIN part p ON p.message_id = m.id '
        'WHERE m.data LIKE \'%"role":"user"%\' AND m.time_created > ?',
        (int(SINCE_TS * 1000),))
    for tms, pdata in cur:
        try: p = json.loads(pdata)
        except Exception: continue
        if p.get('type') != 'text': continue
        if p.get('synthetic'): continue
        text = clean_text(p.get('text', ''))
        if not wanted(text): continue
        dt = datetime.datetime.fromtimestamp(tms / 1000)
        entries.append((dt, 'ZCode', text))
    conn.close()
except Exception:
    pass

# ---------- 输出 ----------
entries.sort(key=lambda e: e[0])
out = f'{HERE}/material-{NOW.strftime("%Y%m%d")}.md'
with open(out, 'w', encoding='utf-8') as f:
    f.write(f'# 素材 {NOW.strftime("%Y-%m-%d")}（过去 {DAYS} 天，共 {len(entries)} 条）\n\n')
    cur_day = None
    for dt, src, text in entries:
        if dt.date() != cur_day:
            cur_day = dt.date()
            f.write(f'\n## {cur_day}\n\n')
        f.write(f'- **{dt.strftime("%H:%M")} [{src}]** {text}\n')

print(f'{len(entries)} 条 → {out}')
