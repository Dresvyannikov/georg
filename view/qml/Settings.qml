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


    SingleButton{
        anchors {
            bottom: parent.bottom
            bottomMargin: 20
            left: parent.left
            leftMargin: 120

        }
        label: qsTr("Сохранить")

        onClicked: {
            console.log('count tabs', tabview_settings.count)

            // сохранение списка всех режимов
            list_data_mode.save_db()

//            console.log('dict_model do', dict_model)
//            var index;
//            for (index=1; index < 2; index++){
//                console.log('add')
//                dict_model.append({index: fruitModel})
//            }
            console.log('dict_mode post', list_model_config.count)


            // сохраняем параметры имитаторов по вкладкам
            var tab_index;
            var tab;
            for (tab_index=1; tab_index < tabview_settings.count; tab_index++){
                tab = tabview_settings.getTab(tab_index)
                var split_v;
                split_v = tab.children[0]
                console.log('child1', tab.children[1])
                if(split_v){
                    console.log('split', split_v.__contents.length)
                }
            }
            list_data_cube.save_configs(configArea.text)

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
                                console.log(index, text)
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

                SplitView{

                    anchors.fill: parent
                    orientation: Qt.Horizontal
                    Item{
//                        width: parent.width / 3
                        width: 145
                        TextArea{
                            readOnly: true
                            id: configArea
                            anchors.left: parent.left
                            anchors.top: parent.top
                            anchors.bottom: parent.bottom
                            anchors.bottomMargin: 40
                            width: parent.width
                            text: model.config
                        }
                    }

                    Item{
                        id: item_right
                        width: parent.width / 2
                        height: parent.height



                        ScrollView{
                            id: scrollViewTab
                            anchors.top: parent.top
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
                                    height: 26*4
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

                                        spacing: 2

                                        SingleFileCheck{
                                            text: text_component.text
                                            model: list_model_files
                                            index_tab: tabview_settings.currentIndex
                                        }
                                    }
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
                implicitWidth: Math.max(text.width + 4, 80)
                implicitHeight: 20
                radius: 2
                Text {
                    id: text
                    anchors.centerIn: parent
                    text: styleData.title
                    color: styleData.selected ? "white" : "black"
                }
            }
            //                  frame: Rectangle { color: "steelblue" }
        }

    }
}
