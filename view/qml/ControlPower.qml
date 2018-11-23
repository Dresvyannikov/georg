import QtQuick 2.5
import QtQuick.Controls 1.4
import QtQuick.Window 2.2

Window {
    id: anotherWindow
    signal signalExit   // Задаём сигнал
    signal signalPoweroff
    signal signalRestart
    width:251
    height:250
    // Кнопка для открытия главного окна приложения
    SingleButton {
        x: 80
        y: 160
        anchors.verticalCenterOffset: 29
        anchors.horizontalCenterOffset: 0
        label: qsTr("Главное окно")
        anchors.centerIn: parent
        onClicked: {
            anotherWindow.signalExit() // Вызываем сигнал
        }
    }

    SingleButton {
        x: 50
        y: 100
        anchors.verticalCenterOffset: -16
        anchors.horizontalCenterOffset: 0
        label: qsTr("Перезагрузка позиции")
        anchors.centerIn: parent
        onClicked: {
            anotherWindow.signalRestart() // Вызываем сигнал
        }
    }

    SingleButton {
        x: 50
        y: 40
        anchors.verticalCenterOffset: -72
        anchors.horizontalCenterOffset: 1
        label: qsTr("Выключение Позиции")
        anchors.centerIn: parent
        onClicked: {
            anotherWindow.signalPoweroff() // Вызываем сигнал
        }
    }
}
