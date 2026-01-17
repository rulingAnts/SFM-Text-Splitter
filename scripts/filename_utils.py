#!/usr/bin/env python3
from __future__ import annotations

import re
import unicodedata
from typing import Iterable, Optional

SAFE_MAX_LEN = 80
RESERVED_BASENAMES = {"CON","PRN","AUX","NUL","COM1","COM2","COM3","COM4","COM5","COM6","COM7","COM8","COM9","LPT1","LPT2","LPT3","LPT4","LPT5","LPT6","LPT7","LPT8","LPT9"}

_invalid_chars_re = re.compile(r'[\\/\?%\*:|"<>\x00-\x1F]')
_multi_dash_re = re.compile(r"[-\s]+")


def _ascii_slug(text: str) -> str:
    if not text:
        return ""
    # Normalize unicode and drop non-ascii
    norm = unicodedata.normalize("NFKD", text)
    ascii_text = norm.encode("ascii", "ignore").decode("ascii")
    ascii_text = ascii_text.strip()
    ascii_text = _invalid_chars_re.sub("", ascii_text)
    ascii_text = _multi_dash_re.sub("-", ascii_text)
    ascii_text = ascii_text.strip("- ")
    ascii_text = ascii_text.lower()
    if not ascii_text:
        return ""
    if ascii_text.upper() in RESERVED_BASENAMES:
        ascii_text = f"_{ascii_text}"
    return ascii_text[:SAFE_MAX_LEN]


def make_filename(title: Optional[str], authors: Iterable[str], ext: str = ".txt", fallback: Optional[str] = None) -> str:
    title_slug = _ascii_slug(title or "")
    authors = [a for a in (authors or []) if a]
    author_slug = _ascii_slug("-".join(authors)) if authors else ""
    base = None
    if title_slug and author_slug:
        base = f"{title_slug} - {author_slug}"
    elif title_slug:
        base = title_slug
    elif author_slug:
        base = author_slug
    elif fallback:
        base = _ascii_slug(fallback)
    else:
        base = "untitled"
    # Ensure extension starts with '.'
    ext = ext if ext.startswith(".") else f".{ext}"
    return f"{base}{ext}"


def dedupe_filename(name: str, existing: set[str]) -> str:
    if name not in existing:
        return name
    stem, dot, ext = name.rpartition(".")
    counter = 2
    while True:
        candidate = f"{stem}-{counter}.{ext}" if dot else f"{stem}-{counter}"
        if candidate not in existing:
            return candidate
        counter += 1
