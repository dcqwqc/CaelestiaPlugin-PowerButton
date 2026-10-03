import importlib.util
from pathlib import Path

path = Path(__file__).parents[1] / 'scripts' / 'power-button-daemon.py'
spec = importlib.util.spec_from_file_location('powerbutton', path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_single_after_window():
    out=[]; e=mod.GestureEngine(lambda:out.append('single'),lambda:out.append('double'),350)
    e.press(0.0); e.tick(0.2); assert out==[]; e.tick(0.36); assert out==['single']


def test_double_cancels_single():
    out=[]; e=mod.GestureEngine(lambda:out.append('single'),lambda:out.append('double'),350)
    e.press(0.0); e.press(0.2); e.tick(1.0); assert out==['double']


def test_late_press_is_two_singles():
    out=[]; e=mod.GestureEngine(lambda:out.append('single'),lambda:out.append('double'),350)
    e.press(0.0); e.press(0.5); e.tick(1.0); assert out==['single','single']


if __name__ == '__main__':
    for name in sorted(n for n in globals() if n.startswith('test_')):
        globals()[name](); print('PASS',name)
