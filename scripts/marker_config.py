#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Set, Dict, Any


@dataclass
class MarkerConfig:
    # Markers that explicitly indicate the start of a new text
    start_markers: Set[str] = field(default_factory=lambda: {
        "no", "id", "t", "te", "a"
    })
    # Markers considered metadata (can appear in intro blocks)
    metadata_markers: Set[str] = field(default_factory=lambda: {
        "no", "id", "t", "te", "a", "so", "genre", "com", "arg", "mkr"
    })
    # Markers considered content (interlinear/discourse)
    content_markers: Set[str] = field(default_factory=lambda: {
        "tx", "gl", "ft", "fte", "d", "dsseg", "mb", "ph"
    })
    # Title resolution priority
    title_priority: tuple[str, ...] = ("te", "t")
    # Author joiner
    join_authors_with: str = "-"

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "MarkerConfig":
        # Accept simple keys; ignore unknowns gracefully
        mc = cls()
        if not isinstance(data, dict):
            return mc
        sm = data.get("start_markers")
        if isinstance(sm, (list, set)):
            mc.start_markers = {str(x).strip("\\").lower() for x in sm if str(x).strip()}
        mm = data.get("metadata_markers")
        if isinstance(mm, (list, set)):
            mc.metadata_markers = {str(x).strip("\\").lower() for x in mm if str(x).strip()}
        cm = data.get("content_markers")
        if isinstance(cm, (list, set)):
            mc.content_markers = {str(x).strip("\\").lower() for x in cm if str(x).strip()}
        tp = data.get("priority_order") or data.get("title_priority")
        if isinstance(tp, (list, tuple)) and tp:
            mc.title_priority = tuple(str(x).strip("\\").lower() for x in tp if str(x).strip())
        ja = data.get("join_authors_with")
        if isinstance(ja, str) and ja:
            mc.join_authors_with = ja
        return mc

    def is_start_marker(self, code: str) -> bool:
        return code.lower() in self.start_markers

    def is_metadata_marker(self, code: str) -> bool:
        return code.lower() in self.metadata_markers

    def is_content_marker(self, code: str) -> bool:
        return code.lower() in self.content_markers
