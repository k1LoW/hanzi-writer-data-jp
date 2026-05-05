# Hanzi Writer Japanese Data

This is a fork of [chanind/hanzi-writer-data-jp](https://github.com/chanind/hanzi-writer-data-jp).

## About

This is the character data used by [Hanzi Writer](https://github.com/chanind/hanzi-writer) for Japanese.

This data is published in a separate repo from Hanzi Writer for the following reasons:
- This data is licensed separately from the Hanzi Writer source code.
- This allows users who wish to import character data in NPM to do so without forcing everyone to download the character data along with Hanzi Writer.
- Publishing on NPM makes this data available on the [unpkg CDN](https://unpkg.com/@k1low/hanzi-writer-data-jp/), so data can be loaded via, for instance, https://unpkg.com/@k1low/hanzi-writer-data-jp@latest/私.json.

Check out [chanind.github.io/hanzi-writer](https://chanind.github.io/hanzi-writer) for more info about Hanzi Writer.

## Demo

https://k1low.github.io/hanzi-writer-data-jp/

## Usage
Until this is supported directly in Hanzi Writer, you'll need to use a custom `charDataLoader` function to use this data in Hanzi Writer. An example of how you can do that using `fetch` and the content on unpkg is shown below:

```
HanziWriter.create('target-div', '私', {
  width: 400,
  height: 400,
  charDataLoader: (char, onLoad, onError) => {
    fetch(`https://unpkg.com/@k1low/hanzi-writer-data-jp@latest/${char}.json`)
      .then(res => res.json())
      .then(onLoad)
      .catch(onError);
  }
})
```

## Notes on stroke count

Some characters may have more strokes in the data than their standard stroke count. This is because the upstream [animCJK](https://github.com/parsimonhi/animCJK) project splits a single stroke into multiple paths for animation purposes (e.g., to control the drawing direction on curves). For example, 「あ」 is 3 strokes but has 4 strokes in the data. This is intentional and not a bug.

## Notes on Arabic numerals

Arabic numeral data (half-width 0-9 and full-width ０-９) comes from [animNumber](https://github.com/k1LoW/animNumber), whose glyphs are based on Klee One. `stroke_data_parser.py` applies a uniform affine transform (`NUMBER_SCALE = 1.0`, anchored at the canvas x-center and at the digit's natural bottom y=12) to every animNumber entry, which is effectively a Y translation that lands each digit's bottom at y≈1 (matching `漢`). The digit height is ≈86% of `漢` so digits and kanji line up visually within the shared 1024×1024 viewBox. The same transform is applied to both `strokes` and `medians`.

## Notes on regenerating data on macOS

Running `python3 stroke_data_parser.py` on macOS produces a working tree diff against many CJK Compatibility Ideograph (U+F900-U+FAFF) JSON files (e.g., `data/侮.json`, `data/海.json`). This is caused by APFS NFC normalizing filenames, so `data/侮.json` (U+F9D6) collides with `data/侮.json` (U+4FAE) on disk. The parser already skips U+F900-U+FAFF entries on macOS to avoid corrupting the Unified Ideograph files, but the existing CI-generated U+F900-U+FAFF files in the repo still appear "modified" locally. These diffs are spurious and should not be committed; only CI on Linux can regenerate them correctly.

## Current limitations compared with the Chinese data
- This data does not support radicals yet
- This data does not have capped strokes, so there are sharp edges where strokes intersect

## License

This data comes from [animCJK](https://github.com/parsimonhi/animCJK) and the [Make Me A Hanzi](https://github.com/skishore/makemeahanzi) project, which extracted the data from fonts by [Arphic Technology](http://www.arphic.com/), a Taiwanese font forge that released their work under a permissive license in 1999. You can redistribute and/or modify this data under the terms of the Arphic Public License as published by Arphic Technology Co., Ltd. A copy of this license can be found in [ARPHICPL.TXT](https://raw.githubusercontent.com/chanind/hanzi-writer-data/master/ARPHICPL.TXT).

AnimCJK's data is licensed under LGPL.
You can redistribute and/or modify these files under the terms of the GNU
Lesser General Public License as published by the Free Software Foundation,
either version 3 of the license, or (at your option) any later version. You
should have received a copy of this license (the file "LGPL.txt") along with
these files; if not, see <http://www.gnu.org/licenses/>.

Arabic numeral data (half-width 0-9 and full-width ０-９) is derived from [animNumber](https://github.com/k1LoW/animNumber), whose glyph outlines are derived and modified from [Klee One Regular](https://fonts.google.com/specimen/Klee+One) by Fontworks Inc. Klee One is licensed under the [SIL Open Font License, Version 1.1](licenses/OFL.txt).
