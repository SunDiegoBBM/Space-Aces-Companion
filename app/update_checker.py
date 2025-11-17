
import webbrowser
from typing import Optional, Tuple

import requests
from PySide6.QtWidgets import QMessageBox, QWidget

# Configure these for your repository
REPO_OWNER = "SunDiegoBBM"
REPO_NAME = "Space-Aces-Companion"

GITHUB_API_LATEST = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/latest"
GITHUB_RELEASES_BASE = f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases"


def _parse_version(version: str) -> Tuple[int, int, int]:
 
    if not version:
        return 0, 0, 0

    v = version.strip()
    if v.lower().startswith("v"):
        v = v[1:]

    parts = v.split(".")
    nums = []
    for p in parts[:3]:
        try:
            nums.append(int(p))
        except ValueError:
            nums.append(0)

    while len(nums) < 3:
        nums.append(0)

    return tuple(nums[:3])


def _fetch_latest_version() -> Optional[tuple]:
    """
    Fetch the latest release tag from GitHub.

    Returns:
        (tag_name, clean_version) or None on error.
        Example: ("v0.4", "0.4")
    """
    try:
        response = requests.get(GITHUB_API_LATEST, timeout=3)
        response.raise_for_status()
        data = response.json()

        tag = data.get("tag_name") or ""
        tag = str(tag).strip()
        if not tag:
            return None

        clean = tag[1:] if tag.lower().startswith("v") else tag
        return tag, clean
    except Exception:
        # Any error: just skip update checking silently
        return None


def check_for_update(parent: Optional[QWidget] = None, local_version: str = "0.3.0") -> None:
    """
    Check GitHub for a newer release and show a dialog if one is available.

    This is designed to be called once shortly after the main window is shown.
    It fails silently if GitHub is not reachable or something goes wrong.
    """
    result = _fetch_latest_version()
    if not result:
        return

    remote_tag, remote_version = result

    local_tuple = _parse_version(local_version)
    remote_tuple = _parse_version(remote_version)

    # If remote <= local, nothing to do
    if remote_tuple <= local_tuple:
        return

    # There is a newer version
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Icon.Information)
    msg.setWindowTitle("Update available")
    msg.setText(
        "A new version of Space Aces Companion is available.\n\n"
        f"Installed version: {local_version}\n"
        f"Latest version: {remote_version}\n\n"
        "Do you want to open the GitHub releases page?"
    )

    open_button = msg.addButton("Open GitHub", QMessageBox.ButtonRole.AcceptRole)
    later_button = msg.addButton("Later", QMessageBox.ButtonRole.RejectRole)

    msg.exec()

    if msg.clickedButton() is open_button:
        # Open the specific tag if possible, otherwise the releases overview
        if remote_tag:
            url = f"{GITHUB_RELEASES_BASE}/tag/{remote_tag}"
        else:
            url = GITHUB_RELEASES_BASE

        webbrowser.open(url)
    else:
        # User chose "Later" – no action
        return
