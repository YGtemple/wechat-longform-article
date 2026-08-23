#!/usr/bin/env python3
"""
微信公众号长文 AI 痕迹扫描器。
扫描 HTML 正文（去标签后的可见文本）中的：
  1. 绝对禁用词（AI/人工智能/大模型等暴露AI身份的词）——命中即不合格；
  2. 高危元话语（"根据搜索结果""综上所述"等暴露流水线的表达）——需逐条改写；
  3. 占位符残留（TODO/XXX/在这里写等模板未替换内容）。
用法：
  python3 scan_ai_traces.py <article.html>
退出码：0 = 未发现绝对禁用词；1 = 发现绝对禁用词；2 = 文件错误。
"""
import re
import sys

# 绝对禁用：出现即判定文章不合格
ABSOLUTE_FORBIDDEN = [
    r"AI\s*生成", r"AI\s*写作", r"AI\s*助手", r"AI\s*模型", r"AI\s*工具",
    r"人工智能", r"大语言模型", r"大模型", r"语言模型", r"机器学习模型",
    r"ChatGPT", r"GPT-?\d", r"Claude", r"Gemini", r"文心一言", r"通义千问",
    r"豆包", r"DeepSeek", r"Llama", r"Copilot",
    r"机器人写作", r"机器写作", r"机器生成", r"自动生成", r"算法生成",
    r"AIGC", r"prompt", r"提示词工程",
    r"作为(?:一个)?AI", r"作为(?:一个)?人工智能", r"本助手", r"我是(?:一个)?(?:AI|人工智能|语言模型)",
    r"无法(?:访问|浏览|联网|实时)", r"作为(?:一个)?(?:AI|语言模型)(?:助手)?",
    r"由(?:AI|人工智能|大模型)(?:生成|撰写|创作|驱动)",
]

# 高危元话语：暴露调研/写作流水线，需改写为第一人称表达
HIGH_RISK_PHRASES = [
    "根据搜索结果", "综合各平台", "综合网络信息", "根据网络资料", "根据网上资料",
    "数据显示", "研究表明", "调查显示", "有分析认为", "有观点认为", "有人指出",
    "综上所述", "总而言之", "总的来说", "概而言之",
    "让我们一起来看看", "让我们看看", "本文将", "本文从以下几个方面",
    "随着社会的发展", "随着互联网的发展", "随着时代的发展", "在当今社会", "众所周知",
    "值得一提的是", "不可否认", "毋庸置疑",
    "首先，", "其次，", "再次，", "最后，",
    "赋能", "抓手", "闭环", "底层逻辑", "顶层设计", "组合拳",
    "据悉", "据了解", "据介绍",
    "引发了广泛关注", "引起热烈反响", "引发热议", "受到广泛关注",
    "笔者",
]

# 模板占位符残留
PLACEHOLDERS = [
    "TODO", "XXX", "在这里写", "示例", "example.com", "封面图注",
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

    abs_hits = find_hits(text, ABSOLUTE_FORBIDDEN, is_regex=True)
    risk_hits = find_hits(text, HIGH_RISK_PHRASES, is_regex=False)
    place_hits = find_hits(text, PLACEHOLDERS, is_regex=False)

    print("=" * 60)
    print(f"文件：{path}")
    print("=" * 60)

    if abs_hits:
        print(f"\n[严重] 发现 {len(abs_hits)} 处绝对禁用词（必须删除/改写）：")
        for word, ctx in abs_hits:
            print(f"  ✗ 「{word}」 …{ctx}…")
    else:
        print("\n[通过] 未发现绝对禁用词。")

    if risk_hits:
        print(f"\n[警告] 发现 {len(risk_hits)} 处高危元话语（建议改写为第一人称表达）：")
        seen = set()
        for word, ctx in risk_hits:
            key = (word, ctx)
            if key in seen:
                continue
            seen.add(key)
            print(f"  ! 「{word}」 …{ctx}…")
    else:
        print("\n[通过] 未发现高危元话语。")

    if place_hits:
        print(f"\n[警告] 发现 {len(place_hits)} 处占位符/模板残留（发布前必须替换）：")
        seen = set()
        for word, ctx in place_hits:
            key = (word, ctx)
            if key in seen:
                continue
            seen.add(key)
            print(f"  ? 「{word}」 …{ctx}…")
    else:
        print("\n[通过] 未发现占位符残留。")

    print("\n" + "=" * 60)
    if abs_hits:
        print("结论：不合格 ❌ —— 存在绝对禁用词，修改后重新扫描。")
        sys.exit(1)
    else:
        print("结论：通过 ✅ —— 无绝对禁用词。" +
              ("（仍建议处理上述警告项）" if (risk_hits or place_hits) else ""))
        sys.exit(0)


if __name__ == "__main__":
    main()
