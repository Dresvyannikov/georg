import QtQuick 2.5
import QtQuick.Controls 1.4
import QtQuick.Window 2.2
import QtQuick.Layouts 1.3
import QtQuick.Controls.Styles 1.4
import QtQuick.Dialogs 1.0

Window{
    id: root
    width:640
    height:480
    flags: Qt.Window | Qt.WindowCancelButtonHint

    function change_config(index){
        var text_config;
        text_config = list_data_cube.item_data(index-1)
        configArea.text = text_config.config
    }

    TextArea{
        id: configArea
        readOnly: true
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 40
        width: parent.width
        text: model.config
    }

    SingleButton{
        anchors.top: configArea.bottom
        anchors.topMargin: 10
        anchors.horizontalCenter: parent.horizontalCenter
        label: 'Закрыть'
        onClicked: root.hide()
    }
}
