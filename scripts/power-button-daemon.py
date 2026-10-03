#!/usr/bin/env python3
import argparse, fcntl, glob, os, select, signal, struct, subprocess, sys, time

EV_KEY = 1
KEY_POWER = 116
EVIOCGRAB = 1074021776
EVENT = struct.Struct("llHHi")


class GestureEngine:
    def __init__(self, single, double, hold, second_hold, long_hold,
                 double_ms=350, repeat_delay_ms=280, repeat_ms=90, long_ms=6000):
        self.single_cb = single
        self.double_cb = double
        self.hold_cb = hold
        self.second_hold_cb = second_hold
        self.long_cb = long_hold
        self.double_s = max(0.08, double_ms / 1000.0)
        self.repeat_delay_s = max(0.08, repeat_delay_ms / 1000.0)
        self.repeat_s = max(0.04, repeat_ms / 1000.0)
        self.long_s = max(self.repeat_delay_s, long_ms / 1000.0)

        self.pressed = False
        self.second_press = False
        self.pending_single = False
        self.repeating = False
        self.repeat_count = 0
        self.long_fired = False
        self.single_deadline = 0.0
        self.repeat_deadline = 0.0
        self.long_deadline = 0.0

    def next_deadline(self):
        deadlines = []
        if self.pressed:
            if not self.repeating:
                deadlines.append(self.repeat_deadline)
            if self.repeating and not self.long_fired:
                deadlines.append(self.repeat_deadline)
            if not self.long_fired:
                deadlines.append(self.long_deadline)
        elif self.pending_single:
            deadlines.append(self.single_deadline)
        return min(deadlines) if deadlines else None

    def _repeat_cb(self):
        return self.second_hold_cb if self.second_press else self.hold_cb

    def tick(self, now):
        if self.pressed and not self.long_fired and now >= self.long_deadline:
            self.long_cb()
            self.long_fired = True
            self.pending_single = False
            self.repeating = False
            return

        if self.pressed and not self.long_fired and now >= self.repeat_deadline:
            self._repeat_cb()(self.repeat_count > 0)
            self.repeat_count += 1
            self.repeating = True
            self.pending_single = False
            self.repeat_deadline = now + self.repeat_s

        if self.pending_single and not self.pressed and now >= self.single_deadline:
            self.single_cb()
            self.pending_single = False

    def key(self, value, now):
        self.tick(now)

        if value == 1:
            if self.pressed:
                return
            self.pressed = True
            self.second_press = self.pending_single and now <= self.single_deadline
            self.repeating = False
            self.repeat_count = 0
            self.long_fired = False
            self.repeat_deadline = now + self.repeat_delay_s
            self.long_deadline = now + self.long_s
            return

        if value != 0 or not self.pressed:
            return

        self.pressed = False

        if self.long_fired or self.repeating:
            self.pending_single = False
            self.second_press = False
            self.long_fired = False
            self.repeating = False
            self.repeat_count = 0
            return

        if self.second_press:
            self.double_cb()
            self.pending_single = False
            self.second_press = False
        else:
            self.pending_single = True
            self.single_deadline = now + self.double_s


class ActionRunner:
    REPEATABLE = {"volume-up", "volume-down", "brightness-up", "brightness-down", "media-next", "media-previous"}

    def __init__(self, args):
        self.args = args

    def spawn(self, command):
        try:
            subprocess.Popen(command, start_new_session=True,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as exc:
            print(f"PowerButton: action failed: {exc}", file=sys.stderr, flush=True)

    def run(self, action, repeated=False):
        if action == "disabled":
            return
        if repeated and action not in self.REPEATABLE:
            return

        volume_step = self.args.repeat_volume_step if repeated else self.args.volume_step
        brightness_step = self.args.repeat_brightness_step if repeated else self.args.brightness_step

        if action == "volume-up":
            self.spawn(["wpctl", "set-volume", "-l", "1.0", "@DEFAULT_AUDIO_SINK@", f"{volume_step}%+"])
        elif action == "volume-down":
            self.spawn(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", f"{volume_step}%-"])
        elif action == "mute-toggle":
            self.spawn(["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "toggle"])
        elif action == "brightness-up":
            self.spawn(["brightnessctl", "set", f"{brightness_step}%+"])
        elif action == "brightness-down":
            self.spawn(["brightnessctl", "set", f"{brightness_step}%-"])
        elif action == "media-play-pause":
            self.spawn(["caelestia", "shell", "mpris", "playPause"])
        elif action == "media-next":
            self.spawn(["caelestia", "shell", "mpris", "next"])
        elif action == "media-previous":
            self.spawn(["caelestia", "shell", "mpris", "previous"])
        elif action == "lock":
            self.spawn(["caelestia", "shell", "lock", "lock"])
        elif action == "display-off":
            self.spawn(["hyprctl", "dispatch", "dpms", "off"])


def event_name(path):
    event = os.path.basename(path)
    try:
        with open(f"/sys/class/input/{event}/device/name", encoding="utf-8") as handle:
            return handle.read().strip()
    except OSError:
        return ""


def candidates():
    paths = sorted(glob.glob("/dev/input/event*"))
    exact = [path for path in paths if event_name(path).lower() == "power button"]
    return exact or [path for path in paths if "power" in event_name(path).lower()]


class PowerDevice:
    def __init__(self, path):
        self.path = path
        self.fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
        fcntl.ioctl(self.fd, EVIOCGRAB, 1)

    def close(self):
        if self.fd is None:
            return
        try:
            fcntl.ioctl(self.fd, EVIOCGRAB, 0)
        except OSError:
            pass
        try:
            os.close(self.fd)
        except OSError:
            pass
        self.fd = None


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--single", default="volume-up")
    parser.add_argument("--double", default="volume-down")
    parser.add_argument("--hold", default="volume-up")
    parser.add_argument("--second-hold", default="volume-down")
    parser.add_argument("--long", default="display-off")
    parser.add_argument("--double-ms", type=int, default=350)
    parser.add_argument("--repeat-delay-ms", type=int, default=280)
    parser.add_argument("--repeat-ms", type=int, default=90)
    parser.add_argument("--long-ms", type=int, default=6000)
    parser.add_argument("--volume-step", type=int, default=5)
    parser.add_argument("--brightness-step", type=int, default=5)
    parser.add_argument("--repeat-volume-step", type=int, default=2)
    parser.add_argument("--repeat-brightness-step", type=int, default=2)
    parser.add_argument("--probe", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.probe:
        for path in candidates():
            print(f"{path}\t{event_name(path)}")
        return 0

    runner = ActionRunner(args)

    def hold_action(action):
        return lambda repeated: runner.run(action, repeated=repeated)


    engine = GestureEngine(
        lambda: runner.run(args.single),
        lambda: runner.run(args.double),
        hold_action(args.hold),
        hold_action(args.second_hold),
        lambda: runner.run(args.long),
        args.double_ms,
        args.repeat_delay_ms,
        args.repeat_ms,
        args.long_ms,
    )

    stopping = False
    devices = {}
    last_value = None
    last_time = 0.0

    def stop(*_):
        nonlocal stopping
        stopping = True

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    next_scan = 0.0

    try:
        while not stopping:
            now = time.monotonic()
            if now >= next_scan:
                wanted = set(candidates())
                for path in list(devices):
                    if path not in wanted:
                        devices.pop(path).close()
                for path in wanted:
                    if path not in devices:
                        try:
                            devices[path] = PowerDevice(path)
                            print(f"PowerButton: grabbed {path} ({event_name(path)})", file=sys.stderr, flush=True)
                        except OSError as exc:
                            print(f"PowerButton: cannot grab {path}: {exc}", file=sys.stderr, flush=True)
                next_scan = now + 3.0

            engine.tick(now)
            deadline = engine.next_deadline()
            timeout_ms = 250 if deadline is None else max(0, min(250, int((deadline - now) * 1000)))

            poller = select.poll()
            fdmap = {}
            for path, device in devices.items():
                poller.register(device.fd, select.POLLIN | select.POLLHUP | select.POLLERR)
                fdmap[device.fd] = path

            if not fdmap:
                time.sleep(min(timeout_ms / 1000.0, 0.25))
                continue

            for fd, mask in poller.poll(timeout_ms):
                path = fdmap.get(fd)
                if path is None:
                    continue
                if mask & (select.POLLHUP | select.POLLERR):
                    devices.pop(path).close()
                    continue
                try:
                    data = os.read(fd, EVENT.size * 32)
                except BlockingIOError:
                    continue
                except OSError:
                    devices.pop(path).close()
                    continue

                for offset in range(0, len(data) - EVENT.size + 1, EVENT.size):
                    _, _, event_type, code, value = EVENT.unpack_from(data, offset)
                    if event_type != EV_KEY or code != KEY_POWER or value == 2:
                        continue
                    now = time.monotonic()
                    if value == last_value and now - last_time < 0.05:
                        continue
                    last_value = value
                    last_time = now
                    engine.key(value, now)
    finally:
        for device in devices.values():
            device.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
