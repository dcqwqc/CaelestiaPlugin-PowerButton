import Caelestia.Plugins

SettingsObject {
    id: root
    readonly property list<string> actions: ["disabled","volume-up","volume-down","mute-toggle","brightness-up","brightness-down","media-play-pause","media-next","media-previous","lock","display-off"]

    property bool enabled: true
    SettingMeta on enabled { label: "Custom power button"; description: "Exclusively capture Mirai's ACPI power button so accidental presses do not reach logind."; icon: "power_settings_new"; inputType: SettingMeta.Switch }

    property string singleAction: "volume-up"
    SettingMeta on singleAction { label: "Single press"; description: "Default: raise volume by one tap step."; icon: "looks_one"; inputType: SettingMeta.SplitButton; options: root.actions }

    property string doubleAction: "volume-down"
    SettingMeta on doubleAction { label: "Double press"; description: "Default: lower volume by one tap step."; icon: "looks_two"; inputType: SettingMeta.SplitButton; options: root.actions }

    property int doubleMilliseconds: 350
    SettingMeta on doubleMilliseconds { label: "Double-click window"; description: "Maximum delay between two ACPI button events."; icon: "speed"; inputType: SettingMeta.SpinBox; min: 180; max: 700; step: 10 }

    property int volumeStepPercent: 5
    SettingMeta on volumeStepPercent { label: "Volume step"; description: "Volume change for volume-up/down actions."; icon: "volume_up"; inputType: SettingMeta.SpinBox; min: 1; max: 20; step: 1 }

    property int brightnessStepPercent: 5
    SettingMeta on brightnessStepPercent { label: "Brightness step"; description: "Brightness change for brightness-up/down actions."; icon: "brightness_6"; inputType: SettingMeta.SpinBox; min: 1; max: 20; step: 1 }
}
