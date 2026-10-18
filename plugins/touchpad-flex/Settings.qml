import QtQuick
import qs.config
import qs.services
import qs.widgets

Column {
    id: root
    property var plugin
    width: parent ? parent.width : 520
    spacing: Skin.px(8)

    readonly property var builtinProfiles: ({
        "work": {"label": I18n.t("Работа", "Work"), "flags": {"tap": true, "dwt": true, "disabled-on-external-mouse": false, "natural-scroll": true}, "values": {"accel-speed": 0.0, "click-method": null, "scroll-method": "two-finger", "scroll-factor": 1.0, "drag": null, "accel-profile": "adaptive"}, "gestureSensitivity": "normal"},
        "precision": {"label": I18n.t("Точность", "Precision"), "flags": {"tap": true, "dwt": true, "disabled-on-external-mouse": false, "natural-scroll": true}, "values": {"accel-speed": -0.35, "click-method": "button-areas", "scroll-method": "two-finger", "scroll-factor": 0.8, "drag": false, "accel-profile": "flat"}, "gestureSensitivity": "low"},
        "gaming": {"label": I18n.t("Игры", "Gaming"), "flags": {"tap": false, "dwt": true, "disabled-on-external-mouse": true, "natural-scroll": false}, "values": {"accel-speed": 0.2, "click-method": "button-areas", "scroll-method": "two-finger", "scroll-factor": 1.0, "drag": false, "accel-profile": "flat"}, "gestureSensitivity": "low"},
        "tablet": {"label": I18n.t("Планшет", "Tablet"), "flags": {"tap": true, "dwt": false, "disabled-on-external-mouse": false, "natural-scroll": true}, "values": {"accel-speed": 0.15, "click-method": "clickfinger", "scroll-method": "two-finger", "scroll-factor": 1.25, "drag": null, "accel-profile": "adaptive"}, "gestureSensitivity": "high"}
    })
    readonly property var profileNames: Object.keys(root.builtinProfiles)
    property string selectedProfile: plugin ? plugin.get("profile", "work") : "work"
    property string log: ""
    readonly property bool ready: !!plugin && InputConfig.loaded

    function value(name, def) {
        const v = InputConfig.tpValue(name, String(def));
        if (v === "null" || v === "")
            return def;
        return v;
    }
    function number(name, def) {
        const n = parseFloat(value(name, def));
        return Number.isFinite(n) ? n : def;
    }
    function flag(name, def) {
        return InputConfig.tpFlag(name);
    }
    function snapshot() {
        return {
            "flags": {"tap": flag("tap"), "dwt": flag("dwt"), "disabled-on-external-mouse": flag("disabled-on-external-mouse"), "natural-scroll": InputConfig.naturalScroll},
            "values": {"accel-speed": number("accel-speed", 0), "click-method": value("click-method", "button-areas"), "tap-button-map": value("tap-button-map", "left-right-middle"), "scroll-method": value("scroll-method", "two-finger"), "scroll-factor": number("scroll-factor", 1), "drag": value("drag", "true") !== "false", "accel-profile": value("accel-profile", "adaptive")},
            "gestureSensitivity": Config.gestures.sensitivity,
            "gesturesEnabled": Config.gestures.enabled,
            "gestureMap": Object.assign({}, Config.gestures.map || {})
        };
    }
    function apply(p) {
        if (!root.ready)
            return false;
        InputConfig.save({"touchpad": {"flags": Object.assign({}, p.flags), "values": Object.assign({}, p.values)}});
        Config.gestures.sensitivity = p.gestureSensitivity;
        if (p.gesturesEnabled !== undefined)
            Config.gestures.enabled = p.gesturesEnabled;
        if (p.gestureMap !== undefined)
            Config.gestures.map = Object.assign({}, p.gestureMap);
        return true;
    }
    function applyProfile(id) {
        if (!root.ready || !root.builtinProfiles[id])
            return;
        const base = root.builtinProfiles[id] || root.builtinProfiles.work;
        const saved = plugin ? plugin.get("custom_" + id, null) : null;
        const p = saved && saved.flags && saved.values ? Object.assign({}, base, saved) : base;
        plugin.set("previous", root.snapshot());
        root.apply(p);
        root.selectedProfile = id;
        if (plugin)
            plugin.set("profile", id);
        root.log = I18n.t("Профиль отправлен на проверку niri: ", "Profile sent for niri validation: ") + p.label;
    }
    function saveProfile() {
        if (!root.ready)
            return;
        const id = root.selectedProfile;
        plugin.set("custom_" + id, root.snapshot());
        root.log = I18n.t("Текущие параметры сохранены в профиле «", "Current settings saved to profile “") + id + "»";
    }
    function undoProfile() {
        const previous = plugin ? plugin.get("previous", null) : null;
        if (previous && root.apply(previous)) {
            plugin.set("previous", null);
            root.log = I18n.t("Предыдущие параметры отправлены на восстановление", "Previous settings sent for restoration");
        }
    }
    function setFlag(name, on) {
        if (!root.ready)
            return;
        const flags = {};
        flags[name] = on;
        InputConfig.save({"touchpad": {"flags": flags}});
    }
    function setValue(name, v) {
        if (!root.ready)
            return;
        const values = {};
        values[name] = v;
        InputConfig.save({"touchpad": {"values": values}});
    }

    PxGroup {
        enabled: root.ready
        title: I18n.t("Профили", "Profiles")
        icon: "sparkle"
        width: parent.width
        SettingRow {
            label: I18n.t("Быстрый профиль", "Quick profile")
            PxCombo {
                model: root.profileNames.map(id => ({"label": root.builtinProfiles[id].label, "value": id}))
                currentValue: root.selectedProfile
                onActivated: v => root.applyProfile(v)
            }
        }
        PxButton {
            text: I18n.t("Сохранить текущие параметры в этот профиль", "Save current settings to this profile")
            icon: "save"
            onClicked: root.saveProfile()
        }
        PxButton {
            text: I18n.t("Вернуть параметры до переключения", "Restore settings before switching")
            enabled: !!root.plugin && !!root.plugin.get("previous", null)
            onClicked: root.undoProfile()
        }
        PxText {
            visible: root.log !== ""
            width: parent.width
            wrapMode: Text.Wrap
            kind: "tiny"
            color: Skin.ok
            text: root.log
        }
    }

    PxGroup {
        enabled: root.ready
        title: I18n.t("Основное", "Basics")
        icon: "touchpad"
        width: parent.width
        SettingRow { label: I18n.t("Тачпад включён", "Touchpad on"); PxToggle { checked: !InputConfig.touchpadOff; onToggled: v => Laptop.setTouchpad(v) } }
        SettingRow { label: I18n.t("Касание вместо клика", "Tap to click"); PxToggle { checked: InputConfig.tpFlag("tap"); onToggled: v => root.setFlag("tap", v) } }
        SettingRow { label: I18n.t("Не мешать при наборе", "Disable while typing"); PxToggle { checked: InputConfig.tpFlag("dwt"); onToggled: v => root.setFlag("dwt", v) } }
        SettingRow { label: I18n.t("Отключать при подключении мыши", "Disable with an external mouse"); PxToggle { checked: InputConfig.tpFlag("disabled-on-external-mouse"); onToggled: v => root.setFlag("disabled-on-external-mouse", v) } }
        SettingRow { label: I18n.t("Естественная прокрутка", "Natural scrolling"); PxToggle { checked: InputConfig.naturalScroll; onToggled: v => InputConfig.save({"naturalScroll": v}) } }
        SettingRow {
            label: I18n.t("Скорость указателя", "Pointer speed")
            PxSlider { width: Skin.px(140); from: -1; to: 1; stepSize: 0.05; decimals: 2; live: false; value: root.number("accel-speed", 0); onReleased: v => root.setValue("accel-speed", v) }
        }
        SettingRow {
            label: I18n.t("Скорость прокрутки", "Scroll speed")
            PxSlider { width: Skin.px(140); from: 0.2; to: 3; stepSize: 0.1; decimals: 1; suffix: "×"; live: false; value: root.number("scroll-factor", 1); onReleased: v => root.setValue("scroll-factor", Math.abs(v - 1) < 0.05 ? null : v) }
        }
    }

    PxGroup {
        enabled: root.ready
        title: I18n.t("Клики и прокрутка", "Clicks and scrolling")
        icon: "mouse"
        width: parent.width
        SettingRow {
            label: I18n.t("Правый клик", "Right click")
            PxSegmented { model: [{"label": I18n.t("угол", "corner"), "value": "button-areas"}, {"label": I18n.t("два пальца", "two fingers"), "value": "clickfinger"}]; currentValue: root.value("click-method", "button-areas"); onActivated: v => root.setValue("click-method", v === "button-areas" ? null : v) }
        }
        SettingRow {
            label: I18n.t("Прокрутка", "Scrolling")
            PxSegmented { model: [{"label": I18n.t("двумя пальцами", "two fingers"), "value": "two-finger"}, {"label": I18n.t("по краю", "edge"), "value": "edge"}]; currentValue: root.value("scroll-method", "two-finger"); onActivated: v => root.setValue("scroll-method", v === "two-finger" ? null : v) }
        }
        SettingRow { label: I18n.t("Перетаскивание касанием", "Tap and drag"); PxToggle { checked: root.value("drag", "true") !== "false"; onToggled: v => root.setValue("drag", v ? null : false) } }
        SettingRow {
            label: I18n.t("Касания 2 / 3 пальцами", "Two / three finger taps")
            PxCombo { model: [{"label": I18n.t("правый / средний", "right / middle"), "value": "left-right-middle"}, {"label": I18n.t("средний / правый", "middle / right"), "value": "left-middle-right"}]; currentValue: root.value("tap-button-map", "left-right-middle"); onActivated: v => root.setValue("tap-button-map", v) }
        }
        SettingRow {
            label: I18n.t("Ускорение", "Acceleration")
            PxSegmented { model: [{"label": I18n.t("плавное", "adaptive"), "value": "adaptive"}, {"label": I18n.t("ровное", "flat"), "value": "flat"}]; currentValue: root.value("accel-profile", "adaptive"); onActivated: v => root.setValue("accel-profile", v === "adaptive" ? null : v) }
        }
    }

    PxGroup {
        enabled: root.ready
        title: I18n.t("Жесты angelOS", "angelOS gestures")
        icon: "sparkle"
        width: parent.width
        SettingRow { label: I18n.t("Включены", "Enabled"); PxToggle { checked: Config.gestures.enabled; onToggled: v => Config.gestures.enabled = v } }
        SettingRow {
            label: I18n.t("Чувствительность", "Sensitivity")
            PxSegmented { model: [{"label": I18n.t("низкая", "low"), "value": "low"}, {"label": I18n.t("обычная", "normal"), "value": "normal"}, {"label": I18n.t("высокая", "high"), "value": "high"}]; currentValue: Config.gestures.sensitivity; onActivated: v => Config.gestures.sensitivity = v }
        }
        Repeater {
            model: Gestures.gestures
            SettingRow {
                id: gestureRow
                required property string modelData
                label: Gestures.label(modelData)
                PxCombo { model: Gestures.actions; currentValue: Gestures.actionOf(gestureRow.modelData); onActivated: v => Gestures.setAction(gestureRow.modelData, v) }
            }
        }
    }
    PxText {
        width: parent.width
        wrapMode: Text.Wrap
        text: I18n.t("Настройки общие для тачпадов niri. Жесты 3 пальцами и масштаб 2 пальцами остаются у композитора и приложений. ", "Settings apply to niri touchpads globally. Three-finger swipes and two-finger zoom remain controlled by the compositor and apps. ") + (Laptop.hasTouchpad ? "" : I18n.t("Тачпад сейчас не найден. ", "No touchpad detected. ")) + I18n.t("Состояние жестов: ", "Gesture status: ") + Gestures.status
    }
    PxText {
        width: parent.width
        wrapMode: Text.Wrap
        text: InputConfig.log
        visible: text !== ""
    }
}
