from __future__ import annotations

import argparse
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtWidgets import QApplication

from .bridge import DJPlannerBridge
from .demo import seed_demo


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="DJ Planner desktop application")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--demo", action="store_true", help="Open an isolated fictional demo")
    group.add_argument("--database", type=Path, help="Use a specific SQLite database")
    args = parser.parse_args(argv)

    QQuickStyle.setStyle("Basic")
    app = QApplication([sys.argv[0]])
    app.setApplicationName("DJ Planner")
    app.setOrganizationName("DJPlanner")
    demo_dir = TemporaryDirectory(prefix="dj-planner-demo-") if args.demo else None
    db_path = Path(demo_dir.name) / "demo.sqlite3" if demo_dir else args.database
    if args.demo:
        seed_demo(db_path)

    bridge = DJPlannerBridge(db_path)
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("planner", bridge)
    engine.load(str(Path(__file__).parent / "qml" / "Main.qml"))
    if args.demo:
        bridge.generate()
    try:
        return app.exec() if engine.rootObjects() else 1
    finally:
        bridge.saveState()
        del engine
        bridge.store.close()
        if demo_dir:
            demo_dir.cleanup()
