import Caelestia.Plugins

SettingsObject {
    id: root

    readonly property list<string> actions: ["disabled","volume-up","volume-down","mute-toggle","brightness-up","brightness-down","media-play-pause","media-next","media-previous","lock","display-off"]

    property bool enabled: true
    SettingMeta on enabled { label: "Custom power button"; description: "Exclusively capture the physical power key so accidental presses do not reach logind."; icon: "power_settings_new"; inputType: SettingMeta.Switch }

    property string singleAction: "volume-up"
    SettingMeta on singleAction { label: "Short press"; description: "Action after one short click."; icon: "looks_one"; inputType: SettingMeta.SplitButton; options: root.actions }

    property string doubleAction: "volume-down"
    SettingMeta on doubleAction { label: "Double press"; description: "Action after two short clicks."; icon: "looks_two"; inputType: SettingMeta.SplitButton; options: root.actions }

    property string holdAction: "volume-up"
    SettingMeta on holdAction { label: "Press and hold"; description: "Starts after the repeat delay and continues while the first press stays held. Repeatable actions ramp continuously."; icon: "south"; inputType: SettingMeta.SplitButton; options: root.actions }

    property string secondHoldAction: "volume-down"
    SettingMeta on secondHoldAction { label: "Click, then hold"; description: "Short click followed immediately by a held second press. Useful as the opposite continuous direction."; icon: "north"; inputType: SettingMeta.SplitButton; options: root.actions }

    property string longAction: "display-off"
    SettingMeta on longAction { label: "Very long hold"; description: "Separate safety action after the full long-hold time. It stops any continuous hold action first."; icon: "power_settings_new"; inputType: SettingMeta.SplitButton; options: root.actions }

    property int longMilliseconds: 6000
    SettingMeta on longMilliseconds { label: "Very long-hold time"; description: "Default is six seconds before Display off."; icon: "timer"; inputType: SettingMeta.SpinBox; min: 1500; max: 12000; step: 250 }

    property int doubleMilliseconds: 350
    SettingMeta on doubleMilliseconds { label: "Double-click window"; description: "Maximum delay between the first release and the second press."; icon: "speed"; inputType: SettingMeta.SpinBox; min: 180; max: 700; step: 10 }

    property int repeatDelayMilliseconds: 280
    SettingMeta on repeatDelayMilliseconds { label: "Hold start delay"; description: "How quickly holding turns into continuous control."; icon: "touch_app"; inputType: SettingMeta.SpinBox; min: 120; max: 900; step: 20 }

    property int repeatMilliseconds: 90
    SettingMeta on repeatMilliseconds { label: "Hold repeat interval"; description: "Lower values make continuous adjustments feel faster and smoother."; icon: "fast_forward"; inputType: SettingMeta.SpinBox; min: 50; max: 300; step: 10 }

    property int volumeStepPercent: 5
    SettingMeta on volumeStepPercent { label: "Tap volume step"; description: "Volume change for a normal short action."; icon: "volume_up"; inputType: SettingMeta.SpinBox; min: 1; max: 20; step: 1 }

    property int repeatVolumeStepPercent: 1
    SettingMeta on repeatVolumeStepPercent { label: "Held volume step"; description: "Volume change per repeat while holding. One percent keeps the ramp gradual."; icon: "tune"; inputType: SettingMeta.SpinBox; min: 1; max: 10; step: 1 }

    property int brightnessStepPercent: 5
    SettingMeta on brightnessStepPercent { label: "Tap brightness step"; description: "Brightness change for a normal short action."; icon: "brightness_6"; inputType: SettingMeta.SpinBox; min: 1; max: 20; step: 1 }

    property int repeatBrightnessStepPercent: 1
    SettingMeta on repeatBrightnessStepPercent { label: "Held brightness step"; description: "Brightness change per repeat while holding."; icon: "tune"; inputType: SettingMeta.SpinBox; min: 1; max: 10; step: 1 }
}
