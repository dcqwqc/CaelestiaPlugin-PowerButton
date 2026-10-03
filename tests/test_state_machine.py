import importlib.util
from pathlib import Path

path=Path(__file__).parents[1]/'scripts'/'power-button-daemon.py'
spec=importlib.util.spec_from_file_location('powerbutton',path)
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

def engine(events):
    out=[]
    e=mod.GestureEngine(lambda:out.append('single'),lambda:out.append('double'),lambda:out.append('hold'),350,6000)
    for kind,t in events:
        if kind=='down': e.key(1,t)
        elif kind=='up': e.key(0,t)
        else: e.tick(t)
    return out

def test_single_waits_for_double_window():
    assert engine([('down',0),('up',.05),('tick',.20)])==[]
    assert engine([('down',0),('up',.05),('tick',.41)])==['single']

def test_double_never_leaks_single():
    assert engine([('down',0),('up',.05),('down',.20),('up',.25),('tick',1)])==['double']

def test_hold_fires_once_and_release_is_clean():
    assert engine([('down',0),('tick',6.0),('tick',7.0),('up',7.1),('tick',8)])==['hold']

def test_late_second_press_becomes_new_sequence():
    assert engine([('down',0),('up',.05),('down',.50),('up',.55),('tick',1)])==['single','single']

if __name__=='__main__':
    tests=[globals()[n] for n in sorted(globals()) if n.startswith('test_')]
    for test in tests:
        test(); print('PASS',test.__name__)
