import QtQuick 2.5
import QtQuick.Dialogs 1.0
import QtQuick.Controls 1.4

Item{
    property alias arg_text: text_field_arg.text
    property alias comf_text: text_field_comf.text
    property alias file_url: file_dialog.fileUrl
    property alias index: number.text
    signal add_row
    signal del_row
    id: row_param
    height: text_field_comf.height
    width: 356

    FileDialog{
        id: file_dialog
        title: "Please choose a file"
        folder: shortcuts.home
        onAccepted: {
            console.log("You chose: " + file_dialog.fileUrls)
        }
    }

    Label{
        id: number
        text: ''
    }

    TextField{
        id: text_field_arg
        anchors.left: number.right
        anchors.leftMargin: 5
        text: 'test_text'
    }

    TextField{
        id: text_field_comf
        anchors.left: text_field_arg.right
        anchors.leftMargin: 20
        text: file_dialog.fileUrl
    }

    SingleButton{
        id:bt_add
        label: qsTr('...')
        height: text_field_comf.height
        anchors.left: text_field_comf.right

        onClicked: {
            file_dialog.open()
        }
        SingleButton{
            id: clear_bt
            label: "del"
            height: text_field_comf.height
            anchors.left: bt_add.right
            anchors.leftMargin: 20
            onClicked: {
                row_param.del_row()
            }
        }

        SingleButton{
            id: add_bt
            label: "add row"
            height: text_field_comf.height
            anchors.left: clear_bt.right
            anchors.leftMargin: 20
            onClicked: {
                row_param.add_row()
            }
        }

    }
}
