import os
import subprocess
import sys
from typing import Optional

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

# Reuse existing logic from the repo
try:
    from scripts.marker_config import MarkerConfig
    from scripts.sfm_parser import parse_and_split
    from scripts.io_utils import read_text_preserve, write_lines_preserve
    from scripts.filename_utils import make_filename, dedupe_filename
except Exception:
    # Fallback to relative imports if packaged differently
    from ..scripts.marker_config import MarkerConfig  # type: ignore
    from ..scripts.sfm_parser import parse_and_split  # type: ignore
    from ..scripts.io_utils import read_text_preserve, write_lines_preserve  # type: ignore
    from ..scripts.filename_utils import make_filename, dedupe_filename  # type: ignore


def ensure_empty_dir(path: str) -> bool:
    return os.path.isdir(path) and len(os.listdir(path)) == 0


def open_folder_in_os(path: str) -> None:
    try:
        if os.name == 'nt':
            os.startfile(path)  # type: ignore[attr-defined]
        elif sys.platform == 'darwin':
            subprocess.run(['open', path], check=False)
        else:
            subprocess.run(['xdg-open', path], check=False)
    except Exception:
        pass


class SFMTextSplitterApp(toga.App):
    def startup(self):
        self.main_window = toga.MainWindow(title="SFM Text Splitter")

        # State
        self.strict = True
        self.input_path: Optional[str] = None
        self.output_dir: Optional[str] = None
        self.config_path: Optional[str] = None
        self.extension: str = ".txt"
        self.encoding: Optional[str] = None

        # Controls
        mode_label = toga.Label("Mode")
        self.mode_select = toga.Selection(items=["Strict", "Loose"], on_select=self.on_mode_select)
        self.mode_select.value = "Strict"

        input_label = toga.Label("Input SFM file")
        self.input_value = toga.Label("None selected", style=Pack(color="#666"))
        input_btn = toga.Button("Select…", on_press=self.on_select_input)

        output_label = toga.Label("Output folder (must be empty)")
        self.output_value = toga.Label("None selected", style=Pack(color="#666"))
        output_btn = toga.Button("Select…", on_press=self.on_select_output)

        config_label = toga.Label("JSON marker config (optional)")
        self.config_value = toga.Label("None", style=Pack(color="#666"))
        config_btn = toga.Button("Select…", on_press=self.on_select_config)

        run_btn = toga.Button("Run Split", style=Pack(padding_top=10), on_press=self.on_run_split)
        self.status = toga.Label("", style=Pack(color="#0a0"))

        # Layout
        row1 = toga.Box(children=[mode_label, self.mode_select], style=Pack(direction=ROW, padding=6, alignment="center"))
        row2 = toga.Box(children=[input_label, input_btn], style=Pack(direction=ROW, padding=6, alignment="center"))
        row2b = toga.Box(children=[self.input_value], style=Pack(direction=ROW, padding_left=12))
        row3 = toga.Box(children=[output_label, output_btn], style=Pack(direction=ROW, padding=6, alignment="center"))
        row3b = toga.Box(children=[self.output_value], style=Pack(direction=ROW, padding_left=12))
        row4 = toga.Box(children=[config_label, config_btn], style=Pack(direction=ROW, padding=6, alignment="center"))
        row4b = toga.Box(children=[self.config_value], style=Pack(direction=ROW, padding_left=12))
        row5 = toga.Box(children=[run_btn], style=Pack(direction=ROW, padding=10))
        row6 = toga.Box(children=[self.status], style=Pack(direction=ROW, padding=6))

        content = toga.Box(children=[row1, row2, row2b, row3, row3b, row4, row4b, row5, row6], style=Pack(direction=COLUMN, padding=12))
        self.main_window.content = content
        self.main_window.show()

    # Handlers
    def on_mode_select(self, widget):
        self.strict = (widget.value == "Strict")

    async def on_select_input(self, widget):
        try:
            path = await self.main_window.open_file_dialog("Choose SFM input file", file_types=["txt", "sfm", "*"], multiselect=False)
        except Exception:
            path = None
        if path:
            self.input_path = path
            self.input_value.text = path

    async def on_select_output(self, widget):
        try:
            folder = await self.main_window.open_folder_dialog("Choose EMPTY output folder")
        except Exception:
            folder = None
        if folder:
            if not os.path.isdir(folder):
                await self.main_window.error_dialog("Invalid output folder", "Output folder must exist and be empty.")
                return
            if not ensure_empty_dir(folder):
                await self.main_window.error_dialog("Invalid output folder", "Output folder must be empty.")
                return
            self.output_dir = folder
            self.output_value.text = folder

    async def on_select_config(self, widget):
        try:
            path = await self.main_window.open_file_dialog("Choose JSON marker config", file_types=["json", "*"], multiselect=False)
        except Exception:
            path = None
        if path:
            self.config_path = path
            self.config_value.text = path

    async def on_run_split(self, widget):
        if not self.input_path or not os.path.isfile(self.input_path):
            await self.main_window.error_dialog("Invalid input", "Please select a valid input file.")
            return
        if not self.output_dir or not os.path.isdir(self.output_dir):
            await self.main_window.error_dialog("Invalid output folder", "Please select an existing, empty output folder.")
            return
        if not ensure_empty_dir(self.output_dir):
            await self.main_window.error_dialog("Invalid output folder", "Output folder must be empty.")
            return

        # Load config
        cfg: MarkerConfig
        try:
            if self.config_path:
                import json
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                cfg = MarkerConfig.from_json(data)
            else:
                cfg = MarkerConfig()
        except Exception:
            cfg = MarkerConfig()

        # Read input preserving encoding/newlines
        lines, newline_style, enc_detected = read_text_preserve(self.input_path)
        enc_to_use = self.encoding or enc_detected

        # Split
        slices, warnings = parse_and_split(lines, cfg, strict=self.strict)
        if warnings:
            # Show warnings inline but don't interrupt flow
            self.status.text = "\n".join([f"WARN: {w}" for w in warnings])
        if not slices:
            await self.main_window.error_dialog("No texts found", "No texts were detected with the current markers. Try Loose mode or adjust markers via JSON config.")
            return

        # Write outputs
        existing = set()
        count = 0
        for sl in slices:
            title = sl.title
            authors_joined = cfg.join_authors_with.join(sl.authors) if sl.authors else ""
            fallback = None
            if sl.id_value:
                fallback = sl.id_value
            elif sl.seq_no:
                fallback = f"no{sl.seq_no}"
            fname = make_filename(title, [authors_joined] if authors_joined else [], ext=self.extension, fallback=fallback)
            fname = dedupe_filename(fname, existing)
            existing.add(fname)

            out_path = os.path.join(self.output_dir, fname)  # type: ignore[arg-type]
            write_lines_preserve(out_path, lines[sl.start:sl.end+1], newline_style, enc_to_use)
            count += 1

        self.status.text = f"Wrote {count} texts to {self.output_dir}"
        try:
            await self.main_window.info_dialog("Done", f"Wrote {count} texts to:\n{self.output_dir}")
        except Exception:
            pass
        try:
            open_folder_in_os(self.output_dir)  # type: ignore[arg-type]
        except Exception:
            pass


def main():
    return SFMTextSplitterApp("SFM Text Splitter", "com.rulingants.sfmtextsplitter")

if __name__ == "__main__":
    app = main()
    app.main_loop()
