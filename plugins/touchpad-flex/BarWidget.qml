import QtQuick
import qs.config
import qs.services
import qs.widgets

Item {
    id: root
    property var plugin
    property string screenName
    implicitWidth: button.implicitWidth
    implicitHeight: button.implicitHeight
    visible: Laptop.hasTouchpad

    PxButton {
        id: button
        anchors.fill: parent
        compact: true
        enabled: InputConfig.loaded
        icon: "touchpad"
        text: InputConfig.touchpadOff ? I18n.t("выкл", "off") : I18n.t("тач", "pad")
        onClicked: Laptop.setTouchpad(InputConfig.touchpadOff)
    }
}
