from __future__ import annotations

import json
import threading
import tkinter as tk
from tkinter import ttk
from typing import Any

from ttkbootstrap.dialogs import Messagebox


class MednetTab(ttk.Frame):
    """Credential entry and verification tab."""

    def __init__(self, master: tk.Misc, mednet_client: Any, store: Any) -> None:
        super().__init__(master)
        self._client = mednet_client
        self._store = store
        self._verified = False
        self._headers: dict[str, str] | None = None
        self._build()

    def _build(self) -> None:
        ttk.Label(self, text="API Key").grid(row=0, column=0, sticky="w")
        self.api_entry = ttk.Entry(self, width=40)
        self.api_entry.grid(row=0, column=1, sticky="ew")

        ttk.Label(self, text="Security Key").grid(row=1, column=0, sticky="w")
        self.sec_entry = ttk.Entry(self, width=40, show="\u2022")
        self.sec_entry.grid(row=1, column=1, sticky="ew")

        self.test_btn = ttk.Button(self, text="Test & List Studies", command=self._on_test)
        self.test_btn.grid(row=2, column=0, columnspan=2, pady=5)

        self.progress = ttk.Progressbar(self, mode="indeterminate")
        self.progress.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 5))
        self.progress.grid_remove()

        ttk.Label(self, text="Study Key").grid(row=4, column=0, sticky="w")
        self.study_var = tk.StringVar()
        self.study_cb = ttk.Combobox(self, textvariable=self.study_var, state="disabled")
        self.study_cb.grid(row=4, column=1, sticky="ew")

        self.columnconfigure(1, weight=1)

    def _on_test(self) -> None:
        self.test_btn.configure(state="disabled")
        self.study_cb.configure(state="disabled")
        self.progress.grid()
        self.progress.start()
        threading.Thread(target=self._fetch_studies, daemon=True).start()

    def _fetch_studies(self) -> None:
        keys = {"x-api-key": self.api_entry.get(), "x-imn-security-key": self.sec_entry.get()}
        try:
            response = self._client.list_studies(headers=keys)
            status = getattr(response, "status_code", 200)
            if status >= 400:
                raise RuntimeError(getattr(response, "text", "API error"))
            data = response.json()
            items = data.get("data") if isinstance(data, dict) else data
            studies = [item.get("studyKey") for item in items or []]
            self.after(0, lambda: self._on_success(studies, keys))
        except Exception as exc:  # noqa: BLE001
            msg = str(exc)
            self.after(0, lambda: self._on_error(msg))

    def _on_success(self, studies: list[str], keys: dict[str, str]) -> None:
        self.progress.stop()
        self.progress.grid_remove()
        self.test_btn.configure(state="normal")
        if studies:
            self.study_cb.configure(values=studies, state="readonly")
            self.study_var.set(studies[0])
            self._verified = True
            self._headers = keys
            payload = json.dumps({"studyKey": self.study_var.get(), "headers": keys})
            self.event_generate("<<MednetCredsVerified>>", data=payload)
        else:
            self.study_cb.configure(values=(), state="disabled")
            Messagebox.show_error("No studies found", title="Error")
            self._verified = False

    def _on_error(self, message: str) -> None:
        self.progress.stop()
        self.progress.grid_remove()
        self.test_btn.configure(state="normal")
        self.study_cb.configure(state="disabled")
        Messagebox.show_error(message, title="Error")
        self._verified = False

    def save(self) -> None:
        if not self._verified or self._headers is None:
            return
        study_key = self.study_var.get()
        if not study_key:
            return
        self._store.save_secret(f"mednet:{study_key}", json.dumps(self._headers))


__all__ = ["MednetTab"]
