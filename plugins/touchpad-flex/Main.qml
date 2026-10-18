import QtQuick
import Quickshell
import Quickshell.Io
import qs.config
import qs.services
import "GestureOptions.js" as Extra

Scope {
    id: root
    property var plugin
    property bool ownsGestures: false
    readonly property bool nativeEnabled: plugin ? plugin.get("nativeBeforeExtra", true) !== false : true
    readonly property bool wanted: !!plugin && plugin.get("extraEnabled", false) && !Shell.dev && !Shell.locked && !Shell.setupLocked && !InputConfig.touchpadOff
    readonly property string specification: JSON.stringify(plugin ? plugin.get("thresholds", {}) : {})
    readonly property string sensitivity: ["low", "normal", "high"].includes(Config.gestures.sensitivity) ? Config.gestures.sensitivity : "normal"
    function releaseNative() {
        if (ownsGestures) {
            Config.gestures.enabled = nativeEnabled;
            ownsGestures = false;
            if (plugin) plugin.set("nativeBeforeExtra", null);
        }
    }
    function sync() {
        daemon.running = false;
        if (root.wanted && !ownsGestures) {
            if (plugin.get("nativeBeforeExtra", null) === null)
                plugin.set("nativeBeforeExtra", Config.gestures.enabled);
            Config.gestures.enabled = false;
            ownsGestures = true;
        } else if (!root.wanted) releaseNative();
        restart.restart();
    }
    onWantedChanged: sync()
    onSpecificationChanged: sync()
    onSensitivityChanged: sync()
    Component.onCompleted: {
        sync();
    }
    Component.onDestruction: { releaseNative(); Runtime.status = "off"; }
    function activate(name) {
        const native = ["pinchIn", "pinchOut", "swipe4Left", "swipe4Right", "swipe4Down", "edgeLeft", "edgeRight", "tap3", "tap4", "hold3"].includes(name);
        if (!root.wanted || (!Extra.ids.includes(name) && !native) || (native && !nativeEnabled)) return;
        Runtime.lastGesture = Extra.label(name, I18n.t("ru", "en") === "ru");
        const action = Gestures.actionOf(name);
        if (action === "command") {
            const command = String(plugin.get("commands", {})[name] || "").trim();
            if (command) Shell.exec(["sh", "-c", command]);
        } else if (action !== "none") Gestures.run(name);
    }
    Timer {
        id: restart
        interval: 250
        onTriggered: {
            Runtime.status = root.wanted ? "starting" : "off";
            daemon.running = root.wanted;
        }
    }
    Timer { id: retry; interval: 5000; onTriggered: if (root.wanted) root.sync() }
    Process {
        id: daemon
        command: ["python3", "-u", root.plugin ? root.plugin.dir + "/gesture-watch.py" : "", "--config", root.specification, "--sensitivity", root.sensitivity]
        stdout: SplitParser {
            onRead: line => {
                if (line.startsWith("gesture ")) root.activate(line.slice(8));
                else if (["ready", "noperm", "notouchpad"].includes(line)) Runtime.status = line;
            }
        }
        stderr: StdioCollector {}
        onExited: code => {
            if (root.wanted && !restart.running) {
                if (code !== 0) Runtime.status = "error";
                root.releaseNative();
                retry.restart();
            }
        }
    }
}
