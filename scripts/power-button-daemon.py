#!/usr/bin/env python3
import argparse, fcntl, glob, os, select, signal, struct, subprocess, sys, time

EV_KEY=1
KEY_POWER=116
EVIOCGRAB=1074021776
EVENT=struct.Struct('llHHi')

class GestureEngine:
    def __init__(self,single,double,double_ms=350):
        self.single_cb=single; self.double_cb=double
        self.double_s=max(0.08,double_ms/1000.0)
        self.pending=False; self.deadline=0.0
    def tick(self,now):
        if self.pending and now>=self.deadline:
            self.single_cb(); self.pending=False
    def press(self,now):
        self.tick(now)
        if self.pending and now<=self.deadline:
            self.double_cb(); self.pending=False
        else:
            self.pending=True; self.deadline=now+self.double_s

class ActionRunner:
    def __init__(self,args): self.args=args
    def spawn(self,command):
        try: subprocess.Popen(command,start_new_session=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        except Exception as exc: print(f'PowerButton: action failed: {exc}',file=sys.stderr,flush=True)
    def run(self,action):
        if action=='disabled': return
        if action=='volume-up': self.spawn(['wpctl','set-volume','-l','1.0','@DEFAULT_AUDIO_SINK@',f'{self.args.volume_step}%+'])
        elif action=='volume-down': self.spawn(['wpctl','set-volume','@DEFAULT_AUDIO_SINK@',f'{self.args.volume_step}%-'])
        elif action=='mute-toggle': self.spawn(['wpctl','set-mute','@DEFAULT_AUDIO_SINK@','toggle'])
        elif action=='brightness-up': self.spawn(['brightnessctl','set',f'{self.args.brightness_step}%+'])
        elif action=='brightness-down': self.spawn(['brightnessctl','set',f'{self.args.brightness_step}%-'])
        elif action=='media-play-pause': self.spawn(['caelestia','shell','mpris','playPause'])
        elif action=='media-next': self.spawn(['caelestia','shell','mpris','next'])
        elif action=='media-previous': self.spawn(['caelestia','shell','mpris','previous'])
        elif action=='lock': self.spawn(['caelestia','shell','lock','lock'])
        elif action=='display-off': self.spawn(['hyprctl','dispatch','dpms','off'])

def event_name(path):
    try:
        with open(f'/sys/class/input/{os.path.basename(path)}/device/name',encoding='utf-8') as f: return f.read().strip()
    except OSError: return ''

def candidates():
    paths=sorted(glob.glob('/dev/input/event*'))
    exact=[p for p in paths if event_name(p).lower()=='power button']
    return exact or [p for p in paths if 'power' in event_name(p).lower()]

class PowerDevice:
    def __init__(self,path):
        self.path=path; self.fd=os.open(path,os.O_RDONLY|os.O_NONBLOCK); fcntl.ioctl(self.fd,EVIOCGRAB,1)
    def close(self):
        if self.fd is None: return
        try: fcntl.ioctl(self.fd,EVIOCGRAB,0)
        except OSError: pass
        try: os.close(self.fd)
        except OSError: pass
        self.fd=None

def parse_args():
    p=argparse.ArgumentParser()
    p.add_argument('--single',default='volume-up'); p.add_argument('--double',default='volume-down')
    p.add_argument('--double-ms',type=int,default=350); p.add_argument('--volume-step',type=int,default=5); p.add_argument('--brightness-step',type=int,default=5)
    p.add_argument('--probe',action='store_true')
    return p.parse_args()

def main():
    args=parse_args()
    if args.probe:
        for path in candidates(): print(f'{path}\t{event_name(path)}')
        return 0
    runner=ActionRunner(args); engine=GestureEngine(lambda:runner.run(args.single),lambda:runner.run(args.double),args.double_ms)
    stopping=False; devices={}; last_press=-1.0
    def stop(*_):
        nonlocal stopping; stopping=True
    signal.signal(signal.SIGTERM,stop); signal.signal(signal.SIGINT,stop)
    next_scan=0.0
    try:
        while not stopping:
            now=time.monotonic()
            if now>=next_scan:
                wanted=set(candidates())
                for path in list(devices):
                    if path not in wanted: devices.pop(path).close()
                for path in wanted:
                    if path not in devices:
                        try: devices[path]=PowerDevice(path); print(f'PowerButton: grabbed {path} ({event_name(path)})',file=sys.stderr,flush=True)
                        except OSError as exc: print(f'PowerButton: cannot grab {path}: {exc}',file=sys.stderr,flush=True)
                next_scan=now+3.0
            engine.tick(now)
            timeout_ms=250 if not engine.pending else max(0,min(250,int((engine.deadline-now)*1000)))
            poller=select.poll(); fdmap={}
            for path,dev in devices.items(): poller.register(dev.fd,select.POLLIN|select.POLLHUP|select.POLLERR); fdmap[dev.fd]=path
            if not fdmap: time.sleep(min(timeout_ms/1000.0,0.25)); continue
            for fd,mask in poller.poll(timeout_ms):
                path=fdmap.get(fd)
                if path is None: continue
                if mask&(select.POLLHUP|select.POLLERR): devices.pop(path).close(); continue
                try: data=os.read(fd,EVENT.size*32)
                except BlockingIOError: continue
                except OSError: devices.pop(path).close(); continue
                for off in range(0,len(data)-EVENT.size+1,EVENT.size):
                    _,_,etype,code,value=EVENT.unpack_from(data,off)
                    if etype!=EV_KEY or code!=KEY_POWER or value!=1: continue
                    now=time.monotonic()
                    if now-last_press<0.05: continue
                    last_press=now; engine.press(now)
    finally:
        for dev in devices.values(): dev.close()
    return 0

if __name__=='__main__': raise SystemExit(main())
