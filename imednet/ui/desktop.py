from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional

from ..sdk import ImednetSDK
from .credential_manager import CredentialManager


class ImednetDesktopApp:
    """Basic Tkinter UI for interacting with iMednet workflows."""

    def __init__(
        self, master: tk.Tk, credential_manager: Optional[CredentialManager] = None
    ) -> None:
        self.master = master
        self.master.title("iMednet SDK")
        self.cred_mgr = credential_manager or CredentialManager()
        self._build()
        self._load_saved()

    def _build(self) -> None:
        frm = ttk.Frame(self.master, padding="10")
        frm.grid(row=0, column=0, sticky="nsew")

        ttk.Label(frm, text="API Key").grid(row=0, column=0, sticky="w")
        self.api_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.api_var, width=40).grid(row=0, column=1, sticky="ew")

        ttk.Label(frm, text="Security Key").grid(row=1, column=0, sticky="w")
        self.sec_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.sec_var, width=40, show="*").grid(
            row=1, column=1, sticky="ew"
        )

        ttk.Label(frm, text="Base URL").grid(row=2, column=0, sticky="w")
        self.url_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.url_var, width=40).grid(row=2, column=1, sticky="ew")

        ttk.Label(frm, text="Study Key").grid(row=3, column=0, sticky="w")
        self.study_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.study_var, width=40).grid(row=3, column=1, sticky="ew")

        save_btn = ttk.Button(frm, text="Save Credentials", command=self._save_credentials)
        save_btn.grid(row=4, column=0, columnspan=2, pady=(5, 10))

        ttk.Separator(frm).grid(row=5, column=0, columnspan=2, sticky="ew")

        ttk.Label(frm, text="Workflows").grid(row=6, column=0, sticky="w", pady=(10, 0))
        self.workflow_var = tk.StringVar(value="data_extraction")
        ttk.Combobox(
            frm,
            textvariable=self.workflow_var,
            values=["data_extraction"],
            state="readonly",
        ).grid(row=6, column=1, sticky="ew", pady=(10, 0))

        run_btn = ttk.Button(frm, text="Run", command=self._run_workflow)
        run_btn.grid(row=7, column=0, columnspan=2, pady=5)

        self.output = tk.Text(frm, height=10, width=60)
        self.output.grid(row=8, column=0, columnspan=2, pady=5)

        frm.columnconfigure(1, weight=1)

    def _load_saved(self) -> None:
        data = self.cred_mgr.load()
        if not data:
            return
        self.api_var.set(data.get("api_key") or "")
        self.sec_var.set(data.get("security_key") or "")
        url = data.get("base_url")
        if url is not None:
            self.url_var.set(url)
        study_key = data.get("study_key")
        if study_key is not None:
            self.study_var.set(study_key)

    def _save_credentials(self) -> None:
        self.cred_mgr.save(
            self.api_var.get(),
            self.sec_var.get(),
            self.url_var.get() or None,
            self.study_var.get() or None,
        )
        messagebox.showinfo("Saved", "Credentials saved successfully.")

    def _run_workflow(self) -> None:
        workflow_name = self.workflow_var.get()
        try:
            sdk = ImednetSDK(
                api_key=self.api_var.get(),
                security_key=self.sec_var.get(),
                base_url=self.url_var.get() or None,
            )
            if workflow_name == "data_extraction":
                result = sdk.workflows.data_extraction.extract_records_by_criteria(
                    self.study_var.get()
                )
                self.output.delete("1.0", tk.END)
                self.output.insert(tk.END, str(result))
            else:
                messagebox.showerror("Error", f"Unknown workflow: {workflow_name}")
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Error", str(exc))


def run() -> None:
    root = tk.Tk()
    ImednetDesktopApp(root)
    root.mainloop()
