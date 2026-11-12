"""Decode the delivered MP4, inspect timed frames and play it through Chrome."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
VIDEO = Path(__file__).resolve().parents[1]
SUPPORT = ROOT / 'project/qa_system/runtime/tooling/python-support'
sys.path.insert(0, str(SUPPORT))
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

target = Path(sys.argv[1]) if len(sys.argv) > 1 else VIDEO / 'OCS_Demo_EN_Visual_Draft.mp4'
qa = VIDEO / 'qa'
qa.mkdir(exist_ok=True)
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
streams = subprocess.run([ffmpeg, '-i', str(target)], capture_output=True, text=True)
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
runtime = Path('C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1105-1297-0_26.1105.1297.0_x64__3k8sg7r9htsxt/dependencies')
subprocess.run([str(runtime / 'node/bin/node.exe'), str(VIDEO / 'source/verify_playback.cjs'),
                str(target), str(qa / 'playback.json')], check=True)
receipt = {
    'video': target.name,
    'video_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
    'bytes': target.stat().st_size,
    'full_decode_exit_code': decoded.returncode,
    'decode_errors': decoded.stderr.strip(),
    'sample_seconds': list(range(10, 240, 20)),
    'audio_stream_present': 'Audio:' in streams.stderr,
    'student_narration_present': target.name != 'OCS_Demo_EN_Visual_Draft.mp4' and 'Audio:' in streams.stderr,
    'browser_playback': json.loads((qa / 'playback.json').read_text()),
}
(qa / 'validation.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
print(json.dumps(receipt, indent=2))
