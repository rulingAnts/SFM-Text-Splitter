#!/usr/bin/env python3
from __future__ import annotations

import os
from typing import Tuple, Optional


def detect_newline_style_bytes(data: bytes) -> str:
    # Heuristic: prefer CRLF if present, else LF, else CR
    if b"\r\n" in data:
        return "\r\n"
    if b"\n" in data:
        return "\n"
    if b"\r" in data:
        return "\r"
    return "\n"


def detect_encoding(path: str) -> Tuple[str, float, bool]:
    """Return (encoding, confidence, has_bom) using charset-normalizer or chardet."""
    enc = "utf-8"
    conf = 1.0
    has_bom = False
    try:
        from charset_normalizer import from_path
        res = from_path(path)
        if res:
            best = res.best()
            if best:
                enc = best.encoding or enc
                conf = float(best.encoding_aliases and 0.8 or 0.6)
                # crude BOM detection for UTF-8
                try:
                    with open(path, 'rb') as f:
                        start = f.read(3)
                        has_bom = start == b"\xef\xbb\xbf"
                except Exception:
                    has_bom = False
    except Exception:
        try:
            import chardet  # type: ignore
            with open(path, 'rb') as f:
                raw = f.read()
                det = chardet.detect(raw)
                enc = det.get('encoding') or enc
                conf = float(det.get('confidence') or 0.5)
                has_bom = raw.startswith(b"\xef\xbb\xbf")
        except Exception:
            enc = "utf-8"
            conf = 0.5
            has_bom = False
    return enc, conf, has_bom


def read_text_preserve(path: str) -> Tuple[list[str], str, str]:
    """Read file, returning (lines_without_newlines, newline_style, encoding)."""
    with open(path, 'rb') as fb:
        raw = fb.read()
    newline_style = detect_newline_style_bytes(raw)
    # Detect encoding
    enc, conf, has_bom = detect_encoding(path)
    # Decode
    try:
        text = raw.decode(enc)
    except Exception:
        # Fallback to utf-8
        enc = "utf-8"
        text = raw.decode(enc, errors='replace')
    # Strip BOM in decoded
    if text.startswith("\ufeff"):
        text = text[1:]
    # Split lines while preserving content-only (no newlines)
    lines = text.splitlines()
    return lines, newline_style, enc


def write_lines_preserve(path: str, lines: list[str], newline_style: str, encoding: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    text = newline_style.join(lines)
    with open(path, 'w', encoding=encoding, newline='') as f:
        # writing with explicit newline='' prevents universal-newline translation
        f.write(text)
