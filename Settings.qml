import Caelestia.Plugins

SettingsObject {
    property bool enabled: true
    SettingMeta on enabled { label: "Custom power button"; description: "Exclusively capture the physical power key while this plugin is running so logind cannot suspend on an accidental press."; icon: "power_settings_new"; inputType: SettingMeta.Switch }

    property string singleAction: "volume-up"
    SettingMeta on singleAction { label: "Single press"; description: "Action after one short press."; icon: "looks_one"; inputType: SettingMeta.SplitButton; options: ["disabled","volume-up","volume-down","mute-toggle","brightness-up","brightness-down","media-play-pause","lock","display-off"] }

    property string doubleAction: "volume-down"
    SettingMeta on doubleAction { label: "Double press"; description: "Action when a second press begins inside the double-click window."; icon: "looks_two"; inputType: SettingMeta.SplitButton; options: ["disabled","volume-up","volume-down","mute-toggle","brightness-up","brightness-down","media-play-pause","lock","display-off"] }

    property string holdAction: "display-off"
    SettingMeta on holdAction { label: "Long hold"; description: "Action fired once while the button is still held."; icon: "touch_app"; inputType: SettingMeta.SplitButton; options: ["disabled","volume-up","volume-down","mute-toggle","brightness-up","brightness-down","media-play-pause","lock","display-off"] }

    property int holdMilliseconds: 6000
    SettingMeta on holdMilliseconds { label: "Long-hold time"; description: "How long the button must stay down before the hold action fires."; icon: "timer"; inputType: SettingMeta.SpinBox; min: 1000; max: 12000; step: 250 }

    property int doubleMilliseconds: 350
    SettingMeta on doubleMilliseconds { label: "Double-click window"; description: "Maximum delay between the first release and the start of the second press."; icon: "speed"; inputType: SettingMeta.SpinBox; min: 180; max: 700; step: 10 }

    property int volumeStepPercent: 5
    SettingMeta on volumeStepPercent { label: "Volume step"; description: "Amount changed by volume-up and volume-down actions."; icon: "volume_up"; inputType: SettingMeta.SpinBox; min: 1; max: 20; step: 1 }

    property int brightnessStepPercent: 5
    SettingMeta on brightnessStepPercent { label: "Brightness step"; description: "Amount changed by brightness-up and brightness-down actions."; icon: "brightness_6"; inputType: SettingMeta.SpinBox; min: 1; max: 20; step: 1 }

}
