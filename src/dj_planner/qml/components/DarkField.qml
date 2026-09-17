
import QtQuick
import QtQuick.Controls
import ".."

TextField {
    id: control
    implicitHeight: 40
    leftPadding: 12
    rightPadding: 12

    color: Theme.text
    placeholderTextColor: Theme.muted2
    selectionColor: Theme.purple
    selectedTextColor: Theme.text
    font.pixelSize: 14

    background: Rectangle {
        radius: Theme.smallRadius
        color: Theme.card2
        border.width: control.activeFocus ? 2 : 1
        border.color: control.activeFocus ? Theme.purple : Theme.border
    }
}
