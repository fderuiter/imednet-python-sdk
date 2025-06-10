from __future__ import annotations

import json
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any

import pandas as pd


class ResultsViewer(tk.Toplevel):
    """Display table and JSON results in a dedicated window."""

    def __init__(self, master: tk.Misc, data: Any) -> None:
        super().__init__(master)
        self.title("Results Viewer")
        self.geometry("800x600")
        self._df = self.to_dataframe(data)
        self._json_data = self.to_json(data)
        self._build()

    def _build(self) -> None:
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)
        self._build_table_tab(nb)
        self._build_json_tab(nb)

    def _build_table_tab(self, nb: ttk.Notebook) -> None:
        frame = ttk.Frame(nb)
        nb.add(frame, text="Table")
        tree = ttk.Treeview(frame, show="headings")
        yscroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=yscroll.set)
        tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        if not self._df.empty:
            tree["columns"] = list(self._df.columns)
            for col in self._df.columns:
                tree.heading(col, text=col)
                tree.column(col, width=100)
            for row in self._df.itertuples(index=False):
                tree.insert("", "end", values=list(row))
        btn = ttk.Button(frame, text="Export CSV", command=self._export_csv_dialog)
        btn.grid(row=1, column=0, sticky="e", pady=5)

    def _build_json_tab(self, nb: ttk.Notebook) -> None:
        frame = ttk.Frame(nb)
        nb.add(frame, text="JSON")
        text = tk.Text(frame)
        yscroll = ttk.Scrollbar(frame, orient="vertical", command=text.yview)
        text.configure(yscrollcommand=yscroll.set)
        text.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        pretty = json.dumps(self._json_data, indent=2, ensure_ascii=False, default=str)
        text.insert(tk.END, pretty)
        text.configure(state="disabled")
        btn = ttk.Button(frame, text="Download JSON", command=self._export_json_dialog)
        btn.grid(row=1, column=0, sticky="e", pady=5)

    def _export_csv_dialog(self) -> None:
        if self._df.empty:
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV files", "*.csv")]
        )
        if path:
            self.export_csv(self._df, Path(path))
            messagebox.showinfo("Saved", f"CSV exported to {path}")

    def _export_json_dialog(self) -> None:
        path = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=[("JSON files", "*.json")]
        )
        if path:
            self.export_json(self._json_data, Path(path))
            messagebox.showinfo("Saved", f"JSON exported to {path}")

    @staticmethod
    def to_dataframe(data: Any) -> pd.DataFrame:
        if isinstance(data, pd.DataFrame):
            return data
        if isinstance(data, list) and data and isinstance(data[0], dict):
            return pd.DataFrame(data)
        if isinstance(data, dict):
            return pd.DataFrame([data])
        return pd.DataFrame()

    @staticmethod
    def to_json(data: Any) -> Any:
        if isinstance(data, pd.DataFrame):
            return data.to_dict(orient="records")
        return data

    @staticmethod
    def export_csv(df: pd.DataFrame, path: Path) -> None:
        df.to_csv(path, index=False)

    @staticmethod
    def export_json(data: Any, path: Path) -> None:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False, default=str)
