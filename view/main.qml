import QtQuick.Window 2.2
import QtQuick 2.5
import QtQuick.Controls 1.4
import QtQuick.Dialogs 1.0
import QtQuick.Controls.Styles 1.4
import QtQuick.Layouts 1.0
import "qml"


ApplicationWindow {
    id: root
    visible: true
    width: 640
    height: 480
    title: main_window.name
    color: "#5e0f0f"

    statusBar: StatusBar {
              RowLayout {
                  anchors.fill: parent
                  Label { text: "Read Only" }
              }
          }

    Rectangle {
        id: rectangle
        height: 65
        color: "#555753"
        anchors.right: parent.right
        anchors.rightMargin: 6
        anchors.left: parent.left
        anchors.leftMargin: 6
        anchors.top: parent.top
        anchors.topMargin: 6
        border.width: 2

        Row {
            id: panel
            height: 21
            anchors.horizontalCenterOffset: 0
            spacing: 20
            anchors {
                top: parent.top
                horizontalCenter: parent.horizontalCenter
                bottomMargin: 20
                topMargin: 22}

            SingleButton {
                id: startButton
                label: qsTr("Start")
                onClicked: {
                    main_window.mode = boxmodes.currentText
                    main_window.user = boxusers.currentText
                    main_window.start_all()}
                //            rotation: -2;
            }

            SingleButton {
                id: stopButton
                label: qsTr("Auto")
                onClicked: main_window.auto_start()
            }

            SingleButton {
                id: newWindowButton
                label: qsTr("Power")
                onClicked: {
                    powerWindow.show()
                    root.hide()
                }
            }

            SingleButton {
                id: settingsButton
                label: qsTr("Settings")
                onClicked: {
                    main_window.connection_thread_stop()
                    settingsWindow.show()
                    root.hide()
                }
            }

            SingleButton {
                id: quitButton
                label: qsTr("Quit")
                onClicked: Qt.quit()
            }
        }
    }

    Rectangle {
        id: checkRect
        width: 628
        height: 35
        border.width: 2
        anchors.right: parent.right
        anchors.rightMargin: 6
        anchors.left: parent.left
        anchors.leftMargin: 6
        anchors.top: rectangle.bottom
        anchors.topMargin: 6

        Row {
            anchors.verticalCenter: parent.verticalCenter
            anchors.right: parent.right
            anchors.rightMargin: 6
            anchors.left: parent.left
            anchors.leftMargin: 6
            Label{
                text: 'Mode: '
            }

            ComboBox{
                id: boxmodes
                style: ComboBoxStyle{}
                model: list_data_mode
                textRole: 'text'
           }

            Label{
                text: 'User: '
            }

            ComboBox{
                id: boxusers
                style: ComboBoxStyle{}
                model: list_data_user
                textRole: 'text'
           }
       }
    }

    Rectangle {
        id: rectangleTabs
        width: 116
        color: "#8d8484"
        border.width: 2
        anchors.left: parent.left
        anchors.leftMargin: 6
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 6
        anchors.top: checkRect.bottom
        anchors.topMargin: 6

        ScrollView{
            id: scrollViewTab

            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            anchors.right: parent.right

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

        Column {
            id: tabs
            anchors.right: parent.right
            anchors.rightMargin: 3
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 3
            anchors.top: parent.top
            anchors.topMargin: 3
            anchors.left: parent.left
            anchors.leftMargin: 3

            Repeater {
                model: list_data_cube
                delegate: SingleCheckBox {
                    text: model.label
                    checked: model.checked
                    onClicked: {
                        list_data_cube.change_active(index, checked)

                    }
                }
            }
        }
        }
    }

    Rectangle {
        id: rectangleCubes
        color: "#e8e5ce"
        border.width: 2
        anchors.left: rectangleTabs.right
        anchors.leftMargin: 6
        anchors.right: parent.right
        anchors.rightMargin: 6
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 6
        anchors.top: checkRect.bottom
        anchors.topMargin: 6

        ScrollView{
            id: scrollView

            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            anchors.right: parent.right

            property int scrollWidth: 10

            style: ScrollViewStyle {
                id: sptScrollStyleCube

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

            GridView {
                id: grid
                anchors.right: parent.right
                anchors.rightMargin: 3
                anchors.left: parent.left
                anchors.leftMargin: 3
                anchors.bottom: parent.bottom
                anchors.bottomMargin: 3
                anchors.top: parent.top
                anchors.topMargin: 3
                cellWidth: 162
                cellHeight: 152
                model: list_data_cube
                delegate: SingleCube {
                    label: model.label
                    color_state: model.color_state
                    color_fone: model.color_fone
                    index_cube: index
                    }
            }
        }
    }

    ControlPower{
        id: powerWindow
        title: qsTr("Управление питанием")
        color: root.color

        // Обработчик сигнала на открытие основного окна
        onSignalExit: {
            powerWindow.close()     // Закрываем первое окно
            root.show()       // Показываем основное окно

        }

        onSignalPoweroff: {
            main_window.poweroff()
        }

        onSignalRestart: {
            main_window.restart()
        }
    }

    Settings{
        id:settingsWindow
        title: qsTr("Settings")
        color: root.color

        onSignalExit: {
            main_window.connection_thread_start()
            settingsWindow.close()     // Закрываем первое окно
            root.show()       // Показываем основное окно
        }
    }


    //    Connections {
    //        target: main_window

    //        // обработчик сигнала sum_result описанный в конструкторе MainWindow
    //        onSum_result: {
    //            //sum задан через arguments=['sum']
    //            sum_result.text = sum
    //        }

    //        onSub_result: {
    //            sub_result.text = sub
    //        }
    //    }
}
