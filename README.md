# CaelestiaPlugin-PowerButton

A configurable Caelestia plugin for Mirai-style convertible laptops that turns the physical power key into a deliberate multi-action button instead of an easy accidental suspend trigger.

## Defaults

- single press: volume down
- double press: volume up

The defaults can be changed in Nexus → Plugins. Available mappings include disabled, volume up/down, mute, brightness up/down, media play/pause/next/previous, lock, and display off. Double-click timing and tap step sizes are configurable.

## How accidental suspend is prevented

The helper discovers the Linux input device named `Power Button`, opens it as the logged-in user, and uses `EVIOCGRAB` while the plugin is enabled. That means the button events go to this plugin rather than logind. No `/etc/systemd/logind.conf` edit, root daemon, or permanent Hyprland bind is required.

When the helper exits or the plugin is disabled, the kernel releases the grab automatically and the machine's normal power-button behavior returns.

The user must have read access to the relevant `/dev/input/event*` device. On Mirai this is already provided by membership in the `input` group.

## Gesture semantics

Mirai exposes its physical side power button through the ACPI `PNP0C0C` button driver. That kernel driver emits an instantaneous press+release pair for each ACPI notification, so userspace does not receive the physical hold duration. Because of that, this plugin intentionally supports edge gestures (single/double press) only on Mirai instead of pretending that hold/release is measurable.

The laptop firmware can still enforce its own very-long physical hold behavior independently of Linux.

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
