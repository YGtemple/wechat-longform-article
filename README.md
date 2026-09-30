# wechat-longform-article ·「竹心一言」微信公众号长文创作 Skill

> 一句话简介：公众号长文流水线：调研→原创长文→HTML 排版，可直接发布

## 一、项目概述与定位

这是一个面向 AI Agent（豆包 / 兼容 Skill 机制的助手）的可复用技能包，作者署名**「竹心一言」**。用户只需给出**主题、日期范围、风格倾向**，它就自动跨 10+ 平台搜集素材，以第一人称撰写一篇 2 万–4.5 万字的微信公众号深度长文，最终交付一个**内联样式、可直接复制到公众号后台发布**的单文件 HTML。

它解决的核心痛点：①公众号长文排版在后台容易被清洗样式；②AI 写的万字长文"一屏黑字"、通稿感重、像资料汇编；③没有真实多平台素材支撑。本 Skill 用"调研—写作—排版—配图—自检"一体化流水线来应对。

## 二、核心能力（9 条硬性约束）

1. **字数硬门槛**：正文 2 万–4.5 万字（默认 2.5–3.5 万），用脚本实测，禁止估算。
2. **多平台调研**：素材来源 ≥10 个平台且至少含 1 个视频平台。
3. **日期范围**：严格限定用户给定起止日期，占位符先追问。
4. **配图与组件密度**：全文 ≥10 张图、每 800–1800 字一张；至少用到 6 类视觉组件；每连续 3 段纯文字后必须插入配图或组件。
5. **正文色彩密度**：禁止整段纯黑字；每段至少一处内联色彩（主题色加粗关键词 / 五色荧光笔按语义轮换 / 彩色数字大号 / 段首彩色引导词 / 核心句放大 / 情绪词着色）。
6. **第一人称 + 署名"竹心一言"**。
7. **零 AI 作者身份**：不出现"本文由 AI 生成/作为 AI 助手"等声明与拒答话术；但 AI/大模型/ChatGPT 作为**讨论对象**可正常使用。
8. **微信兼容**：全部内联 `style`，禁用 `<style>`/class/JS/position/浮动；渐变用纯色兜底 + `linear-gradient` 渐进增强。
9. **可直接发布**：单文件 HTML，本地与公众号后台均不丢样式图片。

## 三、工作流（7 步）

第0步确认参数 → 第1步多平台调研（`general_search` 并行 + `doubao-video-extract` 提取视频字幕 + `browser-task` 采集登录态平台，每条素材记五要素写入 `research_notes.md`）→ 第2步搭 8–15 章大纲（标注字数/配图/组件位置）→ 第3步配图（AI 生成为主、强调色彩鲜艳饱满，真实实体才网络搜图，能用 HTML 组件的不占图片额度）→ 第4步分章写作（边写边上色）→ 第5步 HTML 排版（套模板、暖米底色 `#faf7f0`、17px/1.9 行高，定稿后一键换主题色）→ 第6步三重自检 → 第7步交付 HTML。

## 四、技术栈与脚本

纯 Markdown Skill + 3 个 Python 3 标准库脚本（无第三方依赖）：

| 脚本 | 作用 |
|---|---|
| `scripts/word_count.py` | 中文字数统计（中文字符+英文词+数字串，与 Word 口径一致），支持 `--min/--max` 区间判定（默认 20000–45000） |
| `scripts/scan_ai_traces.py` | AI 痕迹扫描器：①【严重】正则拦截"本文由AI生成/作为AI助手/我无法联网"等身份声明与拒答话术（命中即退出码 1，必须删除）；②【警告】模板化元话语（"综上所述""根据搜索结果""赋能/抓手/闭环""笔者"等通稿腔）仅提示不拦截；③【警告】占位符残留（TODO/example.com） |
| `scripts/apply_theme.py` | 10 套主题配色一键替换，只替换模板默认竹青的 5 个色阶（主色/深色/浅底/高亮底/柔和底），不动布局与功能标签色 |

## 五、完整目录结构

仓库根目录为"已发布形态"，内层 `wechat-longform-article-github/wechat-longform-article/` 是标准 Skill 目录：

```
wechat-longform-article/                 # 仓库根（发布预览形态）
├── README.md                            # 项目说明（特性/组件/结构/用法）
├── LICENSE（MIT 许可证）.license        # MIT 许可证
├── template.html                        # 完整排版模板（31.5KB，= assets/template.html）
├── template.html（双击可在浏览器预览排版）.html  # 精简预览版（14KB）
└── wechat-longform-article-github/       # 内层完整 Skill
    ├── LICENSE
    ├── README.md
    └── wechat-longform-article/
        ├── SKILL.md                     # Skill 主文件（触发条件+9条硬约束+7步工作流）
        ├── assets/template.html         # 微信公众号排版模板（22类内联组件）
        ├── references/
        │   ├── writing-guide.md         # 写作风格、去AI味指南、组件与配色说明（20KB）
        │   └── platforms.md             # 10+ 平台清单与采集方法、素材整理模板（5KB）
        └── scripts/
            ├── word_count.py
            ├── scan_ai_traces.py
            └── apply_theme.py
```

## 六、关键内容解读

- **`SKILL.md`**：带 YAML frontmatter（`name: wechat-longform-article`，中文 description 写明触发场景：围绕主题+日期范围跨 10+ 平台写 2 万字以上可发布公众号长文时使用）。是整个流水线的规则中枢。
- **`assets/template.html`**：提供 **22 类排版组件**——标题区、章节卡片标题、渐变章节标题、小节标题、正文段落（6 种内联色彩手法）、五色标签段落（蓝定义/绿解析/橙影响/红警示/紫延伸）、金句卡片、对话气泡、人物卡片、Q&A 问答、红绿对比行、浅色旁注、三列多彩数据卡、单数据大卡（深色渐变白字）、纵向时间线、双列对比卡、数字步骤卡、要点列表、关键词标签云、配图（标准/色条两种图注）、两种分隔符、作者署名区。
- **`references/platforms.md`**：把 10+ 平台按视频（抖音/B站/快手/视频号）、社交问答（微博/知乎/小红书/豆瓣/贴吧）、新闻资讯（头条/澎湃/腾讯网易/百度资讯/搜狗微信）、垂类（36氪/虎嗅、雪球、丁香园、懂车帝、政府网）分组；规定每条素材五要素（平台|时间|事实观点|金句数据|URL）与 `research_notes.md` 整理模板（时间线/事实数据/人物案例/观点光谱/金句库/争议待核查）。
- **`references/writing-guide.md`**：写作风格与去 AI 味指南、组件使用频率、第八节主题配色按选题自动匹配。
- **`apply_theme.py` 的 10 套主题**：bamboo 竹青（默认，文学/深度）、tech-blue 科技蓝、warm-orange 暖橙、forest 森林绿、elegant-purple 典雅紫、china-red 中国红、ink-dark 墨黑、sunset 日落橘、teal 青蓝、rose 玫红。蓝/绿/橙/红四个功能标签色固定不变。

## 七、运行与使用

安装：把 `wechat-longform-article` 文件夹放入 Agent 的 skills 目录（`SKILL.md` 须在根）。触发：自然语言下达"用 wechat-longform-article，主题是…，日期…，写 3 万字，深度调查风格"。

```bash
python3 scripts/word_count.py article.html --min 20000 --max 45000
python3 scripts/scan_ai_traces.py article.html
python3 scripts/apply_theme.py article.html tech-blue
```

## 八、数据/资源构成

全部为**文本文件**（Markdown/HTML/Python/License），无图片、音视频、字体等二进制文件；HTML 模板中的图片为引用占位/示例。外部数据来自运行时多平台采集，不预置。

## 九、项目特点

1. **视觉密度优先**：把"万字长文不劝退读者"当作工程问题——配色、组件、配图频率都量化成硬指标。
2. **事实底线**：数字/日期/人名/引语均来自真实采集，冲突时呈现多版本，不编造；采不到就换平台，"宁可少一个案例，不可造一个事实"。
3. **诚实区分"AI 作为讨论对象"与"AI 身份声明"**：扫描器精准拦截身份自曝，不误伤科技选题里正常讨论大模型的内容。
4. **与作者其他写作 Skill 同源**：其微信内联 HTML 组件体系与"竹青/科技蓝/暖橙…"十套配色，和 UItimateWriter 的 `ref-wechat-html.md` 为同一套设计语言。
