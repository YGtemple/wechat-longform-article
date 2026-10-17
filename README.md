<div align="right">

**[English](README.md)** · [简体中文](README.zh-CN.md)

</div>

# wechat-longform-article

A pipeline for WeChat long reads — research to original article to formatted HTML.

<sub>HTML · ready to publish</sub>

---

## The workflow

WeChat articles go through three stages before they publish:

```
research → write the original piece → render to styled HTML
```

Keeping those as separate steps means the writing and the layout are not tangled. You draft the article as text, then drop it into the template that renders mobile-friendly HTML for the WeChat editor.

## What the template handles

- **Mobile-first layout** — paragraphs, blockquotes and heading hierarchy tuned for narrow reading
- **Paste-ready** — the rendered HTML pastes into the WeChat editor cleanly, without re-styling
- **Single page** — `template.html` holds the layout, so a new article means changing the content, not the template

## Layout

```
template.html       the layout template
相关文件             see README history / folder
```

## License

MIT