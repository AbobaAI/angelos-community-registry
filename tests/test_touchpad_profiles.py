"""Exercise the production profile functions without writing to niri or real settings."""
from pathlib import Path
import json
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which('node'), 'Node is required for profile JS checks')
class TouchpadProfiles(unittest.TestCase):
    def test_profile_roundtrip_and_undo(self):
        source = (ROOT / 'plugins/touchpad-flex/Settings.qml').read_text()
        functions = source[source.index('    function value('):source.index('    PxGroup {')]
        profiles = source.split('readonly property var builtinProfiles: (', 1)[1].split('\n    })', 1)[0] + '\n    }'
        script = r'''
const vm = require('node:vm');
const assert = require('node:assert/strict');
const input = JSON.parse(process.argv[1]);
const saved = {};
let writes = [];
const sandbox = {
  I18n: {t: (ru,en) => en},
  plugin: {get: (k,d) => k in saved ? saved[k] : d, set: (k,v) => saved[k] = v},
  InputConfig: {tpFlag: () => false, tpValue: (k,d) => d, naturalScroll: false,
                save: change => writes.push(change)},
  Config: {gestures: {enabled: false, sensitivity: 'normal', map: {tap4: 'lock'}}}
};
sandbox.root = sandbox;
vm.createContext(sandbox);
vm.runInContext('var builtinProfiles = ' + input.profiles + '; var ready = true; var selectedProfile = "work"; var log = "";\n' + input.functions, sandbox);
const plain = obj => JSON.parse(JSON.stringify(obj));
// Saving false flags must not silently turn tap or disable-while-typing on.
sandbox.saveProfile();
assert.equal(saved.custom_work.flags.tap, false);
assert.equal(saved.custom_work.flags.dwt, false);
sandbox.Config.gestures.map = {tap4: 'angel'};
sandbox.applyProfile('work');
assert.equal(writes[0].touchpad.flags.tap, false);
assert.equal(sandbox.Config.gestures.enabled, false);
assert.deepEqual(plain(sandbox.Config.gestures.map), {tap4: 'lock'});
sandbox.undoProfile();
assert.deepEqual(plain(sandbox.Config.gestures.map), {tap4: 'angel'});
assert.equal(saved.previous, null);
for (const id of ['precision', 'gaming', 'tablet']) {
  sandbox.applyProfile(id);
  assert.ok(writes.at(-1).touchpad.values['accel-speed'] >= -1);
  assert.ok(writes.at(-1).touchpad.values['scroll-factor'] > 0);
}
const count = writes.length;
sandbox.applyProfile('../invalid');
assert.equal(writes.length, count);
sandbox.ready = false;
sandbox.applyProfile('work');
sandbox.setValue('scroll-factor', 2);
sandbox.setFlag('tap', true);
assert.equal(writes.length, count);
console.log('profile save/apply/undo and unloaded-state checks passed');
'''
        result = subprocess.run(['node', '-e', script, json.dumps({'functions': functions, 'profiles': profiles})], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
