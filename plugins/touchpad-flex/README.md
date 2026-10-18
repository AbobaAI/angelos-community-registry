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
The optional bar button toggles the touchpad and is hidden without a touchpad.

Requires AngelOS services InputConfig, Laptop and Gestures, with the standard
qs.config, qs.services and qs.widgets imports. Settings apply globally to niri
touchpads, not independently per hardware device. Native three-finger swipes
and application two-finger zoom keep their existing behavior. Custom angelOS
gestures require the existing gesture service's input-device access. No root
helper, additional daemon, automatic package installation or network access.

Configuration remains in niri and AngelOS when the plugin is disabled or removed.
Use the restore button before removal if you want to undo the last profile switch.

Source: https://github.com/futureUnd1ground/angelos-community-registry/tree/main/plugins/touchpad-flex
License: MIT (LICENSE).
