# CaelestiaPlugin-PowerButton

A configurable Caelestia plugin for Mirai-style convertible laptops that turns the physical power key into a deliberate multi-action button instead of an easy accidental suspend trigger.

## Defaults

- single press: volume up
- double press: volume down
- hold for 6 seconds: display off

The defaults can be changed in Nexus → Plugins. Available mappings are disabled, volume up/down, mute toggle, brightness up/down, media play/pause, lock, and display off. Volume/brightness step size, double-click timing, and long-hold timing are configurable.

## How accidental suspend is prevented

The helper discovers the Linux input device named `Power Button`, opens it as the logged-in user, and uses `EVIOCGRAB` while the plugin is enabled. That means the button events go to this plugin rather than logind. No `/etc/systemd/logind.conf` edit, root daemon, or permanent Hyprland bind is required.

When the helper exits or the plugin is disabled, the kernel releases the grab automatically and the machine's normal power-button behavior returns.

The user must have read access to the relevant `/dev/input/event*` device. On Mirai this is already provided by membership in the `input` group.

## Gesture semantics

A single press is delayed only until the configured double-click window expires. A valid double press cancels the pending single action. A long hold fires once while the button is still held, and releasing after a long hold never produces an extra single/double action. Kernel repeat events are ignored.

## Install

Clone or symlink this repository to:

```text
~/.local/share/caelestia/plugins/power-button
```

Then enable **PowerButton** in Nexus → Plugins.

## Verification

Safe hardware discovery:

```sh
./scripts/power-button-daemon.py --probe
```

State-machine regression tests are in `tests/test_state_machine.py` and require only Python's standard library.

License: GPL-3.0-or-later.
