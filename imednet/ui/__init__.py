"""Desktop UI for the iMednet SDK."""

from .credential_manager import CredentialManager
from .desktop import ImednetDesktopApp, run
from .profile_manager import ProfileManager
from .template_manager import TemplateManager

__all__ = [
    "CredentialManager",
    "ImednetDesktopApp",
    "TemplateManager",
    "ProfileManager",
    "run",
]
