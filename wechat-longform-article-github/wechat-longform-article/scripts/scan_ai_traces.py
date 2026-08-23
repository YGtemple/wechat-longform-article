#!/usr/bin/env python3
"""
微信公众号长文 AI 作者身份扫描器。

设计原则：
  AI、人工智能、大模型、ChatGPT 等词作为文章讨论对象时完全可以正常出现，
  本脚本不扫描这些词。本脚本只拦截两类问题：
  1. 【严重】直接声明"本文由 AI/模型/机器生成或撰写"的身份表述，以及 AI 拒答话术
     —— 命中即不合格，必须删除，因为这等于告诉读者文章不是人写的；
  2. 【警告】模板化元话语（"根据搜索结果""综上所述"等）让文章像通稿
     —— 给出提示，由作者结合语境自行判断是否改写，不阻塞交付；
  3. 【警告】占位符/模板示例文字残留。

用法：
  python3 scan_ai_traces.py <article.html>
退出码：0 = 未发现身份声明；1 = 发现身份声明；2 = 文件错误。
"""
import re
import sys
import signal
import os

if os.name != "nt":
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)

# 【严重】直接暴露"本文由 AI 撰写/生成"的身份声明，命中即不合格。
# 注意：只匹配"声明作者身份"的句式，不匹配作为讨论对象的"AI/大模型"等词。
IDENTITY_CLAIMS = [
    # 本文/该文章由 AI/模型/机器 生成/撰写
    r"(?:本文|该文|这篇文章|本章|本节|以下内容|全文).{0,8}(?:由|是).{0,8}(?:AI|人工智能|大模型|语言模型|大语言模型|机器|算法|程序|系统).{0,6}(?:生成|撰写|写作|创作|写就|产出|自动)",
    r"(?:由|这是).{0,8}(?:AI|人工智能|大模型|语言模型|大语言模型|机器|算法).{0,6}(?:生成|撰写|写作|创作|自动产出).{0,10}(?:的)?(?:本文|文章|内容|稿件|文字|报道)",
    r"AI\s*(?:生成|写作|创作|撰写).{0,6}(?:的)?(?:本文|文章|内容|稿件|文字)",
    r"(?:本文|文章|内容).{0,6}(?:由|是).{0,6}AI\s*(?:生成|写作|创作|撰写)",
    r"内容由.{0,6}AI.{0,6}生成",
    r"机器(?:自动)?(?:写作|生成|创作)|算法(?:自动)?生成|自动生成(?:的)?(?:本文|文章|内容)",
    r"(?:本文|文章).{0,6}AIGC",
    r"声明[:：].{0,12}(?:AI|人工智能|大模型|模型|机器).{0,6}(?:生成|创作|撰写)",
    # 作为 AI / 我是一个 AI / 本助手
    r"作为(?:一个|一名|一个)?(?:AI|人工智能|语言模型|大模型|大语言模型|智能助手|AI助手|聊天机器人)",
    r"我是(?:一个|一名)?(?:AI|人工智能|语言模型|大模型|大语言模型|智能助手|AI助手|聊天机器人|机器人)",
    r"本助手|AI助手(?:为您|为你|帮您|帮你|为大家)|智能助手(?:为您|为你)",
    r"作为(?:一个)?(?:AI|语言模型)(?:助手)?，?(?:我)?(?:无法|不能|不会|没有)",
    # AI 拒答/自谦话术（明显是聊天机器人而非文章作者会说的话）
    r"(?:我|笔者|本助手)(?:无法|不能|不会)(?:访问|浏览|联网|获取|实时|预测|保证)",
    r"我没有(?:实时|联网|访问|浏览).{0,10}(?:数据|信息|能力)",
    r"如果(?:你|您)(?:有|还有).{0,6}(?:其他)?(?:问题|疑问|需要).{0,10}(?:欢迎)?(?:随时)?(?:提问|咨询|告诉我)",
]

# 【警告】模板化元话语：让文章像通稿/AI腔，建议结合语境改写为第一人称表达。
# 这些不是硬禁忌——某些语境下可能自然出现——所以只警告不拦截。
STYLE_WARNINGS = [
    "根据搜索结果", "综合各平台", "综合网络信息", "根据网络资料", "根据网上资料",
    "数据显示", "研究表明", "调查显示", "有分析认为", "有观点认为", "有人指出",
    "综上所述", "总而言之", "总的来说", "概而言之",
    "让我们一起来看看", "让我们看看", "本文将", "本文从以下几个方面",
    "随着社会的发展", "随着互联网的发展", "随着时代的发展", "在当今社会", "众所周知",
    "值得一提的是", "不可否认", "毋庸置疑",
    "赋能", "抓手", "闭环", "底层逻辑", "顶层设计", "组合拳",
    "据悉", "据了解", "据介绍",
    "引发了广泛关注", "引起热烈反响", "引发热议", "受到广泛关注",
    "笔者",
    "感谢您的阅读", "感谢阅读", "仅供参考", "不构成投资建议",
    "欢迎在评论区留言", "喜欢请点赞关注",
]

# 模板占位符残留
PLACEHOLDERS = [
    "TODO", "在这里写", "example.com", "封面图注",
    "图为某某", "待补充", "占位",
]


def strip_html(html: str) -> str:
    html = re.sub(r"<!--.*?-->", "", html, flags=re.DOTALL)
    html = re.sub(r"<(script|style)\b.*?</\1>", "", html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", html)
    return text


def find_hits(text: str, patterns, is_regex=False):
    hits = []
    for pat in patterns:
        if is_regex:
            for m in re.finditer(pat, text, flags=re.IGNORECASE):
                start = max(0, m.start() - 18)
                end = min(len(text), m.end() + 18)
                ctx = text[start:end].replace("\n", " ").strip()
                hits.append((m.group(0), ctx))
        else:
            start = 0
            low = text.lower()
            key = pat.lower()
            while True:
                idx = low.find(key, start)
                if idx == -1:
                    break
                s = max(0, idx - 18)
                e = min(len(text), idx + len(pat) + 18)
                ctx = text[s:e].replace("\n", " ").strip()
                hits.append((pat, ctx))
                start = idx + len(pat)
    return hits


def dedup(hits):
    seen = set()
    out = []
    for word, ctx in hits:
        key = (word, ctx)
        if key in seen:
            continue
        seen.add(key)
        out.append((word, ctx))
    return out


def main():
    if len(sys.argv) < 2:
        print("用法: python3 scan_ai_traces.py <article.html>", file=sys.stderr)
        sys.exit(2)

    path = sys.argv[1]
    try:
        with open(path, "r", encoding="utf-8") as f:
            html = f.read()
    except OSError as e:
        print(f"[错误] 无法读取文件: {e}", file=sys.stderr)
        sys.exit(2)

    text = strip_html(html)

    id_hits = dedup(find_hits(text, IDENTITY_CLAIMS, is_regex=True))
    style_hits = dedup(find_hits(text, STYLE_WARNINGS, is_regex=False))
    place_hits = dedup(find_hits(text, PLACEHOLDERS, is_regex=False))

    print("=" * 60)
    print(f"文件：{path}")
    print("=" * 60)
    print("说明：AI/人工智能/大模型/ChatGPT 等词作为讨论对象可正常使用，")
    print("      本脚本只拦截“本文由AI生成”这类身份声明。")

    if id_hits:
        print(f"\n[严重] 发现 {len(id_hits)} 处 AI 作者身份声明（必须删除/改写）：")
        for word, ctx in id_hits:
            print(f"  ✗ 「{word}」 …{ctx}…")
    else:
        print("\n[通过] 未发现 AI 作者身份声明。")

    if style_hits:
        print(f"\n[提示] 发现 {len(style_hits)} 处模板化表达（像通稿，建议按语境改写）：")
        for word, ctx in style_hits:
            print(f"  ! 「{word}」 …{ctx}…")
        print("  （这些不是硬禁忌，自然语境下可保留；密集出现则建议改写。）")
    else:
        print("\n[通过] 未发现模板化元话语。")

    if place_hits:
        print(f"\n[警告] 发现 {len(place_hits)} 处占位符/模板残留（发布前必须替换）：")
        for word, ctx in place_hits:
            print(f"  ? 「{word}」 …{ctx}…")
    else:
        print("\n[通过] 未发现占位符残留。")

    print("\n" + "=" * 60)
    if id_hits:
        print("结论：不合格 ❌ —— 存在 AI 身份声明，删除后重新扫描。")
        sys.exit(1)
    else:
        print("结论：通过 ✅ —— 无 AI 身份声明。" +
              ("（建议浏览上述提示项）" if (style_hits or place_hits) else ""))
        sys.exit(0)


if __name__ == "__main__":
    main()
