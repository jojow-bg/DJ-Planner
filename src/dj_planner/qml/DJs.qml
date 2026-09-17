
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
                    text: "DJ management"
                    color: Theme.text
                    font.pixelSize: 24
                    font.bold: true
                }
                Text {
                    text: "Add or remove active DJs while keeping their history."
                    color: Theme.muted
                    font.pixelSize: 12
                }
            }

            DarkField {
                id: newDjField
                placeholderText: "New DJ name"
                Layout.preferredWidth: 240
            }

            PrimaryButton {
                text: "+ Add"
                onClicked: {
                    planner.addDJ(newDjField.text)
                    newDjField.text = ""
                }
            }

            PrimaryButton {
                text: "- Remove"
                normalColor: Theme.card2
                hoverColor: Theme.cardHover
                onClicked: if (selectedIndex >= 0) planner.removeDJ(selectedIndex)
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
                model: planner.djModel

                ScrollBar.vertical: DarkScrollBar {}

                delegate: Rectangle {
                    required property string name
                    required property int index

                    width: list.width
                    height: 56
                    radius: 10
                    color: selectedIndex === index ? Theme.cardHover : Theme.card2
                    border.width: selectedIndex === index ? 2 : 1
                    border.color: selectedIndex === index ? Theme.purple : Theme.border

                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.left: parent.left
                        anchors.leftMargin: 18
                        text: name
                        color: Theme.text
                        font.pixelSize: 16
                        font.bold: true
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: selectedIndex = index
                    }
                }
            }
        }
    }
}
