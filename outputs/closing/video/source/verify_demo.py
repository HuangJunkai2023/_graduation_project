"""Decode the delivered MP4, inspect timed frames and play it through Chrome."""
from argparse import ArgumentParser
from pathlib import Path
import hashlib
import json
import os
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
VIDEO = Path(__file__).resolve().parents[1]
SUPPORT = ROOT / 'project/qa_system/runtime/tooling/python-support'
sys.path.insert(0, str(SUPPORT))
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

parser = ArgumentParser(description=__doc__)
parser.add_argument('video', type=Path, nargs='?', default=VIDEO / 'OCS_Demo_EN_Visual_Draft.mp4')
parser.add_argument('--qa-dir', type=Path, default=VIDEO / 'qa')
parser.add_argument('--narration-kind', choices=('none','synthetic','student'), default='none')
args = parser.parse_args()
target, qa = args.video, args.qa_dir
qa.mkdir(parents=True, exist_ok=True)
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
streams = subprocess.run([ffmpeg, '-i', str(target)], capture_output=True, text=True)
audio_present = 'Audio:' in streams.stderr
fps = re.search(r'Video:.*?([0-9.]+) fps', streams.stderr)
duration = re.search(r'Duration: (\d+):(\d+):([0-9.]+)', streams.stderr)
if not fps or float(fps[1]) != 30 or not duration:
    raise ValueError('The delivered video must be 30 fps and have a known duration')
seconds = int(duration[1])*3600 + int(duration[2])*60 + float(duration[3])
if seconds > 300 or target.stat().st_size > 200_000_000:
    raise ValueError('The delivered video exceeds the course duration or size limits')
if audio_present != (args.narration_kind != 'none'):
    raise ValueError('Actual audio stream does not match the declared narration kind')
decoded = subprocess.run([ffmpeg, '-v', 'error', '-i', str(target), '-f', 'null', '-'],
                         capture_output=True, text=True, check=True)
if decoded.stderr.strip():
    raise RuntimeError(decoded.stderr)
subprocess.run([ffmpeg, '-v', 'error', '-y', '-i', str(target), '-vf',
                'fps=1/20,scale=640:360', str(qa / 'frame-%02d.png')], check=True)
sheet = Image.new('RGB', (1280, 6 * 390), 'white')
draw = ImageDraw.Draw(sheet)
font = ImageFont.truetype('C:/Windows/Fonts/calibri.ttf', 21)
for index in range(12):
    frame = Image.open(qa / f'frame-{index + 1:02d}.png')
    x, y = (index % 2) * 640, (index // 2) * 390
    sheet.paste(frame, (x, y))
    draw.text((x + 12, y + 362), f'{10 + 20 * index} seconds', font=font, fill='#23364B')
sheet.save(qa / 'contact-sheet.png')
runtime = Path(os.environ['OCS_DEMO_RUNTIME'])
subprocess.run([str(runtime / 'node/bin/node.exe'), str(VIDEO / 'source/verify_playback.cjs'),
                str(target), str(qa / 'playback.json')], check=True)
receipt = {
    'video': target.name,
    'video_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
    'bytes': target.stat().st_size,
    'full_decode_exit_code': decoded.returncode,
    'decode_errors': decoded.stderr.strip(),
    'sample_seconds': list(range(10, 240, 20)),
    'frames_per_second': float(fps[1]),
    'audio_stream_present': audio_present,
    'narration_kind': args.narration_kind,
    'student_narration_present': args.narration_kind == 'student',
    'browser_playback': json.loads((qa / 'playback.json').read_text(encoding='utf-8')),
}
if (receipt['browser_playback']['width'], receipt['browser_playback']['height']) != (1280, 720):
    raise ValueError('The delivered video must be 720p')
if audio_present:
    levels = subprocess.run([ffmpeg, '-i', str(target), '-vn', '-af', 'volumedetect',
                             '-f', 'null', '-'], check=True, capture_output=True, text=True)
    volume = re.search(r'max_volume:\s+(-?[\d.]+) dB', levels.stderr)
    if not volume or float(volume[1]) <= -60:
        raise ValueError('No audible signal was detected in the narration stream')
    receipt['narration_peak_dbfs'] = float(volume[1])
if args.narration_kind == 'synthetic':
    cues = (VIDEO / 'OCS_Demo_EN.srt').read_text(encoding='utf-8')
    ends = re.findall(r'--> (\d\d):(\d\d):(\d\d),(\d\d\d)', cues)
    times = [int(h)*3600+int(m)*60+int(s)+int(ms)/1000 for h,m,s,ms in ends]
    assert times == sorted(times) and 205 < times[-1] <= seconds
    receipt['cue_count'] = len(times)
    receipt['last_cue_end_seconds'] = times[-1]
(qa / 'validation.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
print(json.dumps(receipt, indent=2))
