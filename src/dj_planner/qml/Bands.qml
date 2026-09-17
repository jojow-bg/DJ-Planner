
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "components"

Item {
    anchors.fill: parent
    property int selectedIndex: -1

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 22
        spacing: 16

        RowLayout {
            Layout.fillWidth: true

            Column {
                Layout.fillWidth: true
                Text {
                    text: "Time bands"
                    color: Theme.text
                    font.pixelSize: 24
                    font.bold: true
                }
                Text {
                    text: "Set values are weighted by the time spent in each band."
                    color: Theme.muted
                    font.pixelSize: 12
                }
            }

            PrimaryButton {
                text: "+ Add"
                onClicked: planner.addBand()
            }

            PrimaryButton {
                text: "- Remove"
                normalColor: Theme.card2
                hoverColor: Theme.cardHover
                onClicked: if (selectedIndex >= 0) planner.removeBand(selectedIndex)
            }
        }

        Card {
            Layout.fillWidth: true
            Layout.fillHeight: true

            ListView {
                id: list
                anchors.fill: parent
                anchors.margins: 16
                spacing: 8
                clip: true
                model: planner.bandModel

                ScrollBar.vertical: DarkScrollBar {}

                delegate: Rectangle {
                    required property string start
                    required property string end
                    required property real value
                    required property int index

                    width: list.width
                    height: 64
                    radius: 10
                    color: Theme.card2
                    border.width: selectedIndex === index ? 2 : 1
                    border.color: selectedIndex === index ? Theme.purple : Theme.border

                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 12

                        Text {
                            text: "Start"
                            color: Theme.muted
                        }

                        DarkField {
                            id: startField
                            text: start
                            Layout.preferredWidth: 115
                            onEditingFinished: planner.updateBand(index, text, endField.text, Number(valueField.text))
                        }

                        Text {
                            text: "→"
                            color: Theme.muted
                        }

                        DarkField {
                            id: endField
                            text: end
                            Layout.preferredWidth: 115
                            onEditingFinished: planner.updateBand(index, startField.text, text, Number(valueField.text))
                        }

                        Text {
                            text: "Value"
                            color: Theme.muted
                        }

                        DarkField {
                            id: valueField
                            text: Number(value).toFixed(2)
                            Layout.preferredWidth: 95
                            onEditingFinished: planner.updateBand(index, startField.text, endField.text, Number(text))
                        }

                        Item {
                            Layout.fillWidth: true
                        }

                        Rectangle {
                            width: 10
                            height: 10
                            radius: 5
                            color: Theme.purple
                        }
                    }

                    MouseArea {
                        anchors.fill: parent
                        acceptedButtons: Qt.RightButton
                        onClicked: selectedIndex = index
                    }
                }
            }
        }
    }
}
