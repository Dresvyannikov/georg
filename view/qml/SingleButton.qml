import QtQuick 2.0

Item {
    id: container

    property alias label: labelText.text
    property color buttonColor: "lightblue"
    property color onHoverColor: "gold"
    property color borderColor: "white"

    signal clicked

    onClicked: {
        console.log(labelText.text + " clicked")
    }

    width: labelText.width
    height: labelText.height

    Rectangle {
        id:rectangle
        anchors.fill: container;
        color: buttonMouseArea.pressed ? Qt.darker(container.buttonColor, 1.5) : container.buttonColor
        border.color: container.borderColor
    }

    Text { id: labelText; font.pixelSize: 15; anchors.centerIn: parent; text: qsTr("Test") }

    MouseArea {
        id: buttonMouseArea
        width: container.width
        height: container.height
        onClicked: container.clicked()
        hoverEnabled: true
        onEntered: rectangle.border.color = container.onHoverColor
        onExited: rectangle.border.color = container.borderColor
    }
}
