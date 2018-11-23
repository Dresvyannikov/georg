import QtQuick 2.0

Item{
    id: container
    property alias label: labelText.text
    property alias color_state: status_rectangle.color
    property alias color_fone: fone.color
    property int index_cube: 0
    width: 160
    height: 150

    Rectangle{
        id: fone
        width: container.width
        height: container.height
        color: "#9cdb8c"
        border.width: 2
    }

    SingleButton {
        id:stop_rectangle
        x: 40
        y: 2
        width: container.width / 4
        height: container.height / 4
        label: qsTr("Stop")
        //        anchors.fill: container;
//        color: buttonMouseArea.pressed ? Qt.darker(container.buttonColor, 1.5) : container.buttonColor
    }
    SingleButton {
        id:start_rectangle
        x: 2
        y: 2
        width: container.width / 4
        height: container.height / 4
        label: qsTr("Start")
//        anchors.fill: container;
//        color: buttonMouseArea.pressed ? Qt.darker(container.buttonColor, 1.5) : container.buttonColor
    }

    SingleButton {
        id:update_rectangle
        x: width * 2
        y: 2
        width: container.width / 4
        height: container.height / 4
        label: qsTr("Upd")
//        anchors.fill: container;
//        color: buttonMouseArea.pressed ? Qt.darker(container.buttonColor, 1.5) : container.buttonColor
    }

    Rectangle {
        id:status_rectangle
        x: container.width * 3 / 4
        y: 2
        width: container.width / 4 - 2
        height: container.height / 4
        color: "gray"
//        anchors.fill: container;
//        opacity: 0.25
//        color: buttonMouseArea.pressed ? Qt.darker(container.buttonColor, 1.5) : container.buttonColor
    }

    Text { id: labelText; font.pixelSize: 15; anchors.centerIn: parent; text: qsTr("Test") }

    SingleButton {
        id:console_rectangle
        x: 2
        y: container.height - 3 - container.height / 4
        width: container.width - 4
        height: container.height / 4
        label: qsTr("Console")
//        anchors.fill: container;
//        opacity: 0.25
//        color: buttonMouseArea.pressed ? Qt.darker(container.buttonColor, 1.5) : container.buttonColor

    }

    Connections {
        target: stop_rectangle
        onClicked: list_data_cube.set_command(container.index_cube, qsTr("stop"))
    }

    Connections {
        target: start_rectangle
        onClicked: list_data_cube.set_command(container.index_cube, qsTr("start"))
    }



    Connections {
        target: update_rectangle
        onClicked: list_data_cube.set_command(container.index_cube, qsTr("diag"))
    }

    Connections {
        target: console_rectangle
        onClicked: list_data_cube.set_command(container.index_cube, qsTr("console"))
    }
}
