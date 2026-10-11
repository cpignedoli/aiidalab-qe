"""Remember plugin activation that still requires an AiiDA daemon restart."""

from pathlib import Path

from packaging.utils import canonicalize_name

from aiida.manage.configuration import get_profile
from aiida.manage.configuration.settings import AiiDAConfigDir


def _pending_restarts_dir() -> Path:
    return AiiDAConfigDir.get() / "aiidalab-qe" / "pending-plugin-restarts"


def _restart_marker(plugin_name: str) -> Path:
    profile = get_profile()
    profile_id = profile.uuid if profile else "default"
    return _pending_restarts_dir() / profile_id / canonicalize_name(plugin_name)


def get_restart_failure(plugin_name: str) -> str | None:
    """Return an activation warning until the required restart succeeds."""
    if _restart_marker(plugin_name).exists():
        return "Plugin activation requires a successful AiiDA daemon restart."
    return None


def set_restart_pending(plugin_name: str) -> None:
    """Record the required restart before attempting it."""
    marker = _restart_marker(plugin_name)
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.touch()


def clear_restart_pending(plugin_name: str) -> None:
    """A successful restart activates all pending plugins in this profile."""
    for marker in _restart_marker(plugin_name).parent.glob("*"):
        marker.unlink(missing_ok=True)
