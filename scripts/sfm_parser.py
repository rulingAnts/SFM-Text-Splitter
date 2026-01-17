#!/usr/bin/env python3
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional, Tuple

try:
    from .marker_config import MarkerConfig
except ImportError:
    from marker_config import MarkerConfig

_marker_re = re.compile(r"^\\([A-Za-z0-9]+)(?:\s+|$)")


@dataclass
class TextSlice:
    start: int
    end: int  # inclusive index
    title: Optional[str]
    authors: List[str]
    id_value: Optional[str]
    seq_no: Optional[str]


def parse_and_split(lines: list[str], cfg: MarkerConfig, strict: bool = True) -> Tuple[List[TextSlice], List[str]]:
    """
    Split input lines into texts using marker-based boundaries.
    Returns (slices, warnings).
    """
    warnings: List[str] = []
    slices: List[TextSlice] = []

    in_text = False
    seen_content = False
    current_start = None  # type: Optional[int]

    # metadata gathered for current text
    cur_title: Optional[str] = None
    cur_authors: List[str] = []
    cur_id: Optional[str] = None
    cur_seq: Optional[str] = None

    last_marker: Optional[str] = None

    def commit_slice(end_idx: int):
        nonlocal cur_title, cur_authors, cur_id, cur_seq
        if current_start is None:
            return
        slices.append(TextSlice(
            start=current_start,
            end=end_idx,
            title=cur_title,
            authors=cur_authors.copy(),
            id_value=cur_id,
            seq_no=cur_seq,
        ))
        # reset for next
        cur_title = None
        cur_authors.clear()
        cur_id = None
        cur_seq = None

    for i, line in enumerate(lines):
        m = _marker_re.match(line)
        code = m.group(1).lower() if m else None

        if code:
            last_marker = code
            is_start = cfg.is_start_marker(code)
            is_meta = cfg.is_metadata_marker(code)
            is_content = cfg.is_content_marker(code) or (not is_meta and not is_start)

            # capture metadata values
            if code in ("t", "te"):
                # Title could be on the same line after a space
                text = line[m.end():].strip()
                # Prefer priority order: keep first preferred
                if cur_title is None:
                    cur_title = text if text else cur_title
                else:
                    # if we have t but te not set and current is t, allow upgrade
                    if code == cfg.title_priority[0] and cur_title:
                        # upgrade to te if present
                        cur_title = text or cur_title
            elif code == "a":
                text = line[m.end():].strip()
                if text:
                    cur_authors.append(text)
            elif code == "id":
                cur_id = (line[m.end():].strip() or cur_id)
            elif code == "no":
                cur_seq = (line[m.end():].strip() or cur_seq)

            if is_start:
                if not in_text:
                    # Start a new text at this marker
                    in_text = True
                    seen_content = False
                    current_start = i
                else:
                    # inside metadata of current text; if we've seen content, this starts a new text
                    if seen_content:
                        commit_slice(i - 1)
                        in_text = True
                        seen_content = False
                        current_start = i
                        # metadata for next will be (re)captured automatically
                continue

            if is_content:
                if in_text:
                    seen_content = True
                else:
                    # Strict: ignore content before first text; Loose: treat as start
                    if not strict:
                        in_text = True
                        seen_content = True
                        current_start = i
                continue
        else:
            # Non-marker line: treat as continuation of previous marker or as content
            if in_text and last_marker:
                # continuation; if last_marker was content, mark seen_content
                if cfg.is_content_marker(last_marker) or (last_marker not in cfg.metadata_markers and last_marker not in cfg.start_markers):
                    seen_content = True
            elif not in_text and not strict:
                in_text = True
                seen_content = True
                current_start = i
            continue

    # commit last slice
    if in_text and current_start is not None:
        commit_slice(len(lines) - 1)

    if not slices:
        warnings.append("No texts detected with current marker configuration.")
    return slices, warnings
