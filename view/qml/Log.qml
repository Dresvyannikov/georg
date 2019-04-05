import QtQuick 2.5
import QtQuick.Controls 1.4
import QtQuick.Window 2.2
import QtQuick.Layouts 1.3
import QtQuick.Controls.Styles 1.4
import QtQuick.Dialogs 1.0

ApplicationWindow{
    id: logWindow
    width:640
    height:480
    flags: Qt.Window | Qt.WindowCancelButtonHint
    signal signalExit

    function change_cube(index){
        var data_cube;
        data_cube = list_data_cube.get_logs(index)
        logsArea.text = data_cube.log
    }

    TextArea{
        id: logsArea
        readOnly: true
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 40
        width: parent.width
        text: 'adadadda'
    }

    SingleButton{
        anchors.top: logsArea.bottom
        anchors.topMargin: 10
        anchors.horizontalCenter: parent.horizontalCenter
        label: 'Закрыть'
        onClicked: logWindow.signalExit() // Вызываем сигнал
    }
}
