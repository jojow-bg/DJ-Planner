"""Capture the real QML interface using isolated fictional data."""

import os
from pathlib import Path
from tempfile import TemporaryDirectory

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("QT_QUICK_BACKEND", "software")

from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

import dj_planner
from dj_planner.bridge import DJPlannerBridge
from dj_planner.demo import seed_demo


def main():
    QQuickStyle.setStyle("Basic")
    app = QApplication([])
    output = Path(__file__).resolve().parents[1] / "docs" / "images"
    output.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory() as temp:
        path = Path(temp) / "demo.sqlite3"
        seed_demo(path)
        bridge = DJPlannerBridge(path)
        bridge.generate()
        engine = QQmlApplicationEngine()
        engine.rootContext().setContextProperty("planner", bridge)
        engine.load(str(Path(dj_planner.__file__).parent / "qml" / "Main.qml"))
        if not engine.rootObjects():
            raise RuntimeError("QML did not load")
        window = engine.rootObjects()[0]
        for tab, name in [
            (0, "planning"),
            (1, "djs"),
            (2, "bands"),
            (3, "history"),
            (4, "fairness"),
        ]:
            bridge.selectedTab = tab
            QTest.qWait(500)
            app.processEvents()
            window.update()
            QTest.qWait(100)
            image = window.grabWindow()
            if image.isNull() or not image.save(str(output / f"{name}.png")):
                raise RuntimeError(f"Could not capture {name}")
        window.close()
        del engine
        bridge.store.close()


if __name__ == "__main__":
    main()
