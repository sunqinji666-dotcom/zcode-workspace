#!/bin/bash
# 发布文章《两百块的 MV》2026-10-06
set -e
cd /www/wwwroot/www.jack-sun.com/wordpress

ID=$(sudo -u www wp post create --post_type=post --post_status=publish \
  --post_title="两百块的 MV" --porcelain)
echo "文章ID=$ID"

sudo -u www wp post update "$ID" /tmp/final-200mv.html

# SEO meta（zaxu-child 主题读取）
sudo -u www wp post meta update "$ID" zaxu_seo_title "两百块的 MV｜我用 AI 做视频踩过的坑"
SEODESC="花两百块让 AI 做一支 MV，结果完全不能看。我把爆款参考片拆到源代码，才发现差距不在 AI，在流程。一个导演用 AI 做视频的真实记录。"
sudo -u www wp post meta update "$ID" zaxu_seo_description "$SEODESC"
sudo -u www wp post meta update "$ID" zaxu_seo_desc "$SEODESC"
sudo -u www wp post meta update "$ID" zaxu_seo_keywords "孙秦吉, Jack孙, jacksun, AI视频, AI做MV, 音乐MV制作, 桂林导演"

# 封面图
sudo -u www wp post meta update "$ID" _thumbnail_id 2269

# 清缓存
sudo rm -rf /www/server/fastcgi_cache/*
sleep 1

URL=$(sudo -u www wp post url "$ID")
echo "URL=$URL"
echo "=== 验证 ==="
curl -s -m 15 "$URL" -o /tmp/chk200mv.html
echo "HTTP状态: $(curl -s -o /dev/null -w '%{http_code}' -m 15 "$URL")"
grep -o "<title>[^<]*" /tmp/chk200mv.html | head -1
echo "h2 数量: $(grep -o '<h2' /tmp/chk200mv.html | wc -l | tr -d ' ')"
grep -o 'name="description" content="[^"]*"' /tmp/chk200mv.html | head -c 200
echo
echo "封面图: $(grep -o 'd4f5a4fe043b49ac7d3646ec4ec8bdc3' /tmp/chk200mv.html | head -1)"
echo "正文图: $(grep -o '4266b9c31f0cbb841f192c8bc9df11bb' /tmp/chk200mv.html | head -1)"
echo "已发布 HTML 长度: $(sudo -u www wp post get "$ID" --field=post_content | wc -c)"
