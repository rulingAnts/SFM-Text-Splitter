# SFM Text Splitter

Split multi-text SFM (Toolbox/Shoebox) files into separate, individual text files — one per interlinear text — so they can be imported into FieldWorks Language Explorer (FLEx). FLEx cannot import multiple interlinear texts from a single file; this tool performs the required pre-split.

- Default mode: strict (new text starts on any of `\no`, `\id`, `\t`, `\te`, `\a`).
- Preserves original encoding and newline style; default output extension `.txt` (configurable).
- Output folder must be empty to avoid accidental overwrites.
- GUI-first flow with Tk dialogs; CLI mode available.

## Install

Python 3.9+ recommended.

```bash
pip install -r requirements.txt
```

## Quick Start (GUI)

1. Run the app:
   ```bash
   python -m scripts.split_sfm
   ```
2. Choose Strict or Loose mode.
3. Select your input SFM/text file.
4. Select an EMPTY output folder.
5. On success, the app opens the output folder (Explorer/Finder) and shows a completion dialog.

## CLI Usage

```bash
python -m scripts.split_sfm \
  "/path/to/input.sfm" \
  "/path/to/empty-output-folder" \
  --extension .txt
```

Options:
- `--strict` (default) or `--loose`
- `--cli` run without GUI dialogs
- `--extension .txt` output file extension
- `--encoding utf-8` force encoding (otherwise auto-detected)
- `--config markers.json` load marker configuration from JSON

## Marker configuration JSON (advanced)

```json
{
  "start_markers": ["no","id","t","te","a"],
  "metadata_markers": ["no","id","t","te","a","so","genre","com","arg","mkr"],
  "content_markers": ["tx","gl","ft","fte","d","dsseg","mb","ph"],
  "priority_order": ["te","t"],
  "join_authors_with": "-"
}
```

## Windows Build (Portable EXE)

From the repo root on Windows (CMD):

```bat
build_windows.bat
```

This produces a portable, windowed, onefile EXE at `dist\SFM Text Splitter.exe` and a zipped artifact `dist\SFM Text Splitter.zip` suitable for distribution.

## Attribution

- Author: Seth Johnston
- Assistant: GitHub Copilot (AI programming assistant)

## License

AGPL-3.0 — see [LICENSE](LICENSE).
