#!/usr/bin/env python3
"""组装文章 HTML：把图片 URL/ID 和签名块替换进文章模板。

用法:
  python3 assemble.py in.html out.html \
    --cover-url URL --cover-id ID --cover-alt "alt文字" \
    [--inline-url URL --inline-id ID --inline-alt "alt文字"]

占位符: {{IMG_COVER}} {{IMG_COVER_ID}} {{ALT_COVER}} {{IMG_INLINE}} {{IMG_INLINE_ID}} {{ALT_INLINE}} {{SIGNATURE}}
无 inline 参数时 {{IMG_INLINE}} 相关占位符被移除（不插内文图）。
"""
import sys, os, argparse

HERE = os.path.dirname(os.path.abspath(__file__))

IMG_TMPL = ('<!-- wp:image {{json}} --><figure class="wp-block-image size-large">'
            '<img src="{{url}}" alt="{{alt}}"{{cls}} /></figure><!-- /wp:image -->')

def img_block(url, aid, alt):
    if aid:
        json = '{"id":%s,"sizeSlug":"large","linkDestination":"none"}' % aid
        cls = ' class="wp-image-%s"' % aid
    else:
        json = '{"sizeSlug":"large","linkDestination":"none"}'
        cls = ''
    return IMG_TMPL.replace('{{json}}', json).replace('{{url}}', url).replace('{{alt}}', alt).replace('{{cls}}', cls)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('infile'); p.add_argument('outfile')
    p.add_argument('--cover-url', required=True)
    p.add_argument('--cover-id', default='')
    p.add_argument('--cover-alt', default='')
    p.add_argument('--inline-url', default='')
    p.add_argument('--inline-id', default='')
    p.add_argument('--inline-alt', default='')
    args = p.parse_args()

    html = open(args.infile, encoding='utf-8').read()

    # 封面图（整块替换）
    html = html.replace('{{IMG_COVER_BLOCK}}', img_block(args.cover_url, args.cover_id, args.cover_alt))
    html = html.replace('{{ALT_COVER}}', args.cover_alt)

    # 内文图
    if args.inline_url:
        html = html.replace('{{IMG_INLINE}}', img_block(args.inline_url, args.inline_id, args.inline_alt))
    else:
        html = html.replace('{{IMG_INLINE}}', '')

    # 签名块
    sig = open(os.path.join(HERE, 'templates', 'author-signature.html'), encoding='utf-8').read().strip()
    html = html.replace('{{SIGNATURE}}', sig)

    # 残留占位符检查
    import re
    left = re.findall(r'\{\{[A-Z_]+\}\}', html)
    if left:
        print('警告：仍有未替换占位符:', set(left), file=sys.stderr)

    open(args.outfile, 'w', encoding='utf-8').write(html)
    # 统计
    text = re.sub(r'<!--.*?-->', '', html)
    text = re.sub(r'<[^>]+>', '', text)
    print(f'已生成 {args.outfile}，可见文本 {len(text.replace(" ", "").replace(chr(10), ""))} 字')

if __name__ == '__main__':
    main()
