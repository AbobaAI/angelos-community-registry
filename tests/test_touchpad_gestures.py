"""Synthetic touchpad frames exercise all additional gestures without input access."""
import importlib.util
import math
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'plugins/touchpad-flex/gesture-watch.py'
spec = importlib.util.spec_from_file_location('touchpad_flex_gestures', SOURCE)
watch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(watch)


class Gestures(unittest.TestCase):
    def start(self, count, settings=None):
        rec = watch.Recognizer(100, 60, 1, 1, settings=settings)
        rec.slots = {i: [50 + 10 * math.cos(i * 2 * math.pi/count), 30 + 10 * math.sin(i * 2 * math.pi/count)] for i in range(count)}
        self.assertEqual(rec.frame(0), [])
        return rec

    def move(self, rec, dx, dy, t=0.2):
        rec.slots = {i: [x + dx, y + dy] for i, (x,y) in rec.slots.items()}
        return rec.frame(t)

    def release(self, rec, t):
        rec.slots = {}
        return rec.frame(t)

    def test_all_five_finger_swipe_directions(self):
        for dx,dy,name in [(30,0,'Right'),(-30,0,'Left'),(0,-30,'Up'),(0,30,'Down'),(-22,-22,'UpLeft'),(22,-22,'UpRight'),(-22,22,'DownLeft'),(22,22,'DownRight')]:
            with self.subTest(name=name):
                rec = self.start(5)
                self.assertEqual(self.move(rec,dx,dy), ['swipe5'+name])
                self.assertEqual(self.move(rec,dx,dy), [])
                self.assertEqual(self.release(rec,0.3), [])

    def test_four_finger_diagonals_only(self):
        for dx,dy,name in [(-22,-22,'UpLeft'),(22,-22,'UpRight'),(-22,22,'DownLeft'),(22,22,'DownRight')]:
            self.assertEqual(self.move(self.start(4),dx,dy), ['swipe4'+name])
        for dx,dy in [(30,0),(-30,0),(0,30),(0,-30)]:
            self.assertEqual(self.move(self.start(3),dx,dy), [])
        self.assertEqual(self.move(self.start(4),30,0), ['swipe4Right'])
        self.assertEqual(self.move(self.start(4),0,-30), [])

    def test_three_and_five_finger_pinches(self):
        for n in [3,5]:
            for factor,name in [(0.4,'In'),(2,'Out')]:
                rec=self.start(n)
                rec.slots={i:[50+(x-50)*factor,30+(y-30)*factor] for i,(x,y) in rec.slots.items()}
                self.assertEqual(rec.frame(0.2), ['pinch'+str(n)+name])

    def test_taps_holds_and_existing_gestures(self):
        self.assertEqual(self.release(self.start(5),0.2), ['tap5'])
        for n in [4,5]:
            self.assertEqual(self.release(self.start(n),0.8), ['hold'+str(n)])
        for n in [3,4]:
            self.assertEqual(self.release(self.start(n),0.2), ['tap'+str(n)])
        self.assertEqual(self.release(self.start(3),0.8), ['hold3'])

    def test_top_and_bottom_edges(self):
        for y,dy,name in [(1,12,'edgeTop'),(59,-12,'edgeBottom')]:
            rec=watch.Recognizer(100,60,1,1)
            rec.slots={0:[50,y]};rec.frame(0)
            self.assertEqual(self.move(rec,0,dy), [name])
        rec=watch.Recognizer(100,60,1,1)
        rec.slots={0:[1,30]};rec.frame(0)
        self.assertEqual(self.move(rec,30,0), ['edgeLeft'])

    def test_custom_distance_and_hold_threshold(self):
        rec=self.start(5,{'swipeMm':40})
        self.assertEqual(self.move(rec,30,0), [])
        self.assertEqual(self.move(rec,15,0), ['swipe5Right'])
        self.assertEqual(self.release(self.start(4,{'holdMs':1200}),0.8), [])
        self.assertEqual(self.release(self.start(4,{'holdMs':1200}),1.3), ['hold4'])

    def test_bad_parameters_stop_before_device_scan(self):
        for config in ['[]','{"holdMs":-1}','{"swipeMm":true}','{"unknown":1}']:
            result=subprocess.run([sys.executable,str(SOURCE),'--config',config],capture_output=True,text=True)
            self.assertEqual(result.returncode,2,result.stderr)
            self.assertNotIn('ready',result.stdout)

    @unittest.skipUnless(shutil.which('niri'), 'niri required for configuration validation')
    def test_advanced_options_are_valid_niri(self):
        with tempfile.TemporaryDirectory() as folder:
            config=Path(folder)/'config.kdl'
            config.write_text('input {\n touchpad {\n drag-lock\n dwtp\n drag true\n scroll-method "two-finger"\n }\n}\n')
            result=subprocess.run(['niri','validate','-c',str(config)],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
