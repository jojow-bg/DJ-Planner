"""Build on the target OS after installing .[packaging]."""

import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
subprocess.run(
    [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        "--name",
        "DJPlanner",
        "--collect-data",
        "dj_planner",
        str(root / "scripts" / "launcher.py"),
    ],
    cwd=root,
    check=True,
)
