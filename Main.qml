import QtQuick
import Quickshell.Io
import Caelestia.Plugins
import qs.utils

Item {
    id: root
    property SettingsObject settings: null
    readonly property string helper: Paths.toLocalFile(Qt.resolvedUrl("scripts/power-button-daemon.py"))
    readonly property bool wanted: settings?.enabled ?? true

    visible: false
    implicitWidth: 0
    implicitHeight: 0

    function daemonArgs(): var {
        return [
            "python3", helper,
            "--single", String(settings?.singleAction ?? "volume-up"),
            "--double", String(settings?.doubleAction ?? "volume-down"),
            "--double-ms", String(settings?.doubleMilliseconds ?? 350),
            "--volume-step", String(settings?.volumeStepPercent ?? 5),
            "--brightness-step", String(settings?.brightnessStepPercent ?? 5)
        ];
    }

    function restartDaemon(): void {
        daemon.running = false;
        restartTimer.restart();
    }

    onSettingsChanged: restartDaemon()
    onWantedChanged: restartDaemon()
    Component.onCompleted: restartDaemon()

    Connections {
        target: root.settings
        function onChanged(): void { root.restartDaemon(); }
    }

    Timer {
        id: restartTimer
        interval: 180
        repeat: false
        onTriggered: {
            if (!root.wanted) return;
            daemon.command = root.daemonArgs();
            daemon.running = true;
        }
    }

    Timer {
        id: crashRestart
        interval: 1200
        repeat: false
        onTriggered: {
            if (root.wanted && !daemon.running) {
                daemon.command = root.daemonArgs();
                daemon.running = true;
            }
        }
    }

    Process {
        id: daemon
        running: false
        onExited: code => {
            if (root.wanted && !restartTimer.running) crashRestart.restart();
        }
    }

}
