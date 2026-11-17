# The lecture deck

`project/deck.json` lists the slides in order and the sections; `project/slides/<id>.html` is one slide.
`assets/` holds the images used by the slides (the slides refer to them as `/_blob/<id>`; the file
`assets/<id>.png|svg|jpg` is the same image).

This folder is a **snapshot of the published deck** (a Claude Slides artifact, version 1794907683-2502,
2026-11-17, 53 slides). The published deck is the source of truth.

## Look at it locally

```bash
python tools/deck_tools.py preview     # writes slides/preview.html, open it in a browser
python tools/deck_tools.py notes       # writes notes/speaker-notes.md from the speaker notes
```

## Slide format

* One `<section id="...">` per slide, canvas 1920 × 1080 px, inline styles only.
* Speaker notes are in an `<aside>` at the end of the section.
* Footer (logos, title, page number) is plain absolutely positioned elements at the bottom of each slide.
* Images: `<img src="/_blob/<id>">`. Equations are SVG images (rendered from LaTeX).
* Colours: ONERA blue `#00509A`, orange `#B34F00`, light blue `#EAF1F8`, light orange `#FDEBD8`.

## What is not here

The scripts that generated the figures and equations (matplotlib, LaTeX to SVG) and the slide generator were
in a temporary working folder that no longer exists. The figures are kept as images in `assets/`.
