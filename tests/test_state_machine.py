import importlib.util
from pathlib import Path

path = Path(__file__).parents[1] / 'scripts' / 'power-button-daemon.py'
spec = importlib.util.spec_from_file_location('powerbutton', path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def engine(events):
    out = []
    e = mod.GestureEngine(
        lambda: out.append('single'),
        lambda: out.append('double'),
        lambda repeated: out.append('hold-repeat' if repeated else 'hold-start'),
        lambda repeated: out.append('second-hold-repeat' if repeated else 'second-hold-start'),
        lambda: out.append('long'),
        double_ms=350,
        repeat_delay_ms=280,
        repeat_ms=90,
        long_ms=6000,
    )
    for kind, t in events:
        if kind == 'down':
            e.key(1, t)
        elif kind == 'up':
            e.key(0, t)
        else:
            e.tick(t)
    return out


def test_single_waits_for_double_window():
    assert engine([('down', 0), ('up', .05), ('tick', .20)]) == []
    assert engine([('down', 0), ('up', .05), ('tick', .41)]) == ['single']


def test_double_never_leaks_single():
    assert engine([('down', 0), ('up', .05), ('down', .20), ('up', .25), ('tick', 1)]) == ['double']


def test_first_hold_repeats_and_release_is_clean():
    assert engine([
        ('down', 0), ('tick', .27), ('tick', .28), ('tick', .37), ('tick', .46), ('up', .50), ('tick', 1)
    ]) == ['hold-start', 'hold-repeat', 'hold-repeat']


def test_click_then_hold_uses_second_hold_mapping():
    assert engine([
        ('down', 0), ('up', .05), ('down', .20), ('tick', .481), ('tick', .571), ('up', .60), ('tick', 1)
    ]) == ['second-hold-start', 'second-hold-repeat']


def test_very_long_hold_stops_repeat_and_suppresses_click():
    out = engine([
        ('down', 0), ('tick', .28), ('tick', .37), ('tick', 5.90), ('tick', 6.0), ('tick', 6.5), ('up', 6.6), ('tick', 7)
    ])
    assert out[-1] == 'long'
    assert 'single' not in out and 'double' not in out
    assert out.count('long') == 1


def test_late_second_press_becomes_new_sequence():
    assert engine([('down', 0), ('up', .05), ('down', .50), ('up', .55), ('tick', 1)]) == ['single', 'single']


if __name__ == '__main__':
    tests = [globals()[n] for n in sorted(globals()) if n.startswith('test_')]
    for test in tests:
        test()
        print('PASS', test.__name__)
