# CaelestiaPlugin-PowerButton

A configurable Caelestia plugin for Mirai-style convertible laptops that turns the physical power key into a deliberate multi-action button instead of an easy accidental suspend trigger.

## Defaults

- single press: volume up
- double press: volume down
- press and hold: continuously raise volume
- short click, then hold the second press: continuously lower volume
- hold for 6 seconds: stop the ramp and turn the display off

The defaults can be changed in Nexus → Plugins. Every gesture is configurable. Available mappings include disabled, volume up/down, mute, brightness up/down, media play/pause/next/previous, lock, and display off. The first hold and click-then-hold mappings are separate. Repeat start delay, repeat interval, tap step sizes, held step sizes, double-click timing, and the six-second safety action are configurable.

## How accidental suspend is prevented

The helper discovers the Linux input device named `Power Button`, opens it as the logged-in user, and uses `EVIOCGRAB` while the plugin is enabled. That means the button events go to this plugin rather than logind. No `/etc/systemd/logind.conf` edit, root daemon, or permanent Hyprland bind is required.

When the helper exits or the plugin is disabled, the kernel releases the grab automatically and the machine's normal power-button behavior returns.

The user must have read access to the relevant `/dev/input/event*` device. On Mirai this is already provided by membership in the `input` group.

## Gesture semantics

A single press is delayed only until the configured double-click window expires. A valid double press cancels the pending single action. Holding the first press starts its hold mapping after a short delay and repeats repeatable actions until release. A short click followed by a held second press uses the separate click-then-hold mapping. At the configured very-long-hold threshold (six seconds by default), repeating stops and the safety action fires once. Releasing after either hold mode never leaks a single/double action. Kernel repeat events are ignored.

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
