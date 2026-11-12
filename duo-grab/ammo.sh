#!/bin/bash
# iPhone Duo 开闸一键弹药脚本：抓购买页 → 存 HTML → 解析 SKU
# 开闸后运行: bash ammo.sh
set -e
DIR="/Users/jacksun/Documents/zcode/duo-grab"
cd "$DIR"
ego-browser nodejs <<'EOF'
const fs = await import("node:fs/promises");
const dir = "/Users/jacksun/Documents/zcode/duo-grab";
const task = await taskSpace(1);
const page = task.page("p1");
const urls = [
  "https://www.apple.com.cn/cn/shop/goto/buy_iphone/iphone_duo/select",
  "https://www.apple.com.cn/cn/shop/goto/buy_iphone/iphone_duo",
];
let saved = null;
for (const u of urls) {
  if (saved) break;
  for (let i = 0; i < 3; i++) {
    try {
      const r = await page.fetch(u, { timeout: 8000 });
      const body = typeof r.body === "string" ? r.body : "";
      const coming = body.includes("preorder_full_description") || body.includes("来得早");
      console.log(`${u.split("/").pop()} try${i+1} status=${r.status} len=${body.length} comingSoon=${coming}`);
      if (r.status === 200 && body.length > 5000 && !coming) {
        saved = dir + "/buy_" + Date.now() + ".html";
        await fs.writeFile(saved, body);
        break;
      }
    } catch (e) { console.log("ERR " + e.message); }
    await new Promise(s => setTimeout(s, 2000));
  }
}
if (!saved) { console.log("❌ 仍未开闸"); process.exit(0); }
console.log("✅ 已保存 " + saved);
// 直接在浏览器侧解析 SKU 数据（比正则更稳：苹果购买页有内嵌 JSON）
const parsed = await page.evaluate(() => {
  const html = document.documentElement.outerHTML;
  const parts = [...new Set([...html.matchAll(/\b([A-Z]{2,5}\d{2,4}[A-Z]{0,2})CH\/A\b/g)].map(m => m[0]))];
  const prices = [...new Set([...html.matchAll(/RMB\s?([\d,]{4,7})/g)].map(m => m[1]))];
  // 尝试定位内嵌选择数据
  const keys = ["productSelectionJSON", "productSelectionData", "dimensionCompatibility", "initData"];
  const found = keys.filter(k => html.includes(k));
  return { parts, prices, found, len: html.length };
});
console.log("SKU parts:", JSON.stringify(parsed.parts));
console.log("prices:", JSON.stringify(parsed.prices));
console.log("jsonKeys:", parsed.found.join(","), "len:", parsed.len);
await fs.writeFile(dir + "/parts.json", JSON.stringify(parsed, null, 2));
EOF
node parse_buy.mjs "$DIR"/buy_*.html 2>/dev/null || echo "(node 解析器补充结果见 .parsed.json)"
