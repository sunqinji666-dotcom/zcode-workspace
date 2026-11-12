# 博客每日自动发文 PLAYBOOK

孙哥（孙秦吉 / Jack孙 / jacksun，桂林摄影师兼导演，光感影视创始人）的博客
**www.jack-sun.com**（WordPress 7.1 + zaxu/zaxu-child 主题）每日自动发文流程。

本文件是每日定时任务的自包含操作手册。任何新会话执行发文任务时，先读本文件，
再按"总流程"逐步完成。首次建立：2026-10-06。

---

## 一、总流程（每日任务按此执行）

1. **采集**：运行 `python3 /Users/jacksun/Documents/zcode/blog-autopost/collect_day.py`
   （默认扫过去 24 小时，可传天数参数），输出 `material-YYYYMMDD.md` 素材文件
2. **选题**：从素材里挑 1 个最有故事性的主题（优先：有具体数字、有转折、有人味的事）；
   查 `published-index.md` 避免与已发文章重复
3. **写作**：中文、第一人称（孙哥口吻）、1500–2800 字，排版规范见第三节。
   **写作前必读 `voice-guide.md`（孙哥口吻指南），文章必须符合他的口语习惯——
   这是他在 2026-10-06 明确提出的要求，针对全部文章**
4. **配图**：小云雀生成 1–2 张，上传到 WP 媒体库（第四节）
5. **审稿（硬性规则，不得跳过）**：把成稿（标题 + 全文 + 配图）整理成预览给孙哥过目，
   **必须等他明确确认后才能进入发布**。2026-10-06 他在我未经他过目直接发布时紧急叫停：
   "发布前我要看呀！"——他要的"直接发"指的是"他确认后不再问细节、一步发完"，
   不是"跳过他的审稿"。预览做法：生成 HTML 到 `~/Desktop/博客待审稿/` 请他看
6. **发布**：SSH 到 `jacksun-tencent`，wp-cli 发布 + SEO meta（第五节）
7. **清缓存 + 验证**（第六节），回报结果；更新 `published-index.md`

素材不够成篇时：写一篇轻量的"当日随笔"（600–1000 字），或有意思的短观察，
不要硬凑。当天内容全部敏感（见红线）时：跳过发布，在 published-index.md 记一笔原因。

## 二、内容红线（每篇必查，宁缺毋滥）

- **绝不出现**：任何密码 / 密钥 / token / 凭证；合同金额明细；未公开的客户信息；
  私人对话原文；家庭隐私；他人隐私（如健康信息）
- **不写**：翻墙 / 代理 / VPN / 机场相关内容（主域有 SEO 降权风险）。
  当天素材主要是这类内容时，换主题
- **客户名**：官网已公开的可用（桂林银行、微笑堂、优利特、广西交投等，见
  `guanggan-authoritative-facts` 记忆）；没把握的一律不写
- **写"我"的时候**：只写工作与创作相关的自我观察，不写情绪低谷的细节
- 拿不准的细节宁可不写。公开的文章要经得起客户和熟人看到

## 三、写作与排版规范（孙哥 2026-10-06 明确要求）

**文风**：第一人称，短段落、一句一段、口语化、真诚。像深夜写给朋友看的东西。
不用"首先/其次/综上"，不用书面腔，不堆形容词——用具体细节说话
（时间、金额、文件名、数字比形容词有力）。

**结构**：
- 开头 1–2 句钩子（口语化，直接进事）
- 正文 3–5 个 `h2` 小节，每节一个意思
- 结尾回扣开头，落在一个具体的感受或下一步上
- 每篇 2–3 个 pullquote 金句（把最有力的一句单独拎出来）

**HTML 用 Gutenberg 块**（与现有文章一致，示例见 `templates/post-template.html`）：
- 段落 `<p>` 用 `<!-- wp:paragraph -->` 包裹；小节标题用 `<!-- wp:heading -->` + `<h2>`
- 重点句加粗 `<strong>`（每节 1–2 处，别滥用）
- 金句用 `<!-- wp:pullquote -->`；清单用 `<!-- wp:list -->`；图片用 `<!-- wp:image -->`
- 结尾固定作者签名块（复制 `templates/author-signature.html`）
- 封面图放文章最顶部

**标题**：口语、白描、有钩子。参考已发：《凌晨四点，桂林》《我最近其实不是在折腾电脑》
《AI不是靠想象听懂你的》《两百块的 MV》。不用冒号副标题式标题。

## 四、配图（小云雀 xyq-skill）

1. 确认登录：`pippit-tool-cli status`（要 `"logged_in":true`；失效则按
   `~/.zcode/skills/xyq-skill/commands/auth.md` 让孙哥登录）
2. 查模型/比例：`pippit-tool-cli model describe "智能图片V2.5 Pro" --type image`
   （默认模型"智能图片V2.5 Pro"；比例用 16:9 的数字枚举，先查 option_labels 确认）
3. 提交（提示词写中文电影感写实摄影风，延续 6 月文章配图风格——深夜、真实、电影感）：
   `pippit-tool-cli generate-image --prompt "..." --model "智能图片V2.5 Pro" --ratio N --source ""`
4. 查询下载：按 `~/.zcode/skills/xyq-skill/workflows/async-delivery.md`
   （`query-result --thread-id ... --run-id ...` 轮询到完成，下载到本地）
5. 上传到 WP：
   ```bash
   scp 图片 jacksun-tencent:/tmp/
   ssh jacksun-tencent 'cd /www/wwwroot/www.jack-sun.com/wordpress && \
     sudo -u www wp media import /tmp/图片 --title="中文标题" --alt="中文alt" --porcelain'
   ```
   记录返回的 attachment ID；用 `sudo -u www wp post get ATTACH_ID --field=guid`
   取图片真实 URL（应显示 cloud-cdn.jack-sun.com 域名）
6. 封面：发布后 `sudo -u www wp post meta update POST_ID _thumbnail_id ATTACH_ID`；
   正文插入 `wp:image` 块（用真实 URL）
7. 命名规范：`article-<英文slug>-N.png`（延续 6 月：article-4am-guilin-1.png）

## 五、发布（服务器 jacksun-tencent）

```bash
# 0. 本地写好的文章 HTML 先传到服务器（注意 UTF-8、权限）
scp post-xxx.html jacksun-tencent:/tmp/
ssh jacksun-tencent 'sudo chmod 644 /tmp/post-xxx.html'

# 1. 创建文章（拿到 ID）
ssh jacksun-tencent 'cd /www/wwwroot/www.jack-sun.com/wordpress && \
  ID=$(sudo -u www wp post create --post_type=post --post_status=publish \
    --post_title="标题" --porcelain) && echo "ID=$ID"'

# 2. 写入内容（HTML 文件路径）
ssh jacksun-tencent 'cd /www/wwwroot/www.jack-sun.com/wordpress && \
  sudo -u www wp post update $ID /tmp/post-xxx.html'

# 3. SEO meta（zaxu-child 主题读取这三个键）
sudo -u www wp post meta update $ID zaxu_seo_title "SEO标题（≤32字，含关键词）"
sudo -u www wp post meta update $ID zaxu_seo_description "SEO描述（80–120字，自然含关键词）"
sudo -u www wp post meta update $ID zaxu_seo_keywords "孙秦吉, Jack孙, jacksun, <本文关键词>"

# 4. 封面图（传图后）
sudo -u www wp post meta update $ID _thumbnail_id ATTACH_ID

# 5. 清全页缓存（nginx FastCGI 缓存）
sudo rm -rf /www/server/fastcgi_cache/*
```

**要点**：wp 命令一律 `sudo -u www`（网站运行用户），不要 `--allow-root`；
固定链接是 `/%post_id%.html`，文章 URL = `https://www.jack-sun.com/<ID>.html`；
作者留空（与现有文章一致，post_author=0）；分类挂"未分类"（term_id 1，与 6 月随笔一致）。

## 六、验证（发布后必做）

```bash
curl -s -o /tmp/chk.html -w "%{http_code}" -m 15 "https://www.jack-sun.com/<ID>.html"
# 检查：HTTP 200、<title> 正确、h2 数量、description meta、封面图 URL（cloud-cdn）
grep -o "<title>[^<]*" /tmp/chk.html | head -1
grep -o 'name="description" content="[^"]*"' /tmp/chk.html | head -c 300
```

## 七、SEO 配套（每篇必做）

- SEO 标题自然含关键词（如"AI 视频""剪辑""桂林"等，按当日主题定）
- 描述（zaxu_seo_description）写成人话，80–120 字，自然带关键词
- 关键词字段：固定带"孙秦吉, Jack孙, jacksun"，其余按主题 3–5 个
- 内链 1–2 条：链到已发文章或服务页（清单见 `published-index.md`）
- 图片 alt 用中文描述

## 八、重要机制备忘

- 全页缓存：`/www/server/fastcgi_cache/*`，匿名 GET 缓存 10 分钟；发布后必须手动清
- 改了 .php 才需要 `reload php-fpm-83`（opcache）；只发文章不用
- 宝塔 nginx 有两套实例，语法检查用 `/www/server/nginx/sbin/nginx -t`（一般用不上）
- 媒体走七牛 CDN（cloud-cdn.jack-sun.com），wp media import 后 URL 自动是 CDN 域
- 服务器 SSH：`ssh jacksun-tencent`（密钥已配）；本机 wp 不可用，一切 wp 操作在服务器
- 每日任务时间：每天 23:00（CronCreate 自动任务）；若当天已发文章（手动或补发），
  任务开头先 `wp post list --post_status=publish --fields=ID,post_date | tail` 检查，
  最近 24h 内已发过就跳过本次

## 九、已发文章索引

见 `published-index.md`（每发一篇加一行：日期 / ID / 标题 / URL / 主题标签）
