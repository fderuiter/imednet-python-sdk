from __future__ import annotations

import importlib.resources
import json
import tkinter as tk
from tkinter import Variable, messagebox, ttk
from typing import Any, Dict, Optional, cast

from ..sdk import ImednetSDK
from ..utils.filters import build_filter_string
from ..workflows.credential_validation import CredentialValidationWorkflow
from ..workflows.data_extraction import DataExtractionWorkflow
from ..workflows.job_monitoring import JobMonitoringWorkflow
from ..workflows.query_management import QueryManagementWorkflow
from ..workflows.record_mapper import RecordMapper
from ..workflows.record_update import RecordUpdateWorkflow
from ..workflows.register_subjects import RegisterSubjectsWorkflow
from ..workflows.site_progress import SiteProgressWorkflow
from ..workflows.study_structure import get_study_structure
from ..workflows.subject_data import SubjectDataWorkflow
from .credential_manager import CredentialManager


def _parse_filter_string(value: str) -> Optional[Dict[str, Any]]:
    """Parse a comma separated list of key=value pairs."""
    if not value:
        return None
    result: Dict[str, Any] = {}
    for item in value.split(","):
        if "=" not in item:
            raise ValueError(f"Invalid filter: {item}")
        key, val = item.split("=", 1)
        result[key.strip()] = val.strip()
    return result


CLI_COMMANDS: Dict[str, Dict[str, Any]] = {
    "studies.list": {"params": []},
    "sites.list": {"params": []},
    "subjects.list": {"params": [{"name": "subject_filter", "label": "Subject Filter"}]},
    "workflows.extract-records": {
        "params": [
            {"name": "record_filter", "label": "Record Filter"},
            {"name": "subject_filter", "label": "Subject Filter"},
            {"name": "visit_filter", "label": "Visit Filter"},
        ]
    },
    "workflows.extract-audit-trail": {
        "params": [
            {"name": "start_date", "label": "Start Date"},
            {"name": "end_date", "label": "End Date"},
            {"name": "user_filter", "label": "User Filter"},
        ]
    },
    "workflows.wait-for-job": {
        "params": [
            {"name": "batch_id", "label": "Batch ID"},
            {"name": "timeout", "label": "Timeout", "type": "int", "default": "300"},
            {"name": "poll_interval", "label": "Poll Interval", "type": "int", "default": "5"},
        ]
    },
    "workflows.open-queries": {
        "params": [{"name": "additional_filter", "label": "Additional Filter"}]
    },
    "workflows.site-progress": {"params": []},
    "workflows.record-dataframe": {
        "params": [
            {"name": "visit_key", "label": "Visit Key"},
            {
                "name": "use_labels_as_columns",
                "label": "Use Labels",
                "type": "bool",
                "default": True,
            },
        ]
    },
    "workflows.subject-data": {"params": [{"name": "subject_key", "label": "Subject Key"}]},
    "workflows.validate": {"params": []},
    "workflows.register-subjects": {
        "params": [
            {"name": "subjects_file", "label": "Subjects File"},
            {"name": "email_notify", "label": "Email Notify"},
        ]
    },
    "workflows.submit-record-batch": {
        "params": [
            {"name": "batch_file", "label": "Batch File"},
            {"name": "wait_for_completion", "label": "Wait", "type": "bool"},
        ]
    },
    "workflows.study-structure": {"params": []},
}


with importlib.resources.open_text(__package__, "help.json") as fh:
    HELP_DATA: Dict[str, Any] = json.load(fh)


class ToolTip:
    """Simple tooltip for Tkinter widgets."""

    def __init__(self, widget: tk.Widget, text: str) -> None:
        self.widget = widget
        self.text = text
        self.tipwindow: Optional[tk.Toplevel] = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def update_text(self, text: str) -> None:
        self.text = text

    def show(self, _event: Optional[object] = None) -> None:
        if self.tipwindow or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 10
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = ttk.Label(
            tw,
            text=self.text,
            justify="left",
            background="#ffffe0",
            relief="solid",
            borderwidth=1,
        )
        label.pack(ipadx=1)

    def hide(self, _event: Optional[object] = None) -> None:
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None


def _add_placeholder(entry: ttk.Entry, text: str) -> None:
    def on_focus_in(_event: object) -> None:
        if entry.get() == text:
            entry.delete(0, tk.END)
            entry.configure(foreground="black")

    def on_focus_out(_event: object) -> None:
        if not entry.get():
            entry.insert(0, text)
            entry.configure(foreground="grey")

    entry.insert(0, text)
    entry.configure(foreground="grey")
    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)


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

        ttk.Label(frm, text="Command").grid(row=6, column=0, sticky="w", pady=(10, 0))
        self.command_var = tk.StringVar(value=list(CLI_COMMANDS.keys())[0])
        cb = ttk.Combobox(
            frm,
            textvariable=self.command_var,
            values=list(CLI_COMMANDS.keys()),
            state="readonly",
        )
        cb.grid(row=6, column=1, sticky="ew", pady=(10, 0))
        cb.bind("<<ComboboxSelected>>", self._update_param_fields)
        self.command_tooltip = ToolTip(cb, HELP_DATA[self.command_var.get()]["description"])

        self.params_frame = ttk.Frame(frm)
        self.params_frame.grid(row=7, column=0, columnspan=2, sticky="nsew")

        run_btn = ttk.Button(frm, text="Run", command=self._run_command)
        run_btn.grid(row=8, column=0, columnspan=2, pady=5)

        self.output = tk.Text(frm, height=10, width=60)
        self.output.grid(row=9, column=0, columnspan=2, pady=5)

        frm.columnconfigure(1, weight=1)
        self._update_param_fields()

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

    def _update_param_fields(self, _event: Optional[object] = None) -> None:
        for widget in self.params_frame.winfo_children():
            widget.destroy()
        self.param_vars: Dict[str, Any] = {}
        cmd = self.command_var.get()
        cfg = CLI_COMMANDS[cmd]
        help_cfg = HELP_DATA.get(cmd, {})
        if hasattr(self, "command_tooltip"):
            self.command_tooltip.update_text(help_cfg.get("description", ""))
        for row, field in enumerate(cfg["params"]):
            f_type = field.get("type", "str")
            default = field.get("default", "")
            label = field.get("label", field["name"])
            var: Variable
            if f_type == "bool":
                var = tk.BooleanVar(value=bool(default))
                cb = ttk.Checkbutton(self.params_frame, text=label, variable=var)
                cb.grid(row=row, column=0, sticky="w", columnspan=2)
                hint_lbl = ttk.Label(self.params_frame, text="?")
                hint_lbl.grid(row=row, column=2, sticky="w")
            else:
                ttk.Label(self.params_frame, text=label).grid(row=row, column=0, sticky="w")
                var = tk.StringVar(value=str(default))
                ent = ttk.Entry(self.params_frame, textvariable=var, width=30)
                ent.grid(row=row, column=1, sticky="ew")
                hint = help_cfg.get("params", {}).get(field["name"], {}).get("example")
                if hint:
                    _add_placeholder(ent, str(hint))
                hint_lbl = ttk.Label(self.params_frame, text="?")
                hint_lbl.grid(row=row, column=2, sticky="w")
            param_help = help_cfg.get("params", {}).get(field["name"], {})
            tip_parts = []
            if "type" in param_help:
                tip_parts.append(f"Type: {param_help['type']}")
            if "example" in param_help:
                tip_parts.append(f"Example: {param_help['example']}")
            ToolTip(hint_lbl, "\n".join(tip_parts))
            self.param_vars[field["name"]] = (var, f_type)
        self.params_frame.columnconfigure(1, weight=1)

    def _create_sdk(self) -> ImednetSDK:
        return ImednetSDK(
            api_key=self.api_var.get(),
            security_key=self.sec_var.get(),
            base_url=self.url_var.get() or None,
        )

    def _run_command(self) -> None:
        cmd = self.command_var.get()
        try:
            sdk = self._create_sdk()
            params: Dict[str, Any] = {}
            for name, (var, f_type) in self.param_vars.items():
                val = var.get()
                if f_type == "int" and val:
                    params[name] = int(val)
                elif f_type == "bool":
                    params[name] = bool(val)
                else:
                    params[name] = val or None
            result = self._dispatch_command(sdk, cmd, params)
            self.output.delete("1.0", tk.END)
            self.output.insert(tk.END, str(result))
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Error", str(exc))

    def _dispatch_command(self, sdk: ImednetSDK, cmd: str, params: Dict[str, Any]) -> Any:
        study_key = self.study_var.get()
        if cmd == "studies.list":
            return sdk.studies.list()
        if cmd == "sites.list":
            return sdk.sites.list(study_key)
        if cmd == "subjects.list":
            flt = _parse_filter_string(params.get("subject_filter") or "")
            filt = build_filter_string(cast(Dict[str, Any], flt)) if flt else None
            return sdk.subjects.list(study_key, filter=filt)
        if cmd == "workflows.extract-records":
            rf = _parse_filter_string(params.get("record_filter") or "")
            sf = _parse_filter_string(params.get("subject_filter") or "")
            vf = _parse_filter_string(params.get("visit_filter") or "")
            return DataExtractionWorkflow(sdk).extract_records_by_criteria(
                study_key,
                record_filter=cast(Dict[str, Any], rf) if rf else None,
                subject_filter=cast(Dict[str, Any], sf) if sf else None,
                visit_filter=cast(Dict[str, Any], vf) if vf else None,
            )
        if cmd == "workflows.extract-audit-trail":
            uf = _parse_filter_string(params.get("user_filter") or "")
            return DataExtractionWorkflow(sdk).extract_audit_trail(
                study_key,
                start_date=params.get("start_date"),
                end_date=params.get("end_date"),
                user_filter=cast(Dict[str, Any], uf) if uf else None,
            )
        if cmd == "workflows.wait-for-job":
            return JobMonitoringWorkflow(sdk).wait_for_job(
                study_key,
                params["batch_id"],
                timeout=params.get("timeout", 300),
                poll_interval=params.get("poll_interval", 5),
            )
        if cmd == "workflows.open-queries":
            af = _parse_filter_string(params.get("additional_filter") or "")
            return QueryManagementWorkflow(sdk).get_open_queries(
                study_key, additional_filter=cast(Dict[str, Any], af) if af else None
            )
        if cmd == "workflows.site-progress":
            return SiteProgressWorkflow(sdk).get_site_progress(study_key)
        if cmd == "workflows.record-dataframe":
            df = RecordMapper(sdk).dataframe(
                study_key,
                visit_key=params.get("visit_key"),
                use_labels_as_columns=params.get("use_labels_as_columns", True),
            )
            return df.to_csv(index=False)
        if cmd == "workflows.subject-data":
            return SubjectDataWorkflow(sdk).get_all_subject_data(study_key, params["subject_key"])
        if cmd == "workflows.validate":
            return CredentialValidationWorkflow(sdk).validate(study_key)
        if cmd == "workflows.register-subjects":
            with open(params["subjects_file"], "r", encoding="utf-8") as f:
                data = json.load(f)
            return RegisterSubjectsWorkflow(sdk).register_subjects(
                study_key,
                data,
                email_notify=params.get("email_notify"),
            )
        if cmd == "workflows.submit-record-batch":
            with open(params["batch_file"], "r", encoding="utf-8") as f:
                data = json.load(f)
            return RecordUpdateWorkflow(sdk).submit_record_batch(
                study_key,
                data,
                wait_for_completion=params.get("wait_for_completion", False),
            )
        if cmd == "workflows.study-structure":
            return get_study_structure(sdk, study_key)
        raise ValueError(f"Unknown command: {cmd}")


def run() -> None:
    root = tk.Tk()
    ImednetDesktopApp(root)
    root.mainloop()
