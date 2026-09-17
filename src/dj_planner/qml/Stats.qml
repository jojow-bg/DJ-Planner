
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "components"

Item {
    anchors.fill: parent

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 22
        spacing: 16

        Column {
            Text {
                text: "Fairness statistics"
                color: Theme.text
                font.pixelSize: 24
                font.bold: true
            }

            Text {
                text: "Playing time, average slot value and historical position for each DJ."
                color: Theme.muted
                font.pixelSize: 12
            }
        }

        Card {
            Layout.fillWidth: true
            Layout.fillHeight: true

            ListView {
                id: list
                anchors.fill: parent
                anchors.margins: 16
                clip: true
                spacing: 7
                model: planner.statsModel

                ScrollBar.vertical: DarkScrollBar {}

                delegate: Rectangle {
                    required property string dj
                    required property int sets
                    required property string minutes
                    required property real avgValue
                    required property var avgPosition
                    required property string latest

                    width: list.width
                    height: 58
                    radius: 9
                    color: Theme.card2
                    border.width: 1
                    border.color: Theme.border

                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 10

                        Text {
                            text: dj
                            color: Theme.text
                            font.bold: true
                            Layout.preferredWidth: 170
                        }

                        Text {
                            text: sets + " sets"
                            color: Theme.muted
                            Layout.preferredWidth: 90
                        }

                        Text {
                            text: minutes
                            color: Theme.text
                            Layout.preferredWidth: 90
                        }

                        Rectangle {
                            Layout.preferredWidth: 115
                            Layout.preferredHeight: 28
                            radius: 7
                            color: Theme.purpleDark

                            Text {
                                anchors.centerIn: parent
                                text: "Value " + Number(avgValue).toFixed(2)
                                color: Theme.purpleSoft
                                font.bold: true
                            }
                        }

                        Text {
                            text: avgPosition === "" ? "" : "Pos. " + avgPosition
                            color: Theme.muted
                            Layout.preferredWidth: 100
                        }

                        Text {
                            text: latest
                            color: Theme.muted
                            Layout.fillWidth: true
                        }
                    }
                }
            }
        }
    }
}
