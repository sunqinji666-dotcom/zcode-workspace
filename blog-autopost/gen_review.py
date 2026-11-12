#!/usr/bin/env python3
"""生成审核版静态 HTML（给孙哥过目用）：自包含、放桌面"博客待审稿"文件夹。

用法: python3 gen_review.py <配置.json>
配置 JSON 结构（数组，每篇一个对象）:
  [{"src": "drafts/final-xxx.html", "title": "...", "seo_title": "...",
    "seo_desc": "...", "seo_kw": "...", "cover_note": "...",
    "out": "~/Desktop/博客待审稿/0N-xxx.html", "images": {"<cdn-url>": "本地文件名"}}]
"""
import re, json, sys, os, glob

HERE = os.path.dirname(os.path.abspath(__file__))
REVIEW_DIR = os.path.expanduser('~/Desktop/博客待审稿')

TMPL = '''<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<title>待审稿：{title}</title>
<style>
body{{max-width:720px;margin:0 auto 80px;padding:0 22px;font-family:-apple-system,"PingFang SC","Hiragino Sans GB",sans-serif;line-height:1.95;color:#1a1a1a;background:#fff;font-size:17px}}
img{{max-width:100%;border-radius:10px;display:block;margin:0 auto}}
figure{{margin:30px 0}}
blockquote{{border-left:3px solid #222;margin:28px 0;padding:6px 24px;color:#222;font-size:1.13em;font-weight:600;line-height:1.75}}
h2{{margin-top:2.3em;font-size:1.45em;line-height:1.5}}
p{{margin:1.15em 0}}
hr{{border:none;border-top:1px solid #eaeaea;margin:2.5em 0}}
.review-banner{{background:#fef2f2;border:1px solid #fecaca;border-radius:10px;padding:14px 20px;font-size:15px;color:#b91c1c;margin:28px 0 18px;font-weight:600}}
.publish-info{{background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:18px 22px;font-size:14px;color:#334155;margin-bottom:40px}}
.publish-info h3{{margin:0 0 10px;font-size:15px;color:#0f172a}}
.publish-info table{{border-collapse:collapse;width:100%}}
.publish-info td{{padding:5px 8px;vertical-align:top;border-bottom:1px solid #eef2f7;line-height:1.6}}
.publish-info td:first-child{{color:#64748b;white-space:nowrap;width:88px}}
.has-background{{background:#f5f5f5;border-radius:8px;padding:22px 26px;font-size:14px;color:#555;line-height:1.9}}
strong{{font-weight:700}}
.title-main{{font-size:2em;font-weight:800;line-height:1.4;margin:6px 0 4px}}
.meta-line{{color:#94a3b8;font-size:14px;margin-bottom:6px}}
</style></head><body>
<div class="review-banner">📋 待审稿 · 未发布 —— 孙哥审核通过后我再发布</div>
<div class="publish-info">
<h3>发布配置（请一并确认）</h3>
<table>
<tr><td>文章标题</td><td><b>{title}</b></td></tr>
<tr><td>SEO 标题</td><td>{seo_title}</td></tr>
<tr><td>SEO 描述</td><td>{seo_desc}</td></tr>
<tr><td>关键词</td><td>{seo_kw}</td></tr>
<tr><td>配图</td><td>{cover_note}</td></tr>
<tr><td>发布位置</td><td>www.jack-sun.com（WordPress，和现有文章同一位置、同样式）</td></tr>
</table>
</div>
<div class="title-main">{title}</div>
<div class="meta-line">Jack孙 · {date} · 图文</div>
{body}
</body></html>'''

def main():
    cfg_path = sys.argv[1]
    jobs = json.load(open(cfg_path, encoding='utf-8'))
    os.makedirs(REVIEW_DIR, exist_ok=True)
    for j in jobs:
        html = open(os.path.join(HERE, j['src']), encoding='utf-8').read()
        for url, local in j.get('images', {}).items():
            html = html.replace(url, local)
        clean = re.sub(r'<!--\s*/?wp:[^>]*-->', '', html)
        out = os.path.expanduser(j['out'])
        import datetime
        j.setdefault('date', datetime.date.today().strftime('%Y-%m-%d'))
        open(out, 'w', encoding='utf-8').write(TMPL.format(**{k: v for k, v in j.items() if k not in ('src', 'out', 'images')}, body=clean))
        rest = re.findall(r'\{\{[A-Z_]+\}\}', clean)
        imgs = re.findall(r'src="([^"]+)"', clean)
        print(f"✓ {os.path.basename(out)} | 占位符残留: {rest or '无'} | 图片: {imgs}")

if __name__ == '__main__':
    main()
