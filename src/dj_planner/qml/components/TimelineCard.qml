
import QtQuick
import QtQuick.Controls
import ".."

Item {
    id: root
    objectName: "timelineCard_" + slotIndex

    property string dj: ""
    property string startTime: ""
    property string endTime: ""
    property int duration: 0
    property real value: 0
    property bool locked: false
    property int slotIndex: -1

    signal dragFinished(int sourceIndex, real sceneCenterX)
    signal lockRequested(int slotIndex)

    width: 190
    height: 196

    Rectangle {
        id: visualCard
        x: 0
        y: 0
        width: root.width
        height: root.height
        radius: 14
        color: Theme.card
        border.width: root.locked ? 2 : 1
        border.color: root.locked ? Theme.amber : Theme.border
        z: dragArea.drag.active ? 1000 : 1

        Behavior on scale {
            NumberAnimation { duration: 110 }
        }
        scale: dragArea.drag.active ? 1.035 : (hoverArea.containsMouse ? 1.015 : 1.0)

        Rectangle {
            width: parent.width
            height: 7
            anchors.top: parent.top
            radius: 14
            color: Theme.purple
        }

        Rectangle {
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            height: 1
            color: Theme.border
        }

        Column {
            anchors.fill: parent
            anchors.margins: 16
            anchors.topMargin: 23
            spacing: 9

            Text {
                width: parent.width
                text: root.dj
                color: Theme.text
                font.pixelSize: 19
                font.bold: true
                elide: Text.ElideRight
            }

            Text {
                text: root.startTime + "  →  " + root.endTime
                color: Theme.text
                font.pixelSize: 14
                font.bold: true
            }

            Text {
                text: root.duration + " min"
                color: Theme.muted
                font.pixelSize: 13
            }

            Rectangle {
                width: parent.width
                height: 32
                radius: 8
                color: Theme.purpleDark

                Text {
                    anchors.centerIn: parent
                    text: "Value  " + Number(root.value).toFixed(2)
                    color: Theme.purpleSoft
                    font.pixelSize: 13
                    font.bold: true
                }
            }

            Text {
                visible: root.locked
                text: "●  LOCKED"
                color: Theme.amber
                font.pixelSize: 11
                font.bold: true
            }
        }

        MouseArea {
            id: hoverArea
            anchors.fill: parent
            hoverEnabled: true
            acceptedButtons: Qt.NoButton
        }

        MouseArea {
            id: dragArea
            anchors.fill: parent
            drag.target: visualCard
            drag.axis: Drag.XAxis
            drag.threshold: 6
            cursorShape: drag.active ? Qt.ClosedHandCursor : Qt.OpenHandCursor

            onDoubleClicked: root.lockRequested(root.slotIndex)

            preventStealing: true

            onReleased: {
                // Map the dragged card center to scene coordinates before snapping back.
                var p = visualCard.mapToItem(null, visualCard.width / 2, visualCard.height / 2)
                var sourceIndex = root.slotIndex
                var moved = drag.active
                visualCard.x = 0
                visualCard.y = 0
                if (moved)
                    root.dragFinished(sourceIndex, p.x)
            }
        }
    }
}
