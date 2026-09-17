
import QtQuick
import QtQuick.Controls
import ".."

Button {
    id: control

    property color normalColor: Theme.purple
    property color hoverColor: Theme.purpleHover
    property color textColor: Theme.text
    property color borderColor: normalColor === Theme.card2 ? Theme.border : normalColor

    implicitHeight: 42
    leftPadding: 16
    rightPadding: 16

    contentItem: Text {
        text: control.text
        color: control.textColor
        font.pixelSize: 13
        font.bold: true
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        elide: Text.ElideRight
    }

    background: Rectangle {
        radius: Theme.smallRadius
        color: !control.enabled
               ? Theme.border
               : (control.hovered ? control.hoverColor : control.normalColor)
        border.width: 1
        border.color: control.borderColor
        opacity: control.enabled ? 1.0 : 0.55
    }
}
