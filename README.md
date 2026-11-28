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

## Artwork policy

- **Real photos ≥ 1/2 (must be the majority)**: people, news scenes, keynotes, products and interfaces, report covers — sourced via image search; every piece covers all four kinds. Captions describe the scene only — no credit lines or outlet names.
- **AI concept images ≥ 1/3**: boundaries, radii, permission layers, timelines — generated with a saturated palette and no text.
- **Alternate the two**: one image per 350–600 characters; ≥16 images under 10k characters (18–20 recommended), ≥24 for 20k–45k pieces (30+ recommended); at least 2 per chapter.
- Details in `references/images.md`.

## Voice rules

- **No word count in the header**: the meta line keeps only the byline and the date.
- **No recap framing**: never write "two short videos said…" or "the blogger said…"; the lead must be the author's own judgement, and sources go in the footer only.
- **Pre-delivery review**: render at a 390–430px mobile viewport and check every screen, then run the five readability questions (conflict in the title, a personal opening observation, hook in the first three screens, a pause on every screen, a quotable closing line).

## Layout

```
template.html       the layout template
相关文件             see README history / folder
```

## License

MIT