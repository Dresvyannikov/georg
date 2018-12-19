import QtQuick 2.5
import QtQuick.Controls 1.4
import QtQuick.Window 2.2
import QtQuick.Layouts 1.3
import QtQuick.Controls.Styles 1.4
import QtQuick.Dialogs 1.0

ApplicationWindow{
    id: anotherWindow
    width:root.width
    height:root.height
    signal signalExit

    statusBar: StatusBar{
        RowLayout {
                      anchors.fill: parent
                      Label {
                          id: status_text
                          text: "Read Only" }
                  }
    }

    SingleButton{
        anchors {
            bottom: parent.bottom
            bottomMargin: 20
            left: parent.left
            leftMargin: 120

        }
        label: qsTr("Сохранить")

        onClicked: {
//            console.log('count tabs', tabview_settings.count)

            status_text.text = 'Сохранение настроек...'
            // сохранение списка всех режимов
            list_data_mode.save_db()

            // сохраняем параметры имитаторов по вкладкам
            var tab_index, tab;
            for (tab_index=1; tab_index < tabview_settings.count; tab_index++){
                tab = tabview_settings.getTab(tab_index)
                var list_view, list_view_index;
                // пропускаем вкладки, которые не были активными
                if (tab.item === null){
                    continue
                }
                list_view = tab.item.children[1].contentItem;
                list_view.currentIndex = 0; // после инкрементов вернуть назад, если нужно сохранить повторно
                // перечисление SingleFileCheck из списка
                for (list_view_index=0; list_view_index < list_view.count ; list_view_index++){
                    var item, column, checkbox;
                    item = list_view.currentItem;
                    column = item.children[1]
                    checkbox = item.children[2]

                    var index_element, data, j_data;
                    column.data[0].children[2].currentIndex = 0
                    data = {}
                    // перечисляем строки в одном режиме и записываем данные в data
                    for (index_element=0; index_element < column.data[0].children[2].count; index_element++){
                        data['arg_' + index_element] = column.data[0].children[2].currentItem.children[1].text;
                        data['file_' + index_element] =  column.data[0].children[2].currentItem.children[2].text;
                        column.data[0].children[2].incrementCurrentIndex() // инкремент индекса(на грфике видно как двигается скролл)
                    }
                    j_data = JSON.stringify(data)
                    // передача данных в ядро
//                  console.log('mode_name', column.data[0].text)
                    list_data_cube.set_data_config(tab_index, column.data[0].text, j_data, checkbox.checked)
                    list_view.incrementCurrentIndex() // инкремент индекса
                }
            }
            status_text.text = 'Сохранено'
        }
    }

    SingleButton {
        anchors {
            bottom: parent.bottom
            horizontalCenter: parent.horizontalCenter
            bottomMargin: 20
        }
        label: qsTr("Главное окно")

        onClicked: {
            status_text.text = ''
            anotherWindow.signalExit() // Вызываем сигнал
        }
    }

    TabView {
        id: tabview_settings
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 50

        Tab {
            active: true
            title: qsTr("Modes")


            SplitView{
                id: panel
                anchors.fill: parent
                orientation: Qt.Horizontal

                Column{
                    id:columnModes
                    Repeater{
                        model: list_data_mode
                        delegate: TextField{
                            text: model.text
                            onEditingFinished:{
                                list_data_mode.change_mode(index, text)
                            }
                        }
                    }
                }

                Column{
                    id: buttoncolumn

                    TextField{
                        id: fieldMode
                        text: 'text'
                    }

                    SingleButton{
                        id: addButton
                        label: qsTr("add mode")
                        onClicked: {
                            list_data_mode.add_mode(fieldMode.text)
                        }
                    }
                }

            }
        }

        Repeater{
            model: list_data_cube
            delegate: Tab{
                id: service_tab
                title: model.label

                    Item{
                        id: item_right
                        height: parent.height

                        SingleButton{
                            id: button_conf
                            label: qsTr("config")

                            onClicked: {
                                var component = Qt.createComponent('Config.qml')
                                var window = component.createObject(root)
                                window.closing.connect(function(){window.close.accepted = false})
                                window.show()
                                window.change_config(tabview_settings.currentIndex)
//                            config_window.show()
//                            config_window.change_config(tabview_settings.currentIndex)
                            }
                        }

                        ScrollView{
                            id: scrollViewTab
                            anchors.top: button_conf.bottom
                            anchors.bottom: parent.bottom
                            anchors.left: parent.left
                            anchors.right: parent.right

                            verticalScrollBarPolicy: Qt.ScrollBarAlwaysOn

                            horizontalScrollBarPolicy: Qt.ScrollBarAlwaysOn
                            property int scrollWidth: 10

                            style: ScrollViewStyle {
                                id: sptScrollStyle
                                property int iScrollWidth: 10
                                handle: Rectangle {
                                    implicitWidth: iScrollWidth
                                    color: "gray"
                                    radius: 20
                                }
                                scrollBarBackground: Rectangle {
                                    implicitWidth: iScrollWidth
                                    color: "lightgray"
                                    radius: 20
                                }
                                decrementControl: Rectangle {
                                    implicitWidth: 0
                                }
                                incrementControl: Rectangle {
                                    implicitWidth: 0
                                }
                            }

                            ListView{
                                id: list_view_files
                                spacing: 2
                                anchors.top: parent.top
                                anchors.bottom: parent.bottom
                                anchors.bottomMargin: 40
                                width: item_right.width - 10
                                model: list_data_mode
                                header: Label{text: 'Редактирование конфигурации:'}

                                delegate:
                                    Item{
                                    height: column_files.height
                                    width: parent.width
                                    id: component_list

                                    ListModel{
                                        id: list_model_files
                                    }

                                    Label{
                                        id: text_component
                                        text: model.text
                                    }

                                    Component.onCompleted:
                                    {
                                        if (tabview_settings.currentIndex == 0){
                                            return
                                        }
                                        var mode_name = model.text
                                        var tab_index = tabview_settings.currentIndex
                                        var data = list_data_cube.get_data(tab_index, mode_name)
                                        list_model_files.clear()
                                        for(var item in data){
                                            list_model_files.append(data[item])
                                        }
                                    }

                                    Column{
                                        id: column_files
                                        width: parent.width
                                        height: solo_rows.height
                                        spacing: 2

                                        SingleFileCheck{
                                            id: solo_rows
                                            text: text_component.text
                                            model: list_model_files
                                            index_tab: tabview_settings.currentIndex
                                        }
                                    }

                                    CheckBox{
                                        id: block_mode
                                        text: qsTr('Активный режим')
                                        anchors.left: text_component.right
                                        anchors.leftMargin: 10
                                        checked: list_data_cube.get_block_mode(model.text, tabview_settings.currentIndex) // ? true: false
                                    }
                                }
                            }
                        }
                    }
            }
        }

        style: TabViewStyle {
            frameOverlap: 1
            tab: Rectangle {
                color: styleData.selected ? "steelblue" :"lightsteelblue"
                border.color:  "steelblue"
                implicitWidth: Math.max(text_id.width + 4, 80)
                implicitHeight: 20
                radius: 2
                Text {
                    id: text_id
                    anchors.centerIn: parent
                    text: styleData.title
                    color: styleData.selected ? "white" : "black"
                }
            }
            //                  frame: Rectangle { color: "steelblue" }
        }

    }

    Config{
        id:config_window
        title: qsTr("Config")
        color: root.color
    }
}
