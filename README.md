# SFM Text Splitter

Split multi-text SFM (Toolbox/Shoebox) files into one file per text.

- Default mode: strict (new text starts on any of `\no`, `\id`, `\t`, `\te`, `\a`).
- Optional marker configuration UI (Tkinter) to customize metadata/content markers.
- Preserves original encoding and newline style; default output extension `.txt` (configurable).
- Output folder must be empty.

## Install

Python 3.9+ recommended.

```bash
pip install -r requirements.txt
```

## Usage

CLI with positional arguments:

```bash
python -m scripts.split_sfm \
  "/path/to/input.sfm" \
  "/path/to/empty-output-folder" \
  --extension .txt
```

If you omit the input or output path, Tk file open / directory select dialogs will prompt you (when Tkinter is available). Add `--configure` to open the marker configuration UI.

### Options

- `--strict` (default) or `--loose`
- `--configure` open marker configuration dialog (Tk)
- `--cli` force non-GUI prompts
- `--extension .txt` output file extension
- `--encoding utf-8` force encoding (otherwise auto-detected)
- `--config markers.json` load marker configuration from JSON

## Marker configuration JSON

```json
{
  "start_markers": ["no","id","t","te","a"],
  "metadata_markers": ["no","id","t","te","a","so","genre","com","arg","mkr"],
  "content_markers": ["tx","gl","ft","fte","d","dsseg","mb","ph"],
  "priority_order": ["te","t"],
  "join_authors_with": "-"
}
```

## Notes

- Multiple authors are joined with `-` in filenames.
- Filenames derive from `te` → `t` and authors, with safe slugging and de-duplication.
- When no titles/authors exist, filenames fall back to `id` or `no`, else `untitled`.
