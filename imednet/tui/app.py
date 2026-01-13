from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.message import Message
from textual.screen import Screen
from textual.timer import Timer
from textual.widgets import (
    DataTable,
    Label,
    ListItem,
    ListView,
    Log,
    Static,
    TabbedContent,
    TabPane,
)

if TYPE_CHECKING:
    from ..sdk import ImednetSDK

# =============================================================================
# LOGGING HANDLER
# =============================================================================


class TextualLogHandler(logging.Handler):
    """A logging handler that writes to a Textual Log widget."""

    def __init__(self, log_widget: Log):
        super().__init__()
        self.log_widget = log_widget

    def emit(self, record: logging.LogRecord) -> None:
        msg = self.format(record)
        # Use call_after_refresh to ensure thread safety when logging from background threads
        self.log_widget.write_line(msg)


# =============================================================================
# WIDGETS
# =============================================================================


class StudyList(ListView):
    """A list of studies."""

    class Selected(Message):
        """Study selected message."""

        def __init__(self, study_key: str, study_name: str) -> None:
            self.study_key = study_key
            self.study_name = study_name
            super().__init__()

    def __init__(self, sdk: ImednetSDK, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.sdk = sdk
        self.loaded = False

    async def on_mount(self) -> None:
        if not self.loaded:
            self.loading = True
            try:
                studies = await self.sdk.studies.async_list()
                items = []
                for study in studies:
                    # Using study_key as the ID, but displaying name and key
                    # study.name might be None, so fallback
                    name = getattr(study, "name", "Unknown Study")
                    key = getattr(study, "study_key", "no-key")
                    label = f"{name} ({key})"
                    items.append(ListItem(Label(label), id=f"study-{key}"))

                self.extend(items)
                self.loaded = True
            except Exception as e:
                self.app.notify(f"Error loading studies: {e}", severity="error")
            finally:
                self.loading = False

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.item and event.item.id:
            # Extract study key from ID "study-<key>"
            study_key = event.item.id.replace("study-", "")
            # Get label text as name
            label_widget = event.item.query_one(Label)
            study_name = str(label_widget.renderable)
            self.post_message(self.Selected(study_key, study_name))


class SiteList(ListView):
    """A list of sites for a specific study."""

    class Selected(Message):
        """Site selected message."""

        def __init__(self, site_id: str, site_name: str) -> None:
            self.site_id = site_id
            self.site_name = site_name
            super().__init__()

    def __init__(self, sdk: ImednetSDK, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.sdk = sdk
        self.current_study_key: str | None = None

    async def load_sites(self, study_key: str) -> None:
        self.current_study_key = study_key
        self.clear()
        self.loading = True
        try:
            sites = await self.sdk.sites.async_list(study_key)
            items = []
            for site in sites:
                site_id = getattr(site, "site_id", "no-id")
                name = getattr(site, "site_name", "Unknown Site")
                label = f"{name} ({site_id})"
                items.append(ListItem(Label(label), id=f"site-{site_id}"))
            self.extend(items)
        except Exception as e:
            self.app.notify(f"Error loading sites: {e}", severity="error")
        finally:
            self.loading = False

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.item and event.item.id:
            site_id = event.item.id.replace("site-", "")
            label_widget = event.item.query_one(Label)
            site_name = str(label_widget.renderable)
            self.post_message(self.Selected(site_id, site_name))


class SubjectTable(DataTable):
    """A table of subjects."""

    def __init__(self, sdk: ImednetSDK, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.sdk = sdk
        self.cursor_type = "row"
        self.add_columns("Subject ID", "Status", "Created")

    async def load_subjects(self, study_key: str, site_id: str) -> None:
        self.clear()
        self.loading = True
        try:
            subjects = await self.sdk.subjects.async_list(study_key)

            # Note: Subjects endpoint often returns `site_id` in the response.
            rows = []
            for sub in subjects:
                s_site_id = str(getattr(sub, "site_id", ""))
                # Strict string comparison to filter by site
                if s_site_id == str(site_id):
                    sub_id = getattr(sub, "subject_id", "-")
                    status = getattr(sub, "status", "-")
                    created = str(getattr(sub, "date_created", "-"))
                    rows.append((sub_id, status, created))

            self.add_rows(rows)
        except Exception as e:
            self.app.notify(f"Error loading subjects: {e}", severity="error")
        finally:
            self.loading = False


class JobMonitor(Static):
    """A widget that polls jobs."""

    DEFAULT_CSS = """
    JobMonitor {
        height: 100%;
        background: $surface;
        border: solid $primary;
        overflow-y: auto;
    }
    """

    def __init__(self, sdk: ImednetSDK, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.sdk = sdk
        self.timer: Timer | None = None
        self.current_study_key: str | None = None

    def on_mount(self) -> None:
        self.update("Job Monitor: Select a study to view jobs.")
        self.timer = self.set_interval(10.0, self.refresh_jobs, pause=True)

    def set_study(self, study_key: str) -> None:
        self.current_study_key = study_key
        self.update(f"Job Monitor: Loading jobs for study {study_key}...")
        if self.timer:
            self.timer.resume()
        self.run_worker(self.refresh_jobs())

    async def refresh_jobs(self) -> None:
        if not self.current_study_key:
            self.update("Job Monitor: Select a study to view jobs.")
            if self.timer:
                self.timer.pause()
            return

        try:
            # Polling jobs for the selected study
            jobs = await self.sdk.jobs.async_list(self.current_study_key)
            # Sort by date descending?
            # Assuming jobs is a list of models.

            lines = []
            lines.append(f"[bold]Active Jobs ({len(jobs)})[/bold]")
            for job in jobs[:10]:  # Show last 10
                job_type = getattr(job, "job_type", "Unknown")
                status = getattr(job, "state", getattr(job, "status", "Unknown"))
                created = getattr(job, "date_created", "")
                color = (
                    "green"
                    if status in ("Completed", "Success")
                    else "yellow"
                    if status in ("Processing", "Pending")
                    else "red"
                )
                lines.append(f"[{color}]{status}[/{color}] - {job_type} ({created})")

            self.update("\n".join(lines))
        except Exception as e:
            self.update(f"[red]Error fetching jobs: {e}[/red]")


class LogViewer(Log):
    """A log viewer widget."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.border_title = "Logs"


# =============================================================================
# SCREENS
# =============================================================================


class DashboardScreen(Screen):
    """The main dashboard screen."""

    CSS = """
    DashboardScreen {
        layout: grid;
        grid-size: 3 2;
        grid-columns: 1fr 1fr 2fr;
        grid-rows: 3fr 1fr;
    }

    #studies-box {
        grid-column: 1;
        grid-row: 1;
        border: solid green;
        border-title: Studies;
    }

    #sites-box {
        grid-column: 2;
        grid-row: 1;
        border: solid blue;
        border-title: Sites;
    }

    #subjects-box {
        grid-column: 3;
        grid-row: 1;
        border: solid magenta;
        border-title: Subjects;
    }

    #bottom-pane {
        grid-column: 1 / 4;
        grid-row: 2;
        border-top: solid white;
    }
    """

    def __init__(self, sdk: ImednetSDK, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.sdk = sdk
        self.log_viewer = LogViewer()

    def compose(self) -> ComposeResult:
        yield Container(StudyList(self.sdk, id="study_list"), id="studies-box")
        yield Container(SiteList(self.sdk, id="site_list"), id="sites-box")
        yield Container(SubjectTable(self.sdk, id="subject_table"), id="subjects-box")

        with TabbedContent(id="bottom-pane"):
            with TabPane("Jobs"):
                yield JobMonitor(self.sdk)
            with TabPane("Logs"):
                yield self.log_viewer

    def on_study_list_selected(self, message: StudyList.Selected) -> None:
        self.log_viewer.write_line(f"Selected Study: {message.study_name}")
        site_list = self.query_one(SiteList)
        self.run_worker(site_list.load_sites(message.study_key))
        # Clear subjects
        self.query_one(SubjectTable).clear()

        # Update Job Monitor
        job_monitor = self.query_one(JobMonitor)
        job_monitor.set_study(message.study_key)

    def on_site_list_selected(self, message: SiteList.Selected) -> None:
        self.log_viewer.write_line(f"Selected Site: {message.site_name}")
        site_list = self.query_one(SiteList)
        # We need the study key from the site list or store it
        study_key = site_list.current_study_key
        if study_key:
            subject_table = self.query_one(SubjectTable)
            self.run_worker(subject_table.load_subjects(study_key, message.site_id))


# =============================================================================
# APP
# =============================================================================


class ImednetTuiApp(App):
    """The iMednet TUI Application."""

    CSS = """
    Screen {
        background: $surface;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("d", "toggle_dark", "Toggle Dark Mode"),
    ]

    def __init__(self, sdk: ImednetSDK, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.sdk = sdk

    def on_mount(self) -> None:
        self.push_screen(DashboardScreen(self.sdk))
        self.title = "iMednet Mission Control"
        # Set sub-title to environment
        # Use hidden attribute or public if available. SDK doesn't expose base_url publicly.
        base_url = getattr(self.sdk, "_base_url", "Unknown")
        self.sub_title = f"Env: {base_url}"

        # Attach logging handler
        # We need to find the DashboardScreen to get the LogViewer
        dashboard = self.query_one(DashboardScreen)
        log_widget = dashboard.log_viewer

        handler = TextualLogHandler(log_widget)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)

        # Attach to imednet logger
        logger = logging.getLogger("imednet")
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)

        # Also attach to root for broader capture if needed, but imednet should be enough
        # Note: If json_logging is active, it might interfere, but adding a handler usually works.

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark  # type: ignore


def run_tui(sdk: ImednetSDK) -> None:
    """Run the TUI application."""
    app = ImednetTuiApp(sdk)
    app.run()
