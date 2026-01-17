# SFM Text Splitter v1.0.0

Release date: 2026-01-17

## Overview

SFM Text Splitter automates splitting a single SFM (Toolbox/Shoebox) file containing multiple interlinear texts into separate, individual text files—one per interlinear text—so they can be imported into FieldWorks Language Explorer (FLEx).

## Features

- Detects text boundaries via start markers (`\no`, `\id`, `\t`, `\te`, `\a`) in strict mode by default.
- Preserves original encoding and newline style.
- GUI-first workflow with Tk dialogs; CLI mode available.
- Safe filename derivation using titles/authors with de-duplication.
- On success, opens the output folder (Explorer/Finder) and shows a completion dialog.

## Windows Portable Build

- Portable EXE: `dist/SFM Text Splitter.exe` (PyInstaller onefile, windowed)
- Distribution ZIP: `dist/SFM Text Splitter.zip`

## Attribution

- Author: Seth Johnston
- Assistant: GitHub Copilot (AI programming assistant)

## License

AGPL-3.0 — see [LICENSE](LICENSE).
