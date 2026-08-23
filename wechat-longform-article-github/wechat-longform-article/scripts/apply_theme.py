#!/usr/bin/env python3
"""
微信公众号长文主题换色工具。
把模板默认的竹青配色一键替换为指定主题色，不改动任何布局和功能色标签。

每个主题包含五个色阶：
  主色    —— 章节标题、小节色块、胶囊标签、强调文字
  深色    —— 渐变章节标题、单数据大卡的渐变末端
  浅底    —— 章节卡片背景
  高亮底  —— 荧光笔高亮背景
  柔和底  —— 数字步骤卡、对话气泡背景

用法：
  python3 apply_theme.py <article.html> <theme> [output.html]
  python3 apply_theme.py --list

<theme> 可选：
  bamboo          竹青（默认，文学/深度通用）
  tech-blue       科技蓝（科技/互联网/AI）
  warm-orange    暖橙（生活/消费/烟火气）
  forest          森林绿（自然/健康/环保）
  elegant-purple  典雅紫（文化/艺术/女性）
  china-red       中国红（时政/宏大叙事/节庆）
  ink-dark        墨黑（严肃/评论/财经）
  sunset          日落橘（人物/故事/情感）
  teal            青蓝（新知/科普/商业）
  rose            玫红（时尚/情感/年轻向）

不带 output.html 时覆盖原文件。建议在最终定稿后运行一次。
"""
import sys
import re
import signal
import os

if os.name != "nt":
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)

# 每个主题五个色值：(主色, 深色, 浅底, 高亮底, 柔和底)
# 默认 bamboo 的五个色值会被替换为目标主题的对应色值。
PALETTES = {
    "bamboo":         ("#2d5f4f", "#1e4236", "#eef4f1", "#dcebe5", "#f5f9f7"),
    "tech-blue":      ("#1f6fb5", "#155a8a", "#e9f2fb", "#d4e6f7", "#f4f9fd"),
    "warm-orange":    ("#d97706", "#b45309", "#fef3e2", "#fde4c3", "#fef9f0"),
    "forest":         ("#2f7d4f", "#1f5a38", "#eaf6ef", "#d4ecde", "#f3faf6"),
    "elegant-purple": ("#7c5cbf", "#5e42a6", "#f2edfb", "#e3d8f5", "#f8f5fd"),
    "china-red":      ("#c0392b", "#962d22", "#fdf0ee", "#faddd9", "#fef5f4"),
    "ink-dark":       ("#34495e", "#22303c", "#eef1f5", "#dde4ea", "#f5f7f9"),
    "sunset":         ("#e0643a", "#c04a28", "#fef0ea", "#fcded2", "#fef6f2"),
    "teal":           ("#0f766e", "#0a554f", "#e6f4f2", "#cde8e4", "#f1f9f8"),
    "rose":           ("#be4977", "#9e355f", "#fceef4", "#f8d9e7", "#fef5f9"),
}

# 模板默认色值（bamboo）
DEFAULTS = PALETTES["bamboo"]


def list_themes():
    print("可用主题（主色 / 深色 / 浅底 / 高亮底 / 柔和底）：")
    for name, colors in PALETTES.items():
        mark = "（默认）" if name == "bamboo" else ""
        print(f"  {name:<16} {colors[0]} / {colors[1]} / {colors[2]} / {colors[3]} / {colors[4]}{mark}")


def apply_theme(html: str, theme: str) -> tuple[str, int]:
    if theme not in PALETTES:
        raise ValueError(f"未知主题：{theme}（用 --list 查看可用主题）")
    target = PALETTES[theme]
    if theme == "bamboo":
        return html, 0
    total = 0
    out = html
    for old, new in zip(DEFAULTS, target):
        pattern = re.compile(re.escape(old), re.IGNORECASE)
        out, n = pattern.subn(new, out)
        total += n
    return out, total


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)
    if "--list" in args:
        list_themes()
        sys.exit(0)
    if len(args) < 2:
        print("用法: python3 apply_theme.py <article.html> <theme> [output.html]", file=sys.stderr)
        sys.exit(2)

    path, theme = args[0], args[1]
    out_path = args[2] if len(args) > 2 else path

    try:
        with open(path, "r", encoding="utf-8") as f:
            html = f.read()
    except OSError as e:
        print(f"[错误] 无法读取文件: {e}", file=sys.stderr)
        sys.exit(2)

    try:
        out, n = apply_theme(html, theme)
    except ValueError as e:
        print(f"[错误] {e}", file=sys.stderr)
        sys.exit(2)

    try:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(out)
    except OSError as e:
        print(f"[错误] 无法写入文件: {e}", file=sys.stderr)
        sys.exit(2)

    c = PALETTES[theme]
    print(f"✅ 已应用主题「{theme}」：替换 {n} 处颜色")
    print(f"   主色 {c[0]} / 深色 {c[1]} / 浅底 {c[2]} / 高亮 {c[3]} / 柔和 {c[4]}")
    print(f"   输出：{out_path}")
    if n == 0 and theme != "bamboo":
        print("   ⚠️ 未替换到任何颜色——文件是否已套用其他主题？建议基于原始模板生成的文章换色。")


if __name__ == "__main__":
    main()
