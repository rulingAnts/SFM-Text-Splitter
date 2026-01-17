#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Optional

# Tkinter optional
try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
    TK_AVAILABLE = True
except Exception:
    TK_AVAILABLE = False

# Robust imports to work in: module mode, script mode, and PyInstaller
try:
    # Preferred: import as a package (works in PyInstaller, and when run from repo root)
    from scripts.marker_config import MarkerConfig
    from scripts.sfm_parser import parse_and_split
    from scripts.io_utils import read_text_preserve, write_lines_preserve
    from scripts.filename_utils import make_filename, dedupe_filename
except Exception:
    try:
        # Fallback: same directory imports (when running directly from scripts folder)
        from marker_config import MarkerConfig
        from sfm_parser import parse_and_split
        from io_utils import read_text_preserve, write_lines_preserve
        from filename_utils import make_filename, dedupe_filename
    except Exception:
        # Last resort: relative imports when executed as module (python -m scripts.split_sfm)
        from .marker_config import MarkerConfig
        from .sfm_parser import parse_and_split
        from .io_utils import read_text_preserve, write_lines_preserve
        from .filename_utils import make_filename, dedupe_filename


def ensure_empty_dir(path: str) -> bool:
    if not os.path.isdir(path):
        return False
    return len(os.listdir(path)) == 0


def load_config(config_path: Optional[str]) -> MarkerConfig:
    if not config_path:
        return MarkerConfig()
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return MarkerConfig.from_json(data)
    except Exception:
        return MarkerConfig()


def run_cli(input_path: Optional[str], output_dir: Optional[str], strict: bool, ext: str, encoding: Optional[str], config_path: Optional[str], headless: bool) -> int:
    # Initial GUI prompt: strict/loose (no custom marker configuration in current version)
    if TK_AVAILABLE and not headless:
        strict = initial_prompt_gui(default_strict=strict)

    # Resolve input/output via GUI if missing; no interactive CLI prompts
    if TK_AVAILABLE and not headless:
        input_path, output_dir = choose_paths_gui(input_path, output_dir)
        if not input_path:
            print("ERROR: No input file selected.", file=sys.stderr)
            return 2
        if not os.path.isfile(input_path):
            messagebox.showerror("Invalid input", "Cannot read input file.")
            print("ERROR: Cannot read input file.", file=sys.stderr)
            return 2
        if not output_dir:
            print("ERROR: No output folder selected.", file=sys.stderr)
            return 3
        if not os.path.isdir(output_dir):
            # In GUI selection, directory should exist; just error if not
            messagebox.showerror("Invalid output folder", "Output folder must exist and be empty.")
            print("ERROR: Output folder must exist and be empty.", file=sys.stderr)
            return 3
        if not ensure_empty_dir(output_dir):
            messagebox.showerror("Invalid output folder", "Output folder must be empty.")
            print("ERROR: Output folder must be empty.", file=sys.stderr)
            return 3
    else:
        # Headless: use provided CLI args only; do not prompt via input()
        if not input_path or not os.path.isfile(input_path):
            print("ERROR: Cannot read input file.", file=sys.stderr)
            return 2
        if not output_dir:
            print("ERROR: No output folder selected.", file=sys.stderr)
            return 3
        if not os.path.isdir(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
            except Exception:
                print("ERROR: Cannot create output folder.", file=sys.stderr)
                return 3
        if not ensure_empty_dir(output_dir):
            print("ERROR: Output folder must be empty.", file=sys.stderr)
            return 3

    # Load default or JSON-provided markers (no UI configuration)
    cfg = load_config(config_path)

    # Read input preserving encoding/newlines
    lines, newline_style, enc_detected = read_text_preserve(input_path)
    enc_to_use = encoding or enc_detected

    # Split texts
    slices, warnings = parse_and_split(lines, cfg, strict=strict)
    for w in warnings:
        print(f"WARN: {w}", file=sys.stderr)
    if not slices:
        print("ERROR: No texts found; adjust markers or use --loose.", file=sys.stderr)
        return 5

    # Write outputs
    existing = set()
    count = 0
    for sl in slices:
        # title from priority, authors joined with join_authors_with
        title = sl.title
        authors_joined = cfg.join_authors_with.join(sl.authors) if sl.authors else ""
        fallback = None
        if sl.id_value:
            fallback = sl.id_value
        elif sl.seq_no:
            fallback = f"no{sl.seq_no}"
        fname = make_filename(title, [authors_joined] if authors_joined else [], ext=ext, fallback=fallback)
        fname = dedupe_filename(fname, existing)
        existing.add(fname)

        out_path = os.path.join(output_dir, fname)
        write_lines_preserve(out_path, lines[sl.start:sl.end+1], newline_style, enc_to_use)
        count += 1

    print(f"INFO: Wrote {count} texts to {output_dir}")
    return 0


def initial_prompt_gui(default_strict: bool = True) -> bool:
    root = tk.Tk(); root.title("SFM Splitter Setup")
    strict_var = tk.BooleanVar(value=default_strict)

    ttk.Label(root, text="Choose mode:").pack(anchor="w", padx=10, pady=(10,4))
    mode_frame = ttk.Frame(root); mode_frame.pack(fill="x", padx=10)
    ttk.Radiobutton(mode_frame, text="Strict (default)", variable=strict_var, value=True).pack(side="left")
    ttk.Radiobutton(mode_frame, text="Loose", variable=strict_var, value=False).pack(side="left")

    result = {"strict": default_strict}

    def on_ok():
        result["strict"] = bool(strict_var.get())
        root.destroy()

    ttk.Button(root, text="Continue", command=on_ok).pack(pady=10)
    root.mainloop()
    return result["strict"]


def choose_paths_gui(input_path: Optional[str], output_dir: Optional[str]) -> tuple[Optional[str], Optional[str]]:
    root = tk.Tk(); root.withdraw()
    if not input_path:
        input_path = filedialog.askopenfilename(title="Choose SFM input file", filetypes=[("Text/SFM","*.txt *.sfm"),("All","*.*")])
    # Loop until an empty output folder is selected or cancel
    while True:
        if not output_dir:
            output_dir = filedialog.askdirectory(title="Choose EMPTY output folder")
        if not output_dir:
            # user cancelled
            break
        if not os.path.isdir(output_dir):
            messagebox.showerror("Invalid output folder", "Output folder must exist and be empty.")
            output_dir = None
            continue
        if not ensure_empty_dir(output_dir):
            messagebox.showerror("Invalid output folder", "Output folder must be empty.")
            output_dir = None
            continue
        break
    return input_path, output_dir


def configure_markers_ui(cfg: MarkerConfig) -> MarkerConfig:
    root = tk.Tk()
    root.title("Configure Markers")
    root.geometry("520x420")

    strict_var = tk.BooleanVar(value=True)

    ttk.Label(root, text="Mode").pack(anchor="w", padx=8, pady=(8,0))
    mode_frame = ttk.Frame(root); mode_frame.pack(fill="x", padx=8)
    ttk.Radiobutton(mode_frame, text="Strict", variable=strict_var, value=True).pack(side="left")
    ttk.Radiobutton(mode_frame, text="Loose", variable=strict_var, value=False).pack(side="left")

    def make_listbox(title: str, items: list[str]) -> tuple[ttk.Label, tk.Listbox]:
        ttk.Label(root, text=title).pack(anchor="w", padx=8, pady=(12,0))
        lb = tk.Listbox(root, selectmode="multiple", height=6)
        for it in items:
            lb.insert("end", it)
        lb.pack(fill="x", padx=8)
        return lb

    start_items = sorted(cfg.start_markers)
    meta_items = sorted(cfg.metadata_markers)
    content_items = sorted(cfg.content_markers)

    # listboxes
    start_lb = tk.Listbox(root, selectmode="multiple", height=6)
    ttk.Label(root, text="Start-of-Text Markers").pack(anchor="w", padx=8, pady=(12,0))
    for it in start_items:
        start_lb.insert("end", it)
    start_lb.pack(fill="x", padx=8)

    ttk.Label(root, text="Metadata Markers").pack(anchor="w", padx=8, pady=(12,0))
    meta_lb = tk.Listbox(root, selectmode="multiple", height=6)
    for it in meta_items:
        meta_lb.insert("end", it)
    meta_lb.pack(fill="x", padx=8)

    ttk.Label(root, text="Content Markers").pack(anchor="w", padx=8, pady=(12,0))
    content_lb = tk.Listbox(root, selectmode="multiple", height=6)
    for it in content_items:
        content_lb.insert("end", it)
    content_lb.pack(fill="x", padx=8)

    ttk.Label(root, text="Join authors with").pack(anchor="w", padx=8, pady=(12,0))
    join_entry = ttk.Entry(root)
    join_entry.insert(0, cfg.join_authors_with)
    join_entry.pack(fill="x", padx=8)

    result = {"cfg": cfg, "strict": True}

    def on_ok():
        sel_start = {start_items[i] for i in start_lb.curselection()} or set(cfg.start_markers)
        sel_meta = {meta_items[i] for i in meta_lb.curselection()} or set(cfg.metadata_markers)
        sel_content = {content_items[i] for i in content_lb.curselection()} or set(cfg.content_markers)
        ja = join_entry.get() or cfg.join_authors_with
        result["cfg"] = MarkerConfig(
            start_markers=sel_start,
            metadata_markers=sel_meta,
            content_markers=sel_content,
            title_priority=cfg.title_priority,
            join_authors_with=ja,
        )
        result["strict"] = bool(strict_var.get())
        root.destroy()

    ttk.Button(root, text="OK", command=on_ok).pack(pady=12)
    root.mainloop()
    # Update global strict based on UI; caller can use .get("strict") if needed
    return result["cfg"]


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Split multi-text SFM files into individual files.")
    p.add_argument("input", nargs="?", help="Input SFM/text file path")
    p.add_argument("output", nargs="?", help="Output folder (must be empty)")
    p.add_argument("--strict", action="store_true", help="Strict mode (default): start markers only")
    p.add_argument("--loose", action="store_true", help="Loose mode: allow blank-line/content heuristics")
    p.add_argument("--cli", action="store_true", help="Run without GUI dialogs")
    p.add_argument("--extension", default=".txt", help="Output extension (default .txt)")
    p.add_argument("--encoding", default=None, help="Force input/output encoding (default: auto)")
    p.add_argument("--config", default=None, help="JSON marker config file path")
    return p


def main(argv: Optional[list[str]] = None) -> int:
    ap = build_arg_parser()
    args = ap.parse_args(argv)

    strict = True if args.strict or not args.loose else False

    code = run_cli(
        input_path=args.input,
        output_dir=args.output,
        strict=strict,
        ext=args.extension,
        encoding=args.encoding,
        config_path=args.config,
        headless=args.cli,
    )
    return code


if __name__ == "__main__":
    raise SystemExit(main())
