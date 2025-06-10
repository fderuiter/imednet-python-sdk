from __future__ import annotations

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
from .credential_manager import CredentialManager, ProfileManager


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


class ImednetDesktopApp:
    """Basic Tkinter UI for interacting with iMednet workflows."""

    def __init__(
        self,
        master: tk.Tk,
        credential_manager: Optional[CredentialManager] = None,
        profile_manager: Optional[ProfileManager] = None,
    ) -> None:
        self.master = master
        self.master.title("iMednet SDK")
        self.cred_mgr = credential_manager or CredentialManager()
        self.profile_mgr = profile_manager or ProfileManager()
        self._build()
        self._load_saved()

    def _build(self) -> None:
        frm = ttk.Frame(self.master, padding="10")
        frm.grid(row=0, column=0, sticky="nsew")

        ttk.Label(frm, text="Profile").grid(row=0, column=0, sticky="w")
        self.profile_var = tk.StringVar()
        self.profile_combo = ttk.Combobox(
            frm,
            textvariable=self.profile_var,
            state="readonly",
            values=self.profile_mgr.list_profiles(),
        )
        self.profile_combo.grid(row=0, column=1, sticky="ew")
        self.profile_combo.bind("<<ComboboxSelected>>", self._on_profile_select)

        row_base = 1
        ttk.Label(frm, text="API Key").grid(row=row_base, column=0, sticky="w")
        self.api_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.api_var, width=40).grid(
            row=row_base, column=1, sticky="ew"
        )

        ttk.Label(frm, text="Security Key").grid(row=row_base + 1, column=0, sticky="w")
        self.sec_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.sec_var, width=40, show="*").grid(
            row=row_base + 1, column=1, sticky="ew"
        )

        ttk.Label(frm, text="Base URL").grid(row=row_base + 2, column=0, sticky="w")
        self.url_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.url_var, width=40).grid(
            row=row_base + 2, column=1, sticky="ew"
        )

        ttk.Label(frm, text="Study Key").grid(row=row_base + 3, column=0, sticky="w")
        self.study_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.study_var, width=40).grid(
            row=row_base + 3, column=1, sticky="ew"
        )

        save_btn = ttk.Button(frm, text="Save Profile", command=self._save_profile)
        save_btn.grid(row=row_base + 4, column=0, pady=(5, 0))
        del_btn = ttk.Button(frm, text="Delete", command=self._delete_profile)
        del_btn.grid(row=row_base + 4, column=1, pady=(5, 0), sticky="e")

        ttk.Separator(frm).grid(row=row_base + 5, column=0, columnspan=2, sticky="ew")

        ttk.Label(frm, text="Command").grid(row=row_base + 6, column=0, sticky="w", pady=(10, 0))
        self.command_var = tk.StringVar(value=list(CLI_COMMANDS.keys())[0])
        cb = ttk.Combobox(
            frm,
            textvariable=self.command_var,
            values=list(CLI_COMMANDS.keys()),
            state="readonly",
        )
        cb.grid(row=row_base + 6, column=1, sticky="ew", pady=(10, 0))
        cb.bind("<<ComboboxSelected>>", self._update_param_fields)

        self.params_frame = ttk.Frame(frm)
        self.params_frame.grid(row=row_base + 7, column=0, columnspan=2, sticky="nsew")

        run_btn = ttk.Button(frm, text="Run", command=self._run_command)
        run_btn.grid(row=row_base + 8, column=0, columnspan=2, pady=5)

        self.output = tk.Text(frm, height=10, width=60)
        self.output.grid(row=row_base + 9, column=0, columnspan=2, pady=5)

        frm.columnconfigure(1, weight=1)
        self._update_param_fields()

    def _load_saved(self) -> None:
        profiles = self.profile_mgr.list_profiles()
        self.profile_combo.configure(values=profiles)
        current = self.profile_mgr.current()
        if current:
            self.profile_var.set(current)
            data = self.profile_mgr.load_profile(current)
        else:
            data = None
        if data:
            self.api_var.set(data.get("api_key") or "")
            self.sec_var.set(data.get("security_key") or "")
            url = data.get("base_url")
            if url is not None:
                self.url_var.set(url)
            study_key = data.get("study_key")
            if study_key is not None:
                self.study_var.set(study_key)

    def _save_profile(self) -> None:
        name = self.profile_var.get() or "default"
        self.profile_mgr.save_profile(
            name,
            self.api_var.get(),
            self.sec_var.get(),
            self.url_var.get() or None,
            self.study_var.get() or None,
        )
        self.profile_mgr.set_current(name)
        messagebox.showinfo("Saved", "Profile saved successfully.")
        self._load_saved()

    def _delete_profile(self) -> None:
        name = self.profile_var.get()
        if not name:
            return
        self.profile_mgr.delete_profile(name)
        self.profile_var.set("")
        self._load_saved()

    def _on_profile_select(self, _event: Optional[object] = None) -> None:
        name = self.profile_var.get()
        if not name:
            return
        self.profile_mgr.set_current(name)
        data = self.profile_mgr.load_profile(name)
        if not data:
            return
        self.api_var.set(data.get("api_key") or "")
        self.sec_var.set(data.get("security_key") or "")
        self.url_var.set(data.get("base_url") or "")
        self.study_var.set(data.get("study_key") or "")

    def _update_param_fields(self, _event: Optional[object] = None) -> None:
        for widget in self.params_frame.winfo_children():
            widget.destroy()
        self.param_vars: Dict[str, Any] = {}
        cfg = CLI_COMMANDS[self.command_var.get()]
        for row, field in enumerate(cfg["params"]):
            f_type = field.get("type", "str")
            default = field.get("default", "")
            label = field.get("label", field["name"])
            var: Variable
            if f_type == "bool":
                var = tk.BooleanVar(value=bool(default))
                cb = ttk.Checkbutton(self.params_frame, text=label, variable=var)
                cb.grid(row=row, column=0, sticky="w", columnspan=2)
            else:
                ttk.Label(self.params_frame, text=label).grid(row=row, column=0, sticky="w")
                var = tk.StringVar(value=str(default))
                ttk.Entry(self.params_frame, textvariable=var, width=30).grid(
                    row=row, column=1, sticky="ew"
                )
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
