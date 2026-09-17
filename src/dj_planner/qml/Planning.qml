
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "components"

Item {
    anchors.fill: parent

    RowLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 18

        Card {
            Layout.preferredWidth: 405
            Layout.fillHeight: true

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 18
                spacing: 14

                RowLayout {
                    Layout.fillWidth: true

                    Text {
                        text: "Event"
                        color: Theme.text
                        font.pixelSize: 21
                        font.bold: true
                        Layout.fillWidth: true
                    }

                    Text {
                        text: "Settings"
                        color: Theme.muted
                        font.pixelSize: 11
                    }
                }

                GridLayout {
                    columns: 2
                    columnSpacing: 10
                    rowSpacing: 9
                    Layout.fillWidth: true

                    Text { text: "Name"; color: Theme.muted }
                    DarkField {
                        Layout.fillWidth: true
                        text: planner.partyName
                        onEditingFinished: planner.partyName = text
                    }

                    Text { text: "Date"; color: Theme.muted }
                    DarkField {
                        Layout.fillWidth: true
                        text: planner.partyDate
                        onEditingFinished: planner.partyDate = text
                    }

                    Text { text: "Start"; color: Theme.muted }
                    DarkField {
                        Layout.fillWidth: true
                        text: planner.partyStart
                        onEditingFinished: planner.partyStart = text
                    }

                    Text { text: "End"; color: Theme.muted }
                    DarkField {
                        Layout.fillWidth: true
                        text: planner.partyEnd
                        onEditingFinished: planner.partyEnd = text
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    height: 1
                    color: Theme.border
                }

                RowLayout {
                    Layout.fillWidth: true

                    Text {
                        text: "Availability"
                        color: Theme.text
                        font.pixelSize: 17
                        font.bold: true
                        Layout.fillWidth: true
                    }

                    PrimaryButton {
                        text: "Import Excel"
                        normalColor: Theme.card2
                        hoverColor: Theme.cardHover
                        onClicked: planner.importExcel()
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 6

                    Text {
                        text: ""
                        Layout.preferredWidth: 26
                    }

                    Text {
                        text: "DJ"
                        color: Theme.muted
                        font.pixelSize: 11
                        Layout.preferredWidth: 104
                    }

                    Text {
                        text: "From"
                        color: Theme.muted
                        font.pixelSize: 11
                        Layout.preferredWidth: 78
                        horizontalAlignment: Text.AlignHCenter
                    }

                    Text {
                        text: "Until"
                        color: Theme.muted
                        font.pixelSize: 11
                        Layout.preferredWidth: 78
                        horizontalAlignment: Text.AlignHCenter
                    }
                }

                ListView {
                    id: djList
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    clip: true
                    spacing: 7
                    model: planner.djModel

                    ScrollBar.vertical: DarkScrollBar {}

                    delegate: Rectangle {
                        required property string name
                        required property bool present
                        required property string minTime
                        required property string maxTime
                        required property int index

                        width: djList.width
                        height: 48
                        radius: 9
                        color: Theme.card2
                        border.width: 1
                        border.color: present ? Theme.purpleDark : Theme.border

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 7
                            spacing: 6

                            DarkCheckBox {
                                id: presentBox
                                checked: present
                                Layout.preferredWidth: 26
                            }

                            Text {
                                text: name
                                color: present ? Theme.text : Theme.muted
                                font.pixelSize: 13
                                font.bold: present
                                Layout.preferredWidth: 104
                                elide: Text.ElideRight
                            }

                            DarkField {
                                id: minField
                                text: minTime
                                placeholderText: "HH:MM"
                                Layout.preferredWidth: 78
                                enabled: presentBox.checked
                                opacity: enabled ? 1.0 : 0.45
                            }

                            DarkField {
                                id: maxField
                                text: maxTime
                                placeholderText: "HH:MM"
                                Layout.preferredWidth: 78
                                enabled: presentBox.checked
                                opacity: enabled ? 1.0 : 0.45
                            }

                            Connections {
                                target: presentBox
                                function onToggled() {
                                    planner.updateDJ(index, presentBox.checked, minField.text, maxField.text)
                                }
                            }

                            Connections {
                                target: minField
                                function onEditingFinished() {
                                    planner.updateDJ(index, presentBox.checked, minField.text, maxField.text)
                                }
                            }

                            Connections {
                                target: maxField
                                function onEditingFinished() {
                                    planner.updateDJ(index, presentBox.checked, minField.text, maxField.text)
                                }
                            }
                        }
                    }
                }

                PrimaryButton {
                    text: "GENERATE / REGENERATE"
                    Layout.fillWidth: true
                    Layout.preferredHeight: 50
                    onClicked: planner.generate()
                }
            }
        }

        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 14

            Card {
                Layout.fillWidth: true
                Layout.preferredHeight: 288

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 18
                    spacing: 12

                    RowLayout {
                        Layout.fillWidth: true

                        Column {
                            Layout.fillWidth: true
                            spacing: 2

                            Text {
                                text: "Timeline"
                                color: Theme.text
                                font.pixelSize: 21
                                font.bold: true
                            }

                            Text {
                                text: "Drag cards to swap DJs • double-click to lock"
                                color: Theme.muted
                                font.pixelSize: 11
                            }
                        }

                        Rectangle {
                            width: 10
                            height: 10
                            radius: 5
                            color: Theme.purple
                        }

                        Text {
                            text: "Time slot"
                            color: Theme.muted
                            font.pixelSize: 11
                        }
                    }

                    ListView {
                        id: timelineList
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        orientation: ListView.Horizontal
                        spacing: 12
                        clip: true
                        boundsBehavior: Flickable.StopAtBounds
                        model: planner.scheduleModel

                        ScrollBar.horizontal: DarkScrollBar {
                            orientation: Qt.Horizontal
                            implicitHeight: 8
                        }

                        delegate: Item {
                            required property int slotIndex
                            required property string dj
                            required property string start
                            required property string end
                            required property int duration
                            required property real value
                            required property bool locked

                            width: 190
                            height: timelineList.height - 12

                            TimelineCard {
                                id: card
                                anchors.verticalCenter: parent.verticalCenter
                                slotIndex: parent.slotIndex
                                dj: parent.dj
                                startTime: parent.start
                                endTime: parent.end
                                duration: parent.duration
                                value: parent.value
                                locked: parent.locked

                                onLockRequested: function(i) {
                                    planner.toggleLock(i)
                                }

                                onDragFinished: function(sourceIndex, sceneCenterX) {
                                    // Convert the dragged card center from scene coordinates
                                    // to the horizontal ListView content coordinate.
                                    var local = timelineList.mapFromItem(null, sceneCenterX, 0)
                                    var contentX = local.x + timelineList.contentX
                                    var unit = 190 + timelineList.spacing
                                    var targetIndex = Math.floor(contentX / unit)

                                    if (targetIndex < 0)
                                        targetIndex = 0
                                    if (targetIndex >= timelineList.count)
                                        targetIndex = timelineList.count - 1

                                    if (targetIndex !== sourceIndex)
                                        planner.swapSlots(sourceIndex, targetIndex)
                                }
                            }
                        }
                    }
                }
            }

            Card {
                Layout.fillWidth: true
                Layout.fillHeight: true

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 18
                    spacing: 10

                    RowLayout {
                        Layout.fillWidth: true

                        Text {
                            text: "Schedule details"
                            color: Theme.text
                            font.pixelSize: 18
                            font.bold: true
                            Layout.fillWidth: true
                        }

                        PrimaryButton {
                            text: "Validate"
                            normalColor: Theme.card2
                            hoverColor: Theme.cardHover
                            onClicked: planner.validateCurrent()
                        }

                        PrimaryButton {
                            text: "Archive"
                            normalColor: Theme.card2
                            hoverColor: Theme.cardHover
                            onClicked: planner.archiveCurrent()
                        }

                        PrimaryButton {
                            text: "Export Excel"
                            onClicked: planner.exportExcel()
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        height: 1
                        color: Theme.border
                    }

                    ListView {
                        id: detailList
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true
                        spacing: 6
                        model: planner.scheduleModel

                        ScrollBar.vertical: DarkScrollBar {}

                        delegate: Rectangle {
                            required property int slotIndex
                            required property string dj
                            required property string start
                            required property string end
                            required property int duration
                            required property real value
                            required property bool locked

                            width: detailList.width
                            height: 50
                            radius: 9
                            color: Theme.card2
                            border.width: 1
                            border.color: locked ? Theme.amber : Theme.border

                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 10

                                Text {
                                    text: "#" + (slotIndex + 1)
                                    color: Theme.muted
                                    Layout.preferredWidth: 36
                                }

                                Text {
                                    text: start + " → " + end
                                    color: Theme.text
                                    Layout.preferredWidth: 145
                                }

                                Text {
                                    text: dj
                                    color: Theme.text
                                    font.bold: true
                                    Layout.fillWidth: true
                                }

                                Text {
                                    text: duration + " min"
                                    color: Theme.muted
                                    Layout.preferredWidth: 75
                                }

                                Rectangle {
                                    Layout.preferredWidth: 92
                                    Layout.preferredHeight: 28
                                    radius: 7
                                    color: Theme.purpleDark

                                    Text {
                                        anchors.centerIn: parent
                                        text: Number(value).toFixed(2)
                                        color: Theme.purpleSoft
                                        font.bold: true
                                    }
                                }

                                Text {
                                    text: locked ? "Locked" : ""
                                    color: Theme.amber
                                    font.bold: locked
                                    Layout.preferredWidth: 75
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
