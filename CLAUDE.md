# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Fork of [chanind/hanzi-writer-data-jp](https://github.com/chanind/hanzi-writer-data-jp). Provides Japanese character stroke data (SVG paths + median points) for the [Hanzi Writer](https://github.com/chanind/hanzi-writer) library. Published as `@k1low/hanzi-writer-data-jp` on npm and served via unpkg CDN.

## Architecture

### Data pipeline

```
vendor/animCJK (git submodule, parsimonhi/animCJK)
  ├── dictionaryJa.txt (character decomposition)
  ├── graphicsJa.txt (kanji stroke paths + medians)
  └── graphicsJaKana.txt (hiragana/katakana stroke paths + medians)
vendor/animNumber (git submodule, k1LoW/animNumber)
  └── graphicsNumber.txt (Arabic numeral 0-9 stroke paths + medians)
        │
        ▼
  stroke_data_parser.py
        │
        ▼
  data/*.json (one file per character)
  data/all.json (aggregated)
```

### npm publish flow

`prepublishOnly` copies `data/*` to the repo root. `.npmignore` excludes `data/`, `vendor/`, `stroke_data_parser.py`, and `all.json`, so the published package contains only individual character JSON files at the root level.

`index.js` intentionally throws to prevent `require('hanzi-writer-data-jp')` and force per-character imports like `require('hanzi-writer-data-jp/私')`.

### Character JSON format

```json
{
  "strokes": ["M518,382C614,392...Z"],
  "medians": [[[111, 395], [190, 372], ...]]
}
```

### Demo page

`demo/index.html` is a self-contained HTML page using Hanzi Writer + this package's data via unpkg CDN. Deployed to GitHub Pages via `.github/workflows/pages.yml`.

## Commands

- `python3 stroke_data_parser.py` - Regenerate data/ from vendor/animCJK
- `npm run serve` - Start local http-server for development
- `git submodule update --init` - Initialize the animCJK submodule in vendor/

## macOS / APFS caveat

APFS NFC-normalizes filenames, so CJK Compatibility Ideographs (U+F900-U+FAFF) collide with their canonical Unified Ideograph counterparts (e.g., 侮 U+F9D6 vs U+4FAE) on disk. `stroke_data_parser.py` skips U+F900-U+FAFF entries on macOS to avoid overwriting the canonical files, but the CI-generated U+F900-U+FAFF files committed to the repo still appear as "modified" in `git status` after a local regeneration. **These local diffs against `data/<U+F900-U+FAFF>.json` files are spurious — never stage or commit them.** Only CI on Linux can regenerate them correctly. When opening a PR after a local parser run, stage only the digit/character JSON files you actually intended to change (e.g., `data/0.json`, `data/all.json`).

## Release

Automated via [Songmu/tagpr](https://github.com/Songmu/tagpr). Pushing to main triggers tagpr to create a release PR. Merging that PR creates a git tag + GitHub Release, which triggers `npm publish` using npm Trusted Publishing (OIDC).

## Licenses

Multiple licenses apply simultaneously (AND, not OR) to the data. See `licenses/` directory:
- Arphic Public License (font-derived data)
- LGPL v3+ (animCJK processing)
- Unicode License (Unihan DB data)
- SIL Open Font License 1.1 (Klee One glyph outlines, applies to Arabic numeral 0-9 and full-width ０-９ data via animNumber)
