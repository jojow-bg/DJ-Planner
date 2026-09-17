
import QtQuick
import QtQuick.Controls
import ".."

ScrollBar {
    id: control
    implicitWidth: 8

    contentItem: Rectangle {
        implicitWidth: 6
        radius: 3
        color: control.pressed ? Theme.purple : Theme.borderSoft
        opacity: control.size < 1.0 ? 0.9 : 0.0
    }

    background: Rectangle {
        color: "transparent"
    }
}
