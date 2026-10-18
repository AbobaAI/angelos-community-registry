# Touchpad Flex

Install **Гибкий тачпад / Touchpad Flex** from AngelOS Community Store, then open
Settings → Plugins → Гибкий тачпад. The page is also placed beside Touchpad.

Four editable profiles: Work, Precision, Gaming and Tablet. Select a profile
to apply it, adjust the controls, and use **Save current settings** to remember
your version. **Restore settings before switching** returns to the previous
touchpad and gesture settings. Changes use AngelOS InputConfig, including its
niri validation and configuration backups; the page displays the validation log.
The plugin never reapplies a profile automatically at startup or on enable.

Controls include pointer speed and acceleration, scroll method and speed,
natural scrolling, tap to click, tap dragging, two/three-finger button mapping,
disable while typing, and disable when an external mouse is connected. Gesture
assignments, sensitivity and enable state are saved with custom profiles.
There is no bar button; touchpad enable/disable is available in the settings.

Version 1.1 adds drag lock, disable while using a trackpoint, disabled scrolling
and a 0.1–5× scroll speed range. **Extended recognition**, off by default, adds
21 gestures: three/five-finger pinch/spread, five-finger tap, four/five-finger
holds, top/bottom edges, four-finger diagonal swipes and eight five-finger swipe
directions. Assign any native action or a custom shell command (Enter saves it).
Holds fire on release. Hardware must report the required number of fingers.
Eight threshold sliders tune distance, pinch ratio, tap/hold time, movement
tolerance, edge zone/travel and cooldown. Profiles include these settings and
commands. The watcher stops while locked and when the touchpad is disabled.
It reads touchpad events without grabbing them. Native three-finger navigation
stays with niri. While the extended mode is active it handles the old AngelOS
gesture assignments too, temporarily pausing the stock watcher to prevent
five-finger swipes from triggering four-finger actions as well. Disabling the
mode, locking or unloading the plugin restores the stock watcher's enable state.

Requires AngelOS services InputConfig, Laptop and Gestures, with the standard
qs.config, qs.services and qs.widgets imports. Settings apply globally to niri
touchpads, not independently per hardware device. Native three-finger swipes
and application two-finger zoom keep their existing behavior. Custom angelOS
gestures require the existing gesture service's input-device access. No root
helper, automatic package installation or network access. Extended recognition
starts an optional Python watcher that uses the same input access as AngelOS.

Configuration remains in niri and AngelOS when the plugin is disabled or removed.
Use the restore button before removal if you want to undo the last profile switch.

Source: https://github.com/futureUnd1ground/angelos-community-registry/tree/main/plugins/touchpad-flex
License: MIT (LICENSE).
