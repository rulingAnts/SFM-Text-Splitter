# SFM Text Splitter

SFM Text Splitter takes a single SFM (Toolbox/Shoebox) file containing multiple interlinear texts and splits it into separate, individual text files — one per interlinear text — ready for import into FieldWorks Language Explorer (FLEx).

## Why this is needed

FLEx cannot import multiple interlinear texts from a single file. When working with Toolbox/Shoebox exports that bundle several texts together, you must first split the file so that each interlinear text lives in its own file. This tool automates that split while preserving encoding and newline style.

## Key Features

- Strict-by-default detection of text boundaries using `\no`, `\id`, `\t`, `\te`, `\a`.
- Preserves source encoding and newline style in outputs.
- GUI-first workflow (Tk dialogs) with optional CLI mode.
- Safe filename derivation using titles/authors, with de-duplication.

## Getting Started

- Run `python -m scripts.split_sfm` and follow the prompts.
- Select Strict or Loose mode.
- Choose the input file and an EMPTY output folder.
- On success, the output folder opens automatically and a completion dialog appears.

## Attribution

- Author: Seth Johnston
- Assistant: GitHub Copilot (AI programming assistant)

## License

AGPL-3.0 — see [LICENSE](../LICENSE).
