from pathlib import Path

from PySide6.QtCore import QPointF, Qt
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtTest import QTest

import dj_planner
from dj_planner.bridge import DJPlannerBridge
from dj_planner.demo import seed_demo


def find_item(root, name):
    if root.objectName() == name:
        return root
    for child in root.childItems():
        found = find_item(child, name)
        if found is not None:
            return found
    return None


def test_qml_pages_and_real_drag_gesture(app, tmp_path):
    db = tmp_path / "demo.sqlite3"
    seed_demo(db)
    bridge = DJPlannerBridge(db)
    bridge.generate()
    engine = QQmlApplicationEngine()
    warnings = []
    engine.warnings.connect(lambda items: warnings.extend(str(item) for item in items))
    engine.rootContext().setContextProperty("planner", bridge)
    engine.load(str(Path(dj_planner.__file__).parent / "qml" / "Main.qml"))
    assert engine.rootObjects(), warnings
    window = engine.rootObjects()[0]
    try:
        for tab in range(5):
            bridge.selectedTab = tab
            QTest.qWait(50)
            app.processEvents()
        bridge.selectedTab = 0
        QTest.qWait(100)
        first = find_item(window.contentItem(), "timelineCard_0")
        second = find_item(window.contentItem(), "timelineCard_1")
        assert first is not None and second is not None
        source = first.mapToScene(QPointF(80, 80)).toPoint()
        target = second.mapToScene(QPointF(80, 80)).toPoint()
        before = [r.dj for r in bridge.schedule]
        QTest.mousePress(window, Qt.LeftButton, Qt.NoModifier, source)
        for step in range(1, 11):
            point = source + (target - source) * (step / 10)
            QTest.mouseMove(window, point, 20)
        QTest.mouseRelease(window, Qt.LeftButton, Qt.NoModifier, target)
        QTest.qWait(100)
        assert [r.dj for r in bridge.schedule][:2] == [before[1], before[0]]
        QTest.mouseDClick(window, Qt.LeftButton, Qt.NoModifier, source)
        QTest.qWait(50)
        assert bridge.schedule[0].locked
        assert not warnings, warnings
    finally:
        window.close()
        del engine
        bridge.store.close()
