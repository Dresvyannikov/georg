import QtQuick 2.5
import QtQuick.Controls 1.3
import QtQuick.Controls.Styles 1.4

Item {
    id: idGrid

    property int iNumcolums: 3
    property int iMarginGrid: 2

    ListModel {
        id: appModel

        ListElement { colorR: "red"}
        ListElement { colorR: "green" }
        ListElement { colorR: "blue" }
        ListElement { colorR: "cyan"}
        ListElement { colorR: "yellow"}
        ListElement { colorR: "blue" }
        ListElement { colorR: "lightgray" }
        ListElement { colorR: "red" }
        ListElement { colorR: "green" }
        ListElement { colorR: "blue" }
        ListElement { colorR: "cyan" }
        ListElement { colorR: "yellow" }
        ListElement { colorR: "lightgray" }
        ListElement { colorR: "blue" }
    }

    ScrollView {

        id: scrollView

        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right

        anchors.leftMargin: iMarginGrid
        anchors.rightMargin: iMarginGrid

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

        GridView {
            id: grid

            width: parent.width; height: parent.height

            model: appModel

            property int iSizeThumb: scrollView.width/3

            cellWidth: iSizeThumb; cellHeight: iSizeThumb

            delegate: Item {
                width: grid.cellWidth; height: grid.cellHeight
                Rectangle { color: colorR; anchors.fill: parent; anchors.margins: 2}
            }

            onHeightChanged: {

//                if ( height >= contentItem.height )
//                    grid.iSizeThumb = scrollView.width/3
//                else
//                    grid.iSizeThumb = scrollView.width/3 - 3

                if ((idSptGridThumbs.width - scrollView.scrollWidth) > width)
                    grid.iSizeThumb = scrollView.width/3 - 3
                else
                    grid.iSizeThumb = scrollView.width/3

            }
        }
    }
}
