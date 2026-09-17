import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("QT_QUICK_BACKEND", "software")

import pytest
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def app():
    QQuickStyle.setStyle("Basic")
    return QApplication.instance() or QApplication([])
