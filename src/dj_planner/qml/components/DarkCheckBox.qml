
import QtQuick
import QtQuick.Controls
import ".."

CheckBox {
    id: control
    implicitWidth: 26
    implicitHeight: 26
    spacing: 0

    indicator: Rectangle {
        implicitWidth: 22
        implicitHeight: 22
        x: (control.width - width) / 2
        y: (control.height - height) / 2
        radius: 6
        color: control.checked ? Theme.purple : Theme.card2
        border.width: control.activeFocus ? 2 : 1
        border.color: control.checked ? Theme.purpleSoft : Theme.borderSoft

        Text {
            anchors.centerIn: parent
            text: "✓"
            visible: control.checked
            color: Theme.text
            font.pixelSize: 14
            font.bold: true
        }
    }

    contentItem: Item {}
}
