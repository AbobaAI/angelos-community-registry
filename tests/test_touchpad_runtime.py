"""Run production gesture dispatch against process doubles, never real commands."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]/'plugins/touchpad-flex'
RUNNER='/usr/lib/qt6/bin/qmltestrunner' if Path('/usr/lib/qt6/bin/qmltestrunner').exists() else shutil.which('qmltestrunner')


@unittest.skipUnless(RUNNER,'QtTest required')
class TouchpadRuntime(unittest.TestCase):
    def test_dispatch_and_lock(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            def write(name,text):
                p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
            write('Main.qml',(ROOT/'Main.qml').read_text().replace('id: root','id: root\n    property alias worker: daemon',1))
            for name in ['Runtime.qml','GestureOptions.js','qmldir']:
                write(name,(ROOT/name).read_text())
            write('imports/Quickshell/qmldir','module Quickshell\nScope 1.0 Scope.qml\n')
            write('imports/Quickshell/Scope.qml','import QtQuick\nItem {}')
            write('imports/Quickshell/Io/qmldir','module Quickshell.Io\nProcess 1.0 Process.qml\nSplitParser 1.0 SplitParser.qml\nStdioCollector 1.0 StdioCollector.qml\n')
            write('imports/Quickshell/Io/Process.qml','import QtQuick\nQtObject { property bool running: false; property var command; property QtObject stdout; property QtObject stderr; signal exited(int code) }')
            write('imports/Quickshell/Io/SplitParser.qml','import QtQuick\nQtObject { signal read(string line) }')
            write('imports/Quickshell/Io/StdioCollector.qml','import QtQuick\nQtObject {}')
            write('imports/qs/config/qmldir','module qs.config\nsingleton I18n 1.0 I18n.qml\nsingleton Config 1.0 Config.qml\n')
            write('imports/qs/config/Config.qml','pragma Singleton\nimport QtQuick\nQtObject {property QtObject gestures: QtObject {property bool enabled: true}}')
            write('imports/qs/config/I18n.qml','pragma Singleton\nimport QtQuick\nQtObject { function t(ru,en) { return en } }')
            write('imports/qs/services/qmldir','module qs.services\nsingleton Shell 1.0 Shell.qml\nsingleton InputConfig 1.0 InputConfig.qml\nsingleton Gestures 1.0 Gestures.qml\n')
            write('imports/qs/services/Shell.qml','pragma Singleton\nimport QtQuick\nQtObject { property bool dev: false; property bool locked: false; property bool setupLocked: false; property var argv: []; function exec(args) {argv=args} }')
            write('imports/qs/services/InputConfig.qml','pragma Singleton\nimport QtQuick\nQtObject { property bool touchpadOff: false }')
            write('imports/qs/services/Gestures.qml','pragma Singleton\nimport QtQuick\nQtObject { property string action: "none"; property string last: ""; function actionOf(g) {return action} function run(g) {last=g} }')
            write('tst_runtime.qml','''import QtQuick
import QtTest
import qs.services
import qs.config
import "."
TestCase {
 name: "TouchpadRuntime"
 property var saved: ({})
 Main {id: service; plugin: ({dir:"/test",get:(k,d)=> k in saved ? saved[k] : k === "extraEnabled" ? true : k === "commands" ? {tap5:"playerctl play-pause"} : d,set:(k,v)=>{const n=Object.assign({},saved);n[k]=v;saved=n}})}
 function init() {Shell.locked=false; Shell.setupLocked=false; Shell.dev=false; InputConfig.touchpadOff=false; Shell.argv=[]; Gestures.action="none"; Gestures.last="";}
 function test_custom_command() { Gestures.action="command"; service.activate("tap5"); compare(Shell.argv.join("|"),"sh|-c|playerctl play-pause"); }
 function test_unknown_and_unassigned() {Gestures.action="command";service.activate("unknown");service.activate("hold5");compare(Shell.argv.length,0);}
 function test_native_dispatch() {Gestures.action="launcher";service.activate("hold4");compare(Gestures.last,"hold4");}
 function test_lock_and_disabled_touchpad() {Gestures.action="command";Shell.locked=true;service.activate("tap5");Shell.locked=false;InputConfig.touchpadOff=true;service.activate("tap5");compare(Shell.argv.length,0);}
 function test_worker_stops_when_locked() {tryCompare(service.worker,"running",true);Shell.locked=true;tryCompare(service.worker,"running",false);}
 function test_native_worker_restored_on_lock() {service.sync();compare(Config.gestures.enabled,false);Shell.locked=true;compare(Config.gestures.enabled,true);Shell.locked=false;compare(Config.gestures.enabled,false);}
 function test_reconfigure_does_not_restart_both_workers() {service.sync();service.worker.exited(0);compare(Config.gestures.enabled,false);}
}
''')
            result=subprocess.run([RUNNER,'-input',str(root),'-import',str(root/'imports')],capture_output=True,text=True,env={**os.environ,'QT_QPA_PLATFORM':'offscreen','QT_QUICK_BACKEND':'software'},timeout=20)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
