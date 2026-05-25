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
  └── graphicsNumber.txt (Arabic numeral 0-9 and full-width ０-９ stroke paths + medians)
vendor/subAnimJ (git submodule, k1LoW/subAnimJ)
  └── graphicsJa.txt (kanji modifications tailored for Japanese elementary writing practice)
        │
        ▼
  stroke_data_parser.py  (animNumber entries are uniformly scaled, see "animNumber scaling";
                          subAnimJ entries override animCJK for the same character)
        │
        ▼
  data/*.json (one file per character)
  data/all.json (aggregated)
```

### animNumber scaling

`stroke_data_parser.py` applies a uniform affine transform to every entry loaded from `vendor/animNumber/graphicsNumber.txt` so digits land at the right position within the shared 1024×1024 viewBox. animNumber now ships digits at Klee One's native size with baseline at source y=28, so `NUMBER_SCALE` is `1.0` and the transform is a pure Y translation that maps the digit's natural bottom (y=12 in animNumber data) to animCJK's typical character bottom (y≈1).

- `NUMBER_SCALE = 1.0` (digit height ≈ 86% of `漢`)
- `NUMBER_ORIGIN_X = 512`
- `NUMBER_BOTTOM_SOURCE = 12`, `NUMBER_BOTTOM_TARGET = 1`

The transform is applied to both `strokes` (SVG path numbers) and `medians` (point lists), so they stay in lockstep.

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

- `python3 stroke_data_parser.py` - Regenerate data/ from vendor/{animCJK,animNumber,subAnimJ}
- `npm run serve` - Start local http-server (used to preview demo/index.html)
- `git submodule update --init --recursive` - Initialize all vendor/ submodules (animCJK, animNumber, subAnimJ)

## CI-driven regeneration

`.github/workflows/generate.yml` re-runs `stroke_data_parser.py` on Linux whenever `vendor/*` submodule pointers or `stroke_data_parser.py` change on `main` or in a PR, then commits the regenerated `data/*.json` back. **In most cases, do not hand-edit or commit `data/*.json` yourself** — bump the submodule (or edit the parser) and let CI regenerate. Manual edits to `data/` are reserved for special cases (e.g., the digit-scaling tuning constants in `stroke_data_parser.py`).

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
- Arphic Public License (subAnimJ kanji modifications, derived from animCJK)
