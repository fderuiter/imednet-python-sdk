from __future__ import annotations

import json
import threading
import tkinter as tk
from tkinter import ttk

from ttkbootstrap.dialogs import Messagebox


class MednetTab(ttk.Frame):
    """Tab for entering and verifying Mednet credentials."""

    def __init__(self, master: tk.Misc, mednet_client, store) -> None:  # type: ignore[no-untyped-def]
        super().__init__(master)
        self._client = mednet_client
        self._store = store
        self._verified_keys: dict[str, str] | None = None
        self._build()

    def _build(self) -> None:
        ttk.Label(self, text="API Key").grid(row=0, column=0, sticky="w")
        self.api_entry = ttk.Entry(self)
        self.api_entry.grid(row=0, column=1, sticky="ew")

        ttk.Label(self, text="Security Key").grid(row=1, column=0, sticky="w")
        self.sec_entry = ttk.Entry(self, show="\u2022")
        self.sec_entry.grid(row=1, column=1, sticky="ew")

        self.test_btn = ttk.Button(self, text="Test & List Studies", command=self._start_test)
        self.test_btn.grid(row=2, column=0, columnspan=2, pady=(5, 0))

        self.progress = ttk.Progressbar(self, mode="indeterminate")
        self.progress.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(5, 0))
        self.progress.grid_remove()

        ttk.Label(self, text="Study").grid(row=4, column=0, sticky="w")
        self.study_var = tk.StringVar()
        self.study_combo = ttk.Combobox(self, textvariable=self.study_var, state="disabled")
        self.study_combo.grid(row=4, column=1, sticky="ew")

        self.save_btn = ttk.Button(self, text="Save", command=self._save, state="disabled")
        self.save_btn.grid(row=5, column=0, columnspan=2, pady=(5, 0))

        self.columnconfigure(1, weight=1)

    def _start_test(self) -> None:
        self.test_btn.config(state="disabled")
        self.save_btn.config(state="disabled")
        self.study_combo.config(state="disabled")
        self.progress.grid()
        self.progress.start()
        thread = threading.Thread(target=self._list_studies_bg, daemon=True)
        thread.start()

    def _list_studies_bg(self) -> None:
        keys = {
            "x-api-key": self.api_entry.get(),
            "x-imn-security-key": self.sec_entry.get(),
        }
        try:
            response = self._client.list_studies(headers=keys)
            if response.status_code >= 400:
                raise RuntimeError(str(response.text))
            data = response.json()
            studies = [item.get("studyKey") for item in data.get("data", [])]
            self.after(0, self._on_studies_ready, keys, studies)
        except Exception as exc:  # noqa: BLE001
            self.after(0, self._on_studies_error, exc)

    def _on_studies_ready(self, keys: dict[str, str], studies: list[str]) -> None:
        self.progress.stop()
        self.progress.grid_remove()
        self.test_btn.config(state="normal")
        self.study_combo["values"] = studies
        if studies:
            self.study_var.set(studies[0])
            self.study_combo.config(state="readonly")
            self.save_btn.config(state="normal")
            self._verified_keys = keys
            payload = json.dumps({"study_key": self.study_var.get(), "headers": keys})
            self.event_generate("<<MednetCredsVerified>>", when="tail", data=payload)
        else:
            self.study_combo.config(state="disabled")

    def _on_studies_error(self, exc: Exception) -> None:
        self.progress.stop()
        self.progress.grid_remove()
        self.test_btn.config(state="normal")
        Messagebox.show_error(message=str(exc))
        self.study_combo.config(state="disabled")
        self.save_btn.config(state="disabled")
        self._verified_keys = None

    def _save(self) -> None:
        if not self._verified_keys:
            return
        study = self.study_var.get()
        self._store.save_secret(f"mednet:{study}", json.dumps(self._verified_keys))
