# Usage Guide

## GUI (Recommended)

1. Launch the app:
   ```bash
   python -m scripts.split_sfm
   ```
2. Choose Strict or Loose mode.
3. Select your input SFM/text file.
4. Select an EMPTY output folder.
5. The app writes one file per interlinear text, opens the folder, and shows a success dialog.

## CLI

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
- `--encoding utf-8` force encoding
- `--config markers.json` load marker configuration from JSON

## Marker Configuration (Advanced)

You can supply a JSON file:

```json
{
  "start_markers": ["no","id","t","te","a"],
  "metadata_markers": ["no","id","t","te","a","so","genre","com","arg","mkr"],
  "content_markers": ["tx","gl","ft","fte","d","dsseg","mb","ph"],
  "priority_order": ["te","t"],
  "join_authors_with": "-"
}
```

Use `--config path/to/markers.json` to load these settings.

## Windows Portable Build

From CMD in the repo root:

```bat
build_windows.bat
```

This creates `dist\SFM Text Splitter.exe` and `dist\SFM Text Splitter.zip` for distribution.
