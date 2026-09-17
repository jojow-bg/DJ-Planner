
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: window
    width: 1440
    height: 900
    minimumWidth: 1180
    minimumHeight: 720
    visible: true
    title: "DJ Planner"
    color: Theme.bg

    palette.window: Theme.bg
    palette.windowText: Theme.text
    palette.base: Theme.card2
    palette.alternateBase: Theme.card
    palette.text: Theme.text
    palette.button: Theme.card2
    palette.buttonText: Theme.text
    palette.highlight: Theme.purple
    palette.highlightedText: Theme.text
    palette.toolTipBase: Theme.card2
    palette.toolTipText: Theme.text

    property var pages: [
        "Planning.qml",
        "DJs.qml",
        "Bands.qml",
        "History.qml",
        "Stats.qml"
    ]

    property var labels: [
        "Scheduling",
        "DJs",
        "Time bands",
        "History",
        "Statistics"
    ]

    background: Rectangle {
        color: Theme.bg
    }

    header: Rectangle {
        height: 78
        color: Theme.header
        border.width: 1
        border.color: Theme.border

        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 24
            anchors.rightMargin: 24
            spacing: 18

            Column {
                Layout.preferredWidth: 230
                spacing: 1

                Text {
                    text: "DJ PLANNER"
                    color: Theme.text
                    font.pixelSize: 24
                    font.bold: true
                    font.letterSpacing: 0.5
                }

                Text {
                    text: "CONSTRAINT-BASED SCHEDULING"
                    color: Theme.purpleSoft
                    font.pixelSize: 11
                    font.bold: true
                }
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: 6

                Repeater {
                    model: window.labels.length

                    delegate: Button {
                        required property int index

                        text: window.labels[index]
                        implicitHeight: 42
                        leftPadding: 16
                        rightPadding: 16

                        contentItem: Text {
                            text: parent.text
                            color: planner.selectedTab === index ? Theme.text : Theme.muted
                            font.pixelSize: 13
                            font.bold: planner.selectedTab === index
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }

                        background: Rectangle {
                            radius: 10
                            color: planner.selectedTab === index
                                   ? Theme.purple
                                   : (parent.hovered ? Theme.cardHover : "transparent")
                            border.width: planner.selectedTab === index ? 0 : 1
                            border.color: Theme.border
                        }

                        onClicked: planner.selectedTab = index
                    }
                }
            }

            Rectangle {
                Layout.preferredWidth: 210
                Layout.preferredHeight: 34
                radius: 9
                color: Theme.card2
                border.width: 1
                border.color: Theme.border

                Text {
                    anchors.centerIn: parent
                    width: parent.width - 18
                    text: planner.status
                    color: Theme.muted
                    font.pixelSize: 11
                    horizontalAlignment: Text.AlignHCenter
                    elide: Text.ElideRight
                }
            }
        }
    }

    Loader {
        anchors.fill: parent
        source: window.pages[planner.selectedTab]
    }

    Popup {
        id: messagePopup
        width: Math.min(620, window.width - 80)
        anchors.centerIn: Overlay.overlay
        modal: true
        focus: true
        padding: 22

        property bool errorMode: false
        property string messageText: ""

        background: Rectangle {
            radius: 14
            color: Theme.card
            border.width: 2
            border.color: messagePopup.errorMode ? Theme.red : Theme.purple
        }

        contentItem: ColumnLayout {
            spacing: 16

            Text {
                text: messagePopup.errorMode ? "Warning" : "Information"
                color: Theme.text
                font.pixelSize: 20
                font.bold: true
            }

            Text {
                text: messagePopup.messageText
                color: Theme.text
                wrapMode: Text.Wrap
                Layout.fillWidth: true
            }

            Button {
                text: "Close"
                Layout.alignment: Qt.AlignRight

                contentItem: Text {
                    text: parent.text
                    color: Theme.text
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    font.bold: true
                }

                background: Rectangle {
                    radius: 9
                    color: parent.hovered ? Theme.purpleHover : Theme.purple
                }

                onClicked: messagePopup.close()
            }
        }
    }

    Connections {
        target: planner

        function onErrorRaised(message) {
            messagePopup.errorMode = true
            messagePopup.messageText = message
            messagePopup.open()
        }

        function onInfoRaised(message) {
            messagePopup.errorMode = false
            messagePopup.messageText = message
            messagePopup.open()
        }
    }
}
