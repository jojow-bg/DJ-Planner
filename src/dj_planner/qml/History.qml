
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

        RowLayout {
            Layout.fillWidth: true

            Column {
                Layout.fillWidth: true
                Text {
                    text: "History"
                    color: Theme.text
                    font.pixelSize: 24
                    font.bold: true
                }
                Text {
                    text: "Only archived events influence fairness in future schedules."
                    color: Theme.muted
                    font.pixelSize: 12
                }
            }

            PrimaryButton {
                text: "Clear history"
                normalColor: Theme.card2
                hoverColor: Theme.cardHover
                onClicked: planner.clearHistory()
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
                model: planner.historyModel

                ScrollBar.vertical: DarkScrollBar {}

                delegate: Rectangle {
                    required property string party
                    required property string date
                    required property string dj
                    required property string start
                    required property string end
                    required property real value

                    width: list.width
                    height: 56
                    radius: 9
                    color: Theme.card2
                    border.width: 1
                    border.color: Theme.border

                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 10

                        Text {
                            text: party
                            color: Theme.text
                            Layout.preferredWidth: 190
                            elide: Text.ElideRight
                        }

                        Text {
                            text: date
                            color: Theme.muted
                            Layout.preferredWidth: 100
                        }

                        Text {
                            text: dj
                            color: Theme.text
                            font.bold: true
                            Layout.fillWidth: true
                        }

                        Text {
                            text: start + " → " + end
                            color: Theme.text
                            Layout.preferredWidth: 140
                        }

                        Rectangle {
                            Layout.preferredWidth: 72
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
                    }
                }
            }
        }
    }
}
