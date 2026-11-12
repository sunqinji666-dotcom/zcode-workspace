// 解析开闸后的 iPhone Duo 购买页 HTML，提取全部 SKU 深链与价格
// 用法: node parse_buy.mjs <html文件路径>
import { readFileSync, writeFileSync } from "node:fs";

const file = process.argv[2];
const html = readFileSync(file, "utf8");

// 1) part number 抓取：国行格式如 MTQ83CH/A（字母x4+数字+CH/A）
const partRe = /\b([A-Z]{2,5}\d{2,4}[A-Z]{0,2})CH\/A\b/g;
const parts = [...new Set([...html.matchAll(partRe)].map(m => m[0]))];

// 2) 价格抓取：RMB 15,999 或 ¥15,999 或 "15999"
const priceRe = /RMB\s?([\d,]{4,7})|¥\s?([\d,]{4,7})/g;
const prices = [...new Set([...html.matchAll(priceRe)].map(m => (m[1] || m[2])))];

// 3) 内嵌 JSON 数据块（苹果购买页通常有 productSelectionJSON / init data）
const jsonHints = [];
for (const kw of ["productSelectionJSON", "productSelectionData", "initData", "buyflow", "dimensionCompatibility", "carrierPolicyJson"]) {
  const i = html.indexOf(kw);
  if (i >= 0) jsonHints.push({ kw, around: html.slice(i - 80, i + 200).replace(/\s+/g, " ") });
}

// 4) 颜色/容量关键词上下文，辅助人工核对
const ctx = {};
for (const kw of ["夜空色", "星光白色", "256GB", "512GB", "1TB", "2TB"]) {
  const i = html.indexOf(kw);
  if (i >= 0) ctx[kw] = html.slice(Math.max(0, i - 150), i + 150).replace(/\s+/g, " ");
}

const result = {
  file,
  htmlLen: html.length,
  parts,
  partsCount: parts.length,
  prices,
  jsonHints,
  ctx,
};

// 5) 生成深链
result.deeplinks = parts.map(p => ({
  part: p,
  url: `https://www.apple.com.cn/cn/shop/buy_iphone/iphone-duo/${p.toLowerCase()}`,
}));

writeFileSync(file.replace(/\.html$/, ".parsed.json"), JSON.stringify(result, null, 2));
console.log(JSON.stringify({ partsCount: parts.length, parts, prices, deeplinkCount: result.deeplinks.length }, null, 2));
