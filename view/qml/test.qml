import QtQuick 2.0
import QtQuick.Controls 2.0
import QtQuick.Layouts 1.3
import QtQuick.Templates 2.0

Item {
    id: root
    width: 600
    height: 400

    RowLayout {
        id: layout
        anchors.fill: parent
        spacing: 6

        Rectangle {
            id: rectangle
            color: 'teal'
            transformOrigin: Item.Center
            clip: false
            visible: true
            Layout.fillWidth: true
            Layout.fillHeight: true
            Text {
                text: 'config.ini'
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: parent.top
            }

            Text{
                id: content
                x: -vbar.position * width
                y: -hbar.position * height
                text: 'qweqweqwe '
                font.pixelSize: 160
                }

            ScrollBar{
                id: vbar
                hoverEnabled: true
                active: hovered || pressed
                orientation: Qt.Vertical
                size: rectangle.height / content.height
                anchors.top: parent.top
                anchors.right: parent.right
                anchors.bottom: parent.bottom
            }
            ScrollBar{
                id: hbar
                hoverEnabled: true
                active: hovered || pressed
                orientation: Qt.Horizontal
                size: rectangle.width / content.width
                anchors.top: parent.top
                anchors.right: parent.right
                anchors.bottom: parent.bottom
            }

        }

        Rectangle {
            color: 'plum'
            Layout.fillWidth: true
            Layout.fillHeight: true

            TextArea {
                id:textArea
                anchors.centerIn: parent
                text: parent.width + 'x' + parent.height
                anchors.verticalCenterOffset: -190
                anchors.horizontalCenterOffset: 0
            }
    }
}
}
