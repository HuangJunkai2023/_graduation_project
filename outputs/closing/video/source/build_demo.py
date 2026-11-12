"""Build a captioned four-minute demo from the actual browser recording."""
from pathlib import Path
import argparse
import json
import re
import subprocess
import sys
import textwrap

ROOT = Path(__file__).resolve().parents[4]
VIDEO = Path(__file__).resolve().parents[1]
SUPPORT = ROOT / 'project/qa_system/runtime/tooling/python-support'
sys.path.insert(0, str(SUPPORT))
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont


def card(path, title, lines):
    image = Image.new('RGB', (1280, 720), '#FFFFFF')
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 1280, 94), fill='#194B8C')
    white = ImageFont.truetype('C:/Windows/Fonts/calibrib.ttf', 34)
    heading = ImageFont.truetype('C:/Windows/Fonts/calibrib.ttf', 43)
    body = ImageFont.truetype('C:/Windows/Fonts/calibri.ttf', 30)
    draw.text((60, 29), 'SWJTU Leeds Joint School', fill='white', font=white)
    y = 160
    for line in title:
        draw.text((65, y), line, fill='#194B8C', font=heading)
        y += 58
    y += 36
    for line in lines:
        draw.text((65, y), line, fill='#23364B', font=body)
        y += 47
    image.save(path)


def timestamp(seconds):
    milliseconds = round(seconds * 1000)
    hours, remainder = divmod(milliseconds, 3600000)
    minutes, remainder = divmod(remainder, 60000)
    seconds, milliseconds = divmod(remainder, 1000)
    return f'{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}'


def subtitles():
    script = (VIDEO / 'OCS_Demo_CN_EN_Script.md').read_text(encoding='utf-8')
    passages = re.findall(r'\*\*English\*\*\s+(.*?)\s+\*\*中文对照\*\*', script, flags=re.S)
    intervals = [(0,25),(25,50),(50,100),(100,135),(135,165),(165,195),(195,240)]
    if len(passages) != len(intervals):
        raise ValueError('Narration sections do not match the video schedule')
    captions = []
    for passage, (start, end) in zip(passages, intervals):
        words = passage.split()
        chunks = [words[i:i+18] for i in range(0, len(words), 18)]
        cursor = start
        for chunk in chunks:
            finish = cursor + (end - start) * len(chunk) / len(words)
            captions.append(f'{len(captions)+1}\n{timestamp(cursor)} --> {timestamp(finish)}\n'
                            + '\n'.join(textwrap.wrap(' '.join(chunk), width=60)) + '\n')
            cursor = finish
    (VIDEO / 'OCS_Demo_EN.srt').write_text('\n'.join(captions), encoding='utf-8')
    return sum(len(p.split()) for p in passages)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--narration')
    args = parser.parse_args()
    raw = VIDEO / 'recording/OCS_Demo_Raw.webm'
    if not raw.is_file():
        raise ValueError('The actual browser recording is required')
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    inspected = subprocess.run([ffmpeg, '-i', str(raw)], capture_output=True, text=True)
    match = re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)', inspected.stderr)
    if not match:
        raise ValueError('Cannot inspect recorded duration')
    duration = int(match[1])*3600 + int(match[2])*60 + float(match[3])
    if duration < 210:
        raise ValueError('Recording did not complete the demonstration sequence')
    offset = max(0, duration - 210)
    assets = VIDEO / 'assets'
    assets.mkdir(parents=True, exist_ok=True)
    card(assets/'title.png', ['A Study on a Large-Model-Based Intelligent',
        'Question-Answering System for the', 'Overhead Contact System Field'],
        ['Junkai Huang  |  Leeds SID 201804121', 'Supervisor  Prof. Deqing Huang',
         'Retrieval  /  Edition checks  /  Traceable sources'])
    card(assets/'conclusion.png', ['Corpus bound evaluation'],
        ['25 documents  |  100 questions  |  Five configurations',
         '400 primary first attempt slots',
         'Source reviews and scoring use the documented assistant protocol',
         'Technical document learning and consultation'])
    word_count = subtitles()
    visual = VIDEO / 'OCS_Demo_EN_Visual_Draft.mp4'
    graph = ('[0:v]fps=30,format=yuv420p,setpts=PTS-STARTPTS[a];'
             '[1:v]fps=30,format=yuv420p,setpts=PTS-STARTPTS[b];'
             '[2:v]fps=30,format=yuv420p,setpts=PTS-STARTPTS[c];'
             "[a][b][c]concat=n=3:v=1:a=0,subtitles=OCS_Demo_EN.srt:"
             "force_style='FontName=Calibri,FontSize=18,Outline=1,Shadow=0,MarginV=18'[v]")
    command = [ffmpeg, '-y', '-loop', '1', '-t', '15', '-i', str(assets/'title.png'),
               '-ss', str(offset), '-t', '210', '-i', str(raw),
               '-loop', '1', '-t', '15', '-i', str(assets/'conclusion.png'),
               '-filter_complex', graph, '-map', '[v]', '-t', '240', '-c:v', 'libx264',
               '-crf', '22', '-preset', 'fast', '-pix_fmt', 'yuv420p',
               '-movflags', '+faststart', str(visual)]
    log = VIDEO / 'assets/encoding.log'
    with log.open('w', encoding='utf-8') as handle:
        subprocess.run(command, cwd=VIDEO, stdout=handle, stderr=handle, check=True,
                       creationflags=subprocess.CREATE_NO_WINDOW)
    final = None
    final_seconds = 240
    if args.narration:
        narration = Path(args.narration).resolve()
        if not narration.is_file():
            raise ValueError('Student narration file was not found')
        audio_probe = subprocess.run([ffmpeg, '-i', str(narration)], capture_output=True, text=True)
        audio_match = re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)', audio_probe.stderr)
        if not audio_match:
            raise ValueError('Cannot inspect the student narration audio')
        audio_seconds = int(audio_match[1])*3600 + int(audio_match[2])*60 + float(audio_match[3])
        if audio_seconds > 299:
            raise ValueError('Student narration must fit the five-minute course limit')
        final_seconds = min(300, max(240, int(audio_seconds) + 1))
        final = VIDEO / 'OCS_Demo_EN.mp4'
        subprocess.run([ffmpeg, '-y', '-i', str(visual), '-i', str(narration),
                        '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'libx264', '-crf', '22',
                        '-vf', 'tpad=stop_mode=clone:stop_duration=60', '-c:a', 'aac',
                        '-af', 'apad', '-t', str(final_seconds), '-movflags', '+faststart', str(final)],
                       check=True, creationflags=subprocess.CREATE_NO_WINDOW)
    receipt = {'raw_duration_seconds': duration, 'recording_lead_trim_seconds': offset,
               'output_seconds': final_seconds, 'resolution': [1280,720], 'frames_per_second': 30,
               'english_word_count': word_count, 'visual_bytes': visual.stat().st_size,
               'student_narration_present': bool(final), 'final_video': str(final) if final else None,
               'remaining_action': None if final else 'Provide the student English narration for final audio integration.'}
    (VIDEO/'video_build_receipt.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
