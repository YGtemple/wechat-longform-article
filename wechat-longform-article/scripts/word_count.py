#!/usr/bin/env python3
"""
微信公众号长文字数统计。
统计 HTML 文件正文（去除标签、注释、script/style）的"字数"：
  中文字符数 + 英文单词数（与 Word/WPS 中文字数统计口径一致）。
用法：
  python3 word_count.py <article.html> [--min 20000] [--max 45000]
退出码：0 = 达标；1 = 不达标；2 = 文件读取错误。
"""
import re
import sys
import argparse


def strip_html(html: str) -> str:
    # 去除注释
    html = re.sub(r"<!--.*?-->", "", html, flags=re.DOTALL)
    # 去除 script / style 块
    html = re.sub(r"<(script|style)\b.*?</\1>", "", html, flags=re.DOTALL | re.IGNORECASE)
    # 把 <br>、块级标签换成换行，保留段落边界
    html = re.sub(r"<br\s*/?>", "\n", html, flags=re.IGNORECASE)
    html = re.sub(r"</(p|div|section|h[1-6]|li|blockquote|tr)>", "\n", html, flags=re.IGNORECASE)
    # 去掉所有标签
    text = re.sub(r"<[^>]+>", "", html)
    # 反转义常见 HTML 实体
    for entity, ch in [("&nbsp;", " "), ("&amp;", "&"), ("&lt;", "<"),
                       ("&gt;", ">"), ("&quot;", '"'), ("&#39;", "'"),
                       ("&ldquo;", "\u201c"), ("&rdquo;", "\u201d"),
                       ("&mdash;", "—"), ("&hellip;", "…")]:
        text = text.replace(entity, ch)
    text = re.sub(r"&#\d+;", "", text)
    text = re.sub(r"&[a-zA-Z]+;", "", text)
    return text


def count_words(text: str):
    # 中文字符（CJK 统一表意文字 + 扩展A + 常用中文标点不计入）
    cjk = re.findall(r"[\u4e00-\u9fff\u3400-\u4dbf]", text)
    # 英文单词
    eng = re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", text)
    # 数字串（按词计）
    num = re.findall(r"\d+(?:\.\d+)?", text)
    return len(cjk), len(eng), len(num)


def main():
    ap = argparse.ArgumentParser(description="微信公众号长文字数统计")
    ap.add_argument("html_file", help="HTML 文件路径")
    ap.add_argument("--min", type=int, default=20000, help="字数下限（默认20000）")
    ap.add_argument("--max", type=int, default=45000, help="字数上限（默认45000）")
    args = ap.parse_args()

    try:
        with open(args.html_file, "r", encoding="utf-8") as f:
            html = f.read()
    except OSError as e:
        print(f"[错误] 无法读取文件: {e}", file=sys.stderr)
        sys.exit(2)

    text = strip_html(html)
    cjk, eng, num = count_words(text)
    total = cjk + eng + num

    status = "达标 ✅" if args.min <= total <= args.max else (
        "不足 ❌（需扩写）" if total < args.min else "超标 ⚠️（需精简）"
    )

    print("=" * 48)
    print(f"文件：{args.html_file}")
    print(f"中文字符：{cjk}")
    print(f"英文单词：{eng}")
    print(f"数字串  ：{num}")
    print(f"总字数  ：{total}")
    print(f"目标区间：{args.min} – {args.max}")
    print(f"判定    ：{status}")
    if total < args.min:
        print(f"还差    ：{args.min - total} 字")
    elif total > args.max:
        print(f"需精简  ：{total - args.max} 字")
    print("=" * 48)

    sys.exit(0 if args.min <= total <= args.max else 1)


if __name__ == "__main__":
    main()
