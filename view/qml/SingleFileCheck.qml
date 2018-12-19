import QtQuick 2.4
import QtQuick.Dialogs 1.0
import QtQuick.Controls 1.4

Item {
    id: item1
    property alias text: label_check.text
    property alias model: list_view.model
    property alias index_tab: only_tan_index.text
    height: list_view.height + label_check.height
    width: 500

    Label{
        id: label_check
        text: "Name mode"
        anchors.left: parent.left
        anchors.top: parent.top
    }

    Label{
        id: only_tan_index
        anchors.left: label_check.right
        text: '0'
        visible: false
    }

    ListModel{
        id: model_params
        ListElement{
            arg: 'arg_1'
            comf: 'comf_1'
        }
        ListElement{
            arg: 'arg_2'
            comf: 'comf_2'
        }
        ListElement{
            arg: 'arg_3'
            comf: 'comf_3'
        }
        ListElement{
            arg: 'arg_4'
            comf: 'comf_4'
        }
        ListElement{
            arg: 'arg_4'
            comf: 'comf_4'
        }
    }

    ListView {
        id: list_view
        anchors.top: label_check.bottom
        width: parent.width
        height: 26*model_params.count
        highlightFollowsCurrentItem: true
        model: model_params
        delegate: RowParameters{
            id: row_s
            arg_text: arg
            comf_text:row_s.file_url==''?comf:row_s.file_url
            index: model.index

            onClear_row: {
                console.log('clear', row_s.arg_text, row_s.comf_text)
                row_s.clear()
            }
        }
    }
}

