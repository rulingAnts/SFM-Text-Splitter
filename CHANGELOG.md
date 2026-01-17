# Changelog

## v1.0.0 — 2026-01-17

Initial release.

- Splits multi-text SFM (Toolbox/Shoebox) files into one file per interlinear text.
- Strict-by-default start markers: `\no`, `\id`, `\t`, `\te`, `\a`.
- Preserves source encoding and newline style.
- GUI-first workflow; CLI mode supported.
- Safe filenames from titles/authors with de-duplication.
- Windows portable build via PyInstaller onefile + windowed (`dist/SFM Text Splitter.exe`).
- Distribution artifact: `dist/SFM Text Splitter.zip`.
