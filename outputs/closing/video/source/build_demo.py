"""Build a captioned four-minute demo from the actual browser recording."""
from pathlib import Path
import argparse
import base64
import json
import re
import subprocess
import sys
from tempfile import TemporaryDirectory
import textwrap
import wave

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


def caption_plan():
    script = (VIDEO / 'OCS_Demo_CN_EN_Script.md').read_text(encoding='utf-8')
    passages = re.findall(r'\*\*English\*\*\s+(.*?)\s+\*\*中文对照\*\*', script, flags=re.S)
    intervals = [(0,25),(25,50),(50,100),(100,135),(135,165),(165,195),(195,205),(205,240)]
    if len(passages) != len(intervals):
        raise ValueError('Narration sections do not match the video schedule')
    plan = []
    for passage, (start, end) in zip(passages, intervals):
        words = passage.split()
        chunks = [' '.join(words[i:i+15]) for i in range(0, len(words), 15)]
        plan.append((start, end, chunks))
    return plan


def synthesize(plan, directory):
    """Generate local synthetic preview speech and obtain its actual cue boundaries."""
    cues = [chunk for _, _, chunks in plan for chunk in chunks]
    request = directory / 'captions.json'
    request.write_text(json.dumps(cues), encoding='utf-8')
    sound_script = r'''
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$voice = New-Object System.Speech.Synthesis.SpeechSynthesizer
$voice.SelectVoice('Microsoft Zira Desktop')
$voice.Rate = 1
$format = New-Object System.Speech.AudioFormat.SpeechAudioFormatInfo(22050, 'Sixteen', 'Mono')
$entries = Get-Content -LiteralPath captions.json -Raw -Encoding UTF8 | ConvertFrom-Json
for ($index=0; $index -lt $entries.Count; $index++) {
    $voice.SetOutputToWaveFile(('{0}.wav' -f $index), $format)
    $spoken = $entries[$index] -replace '\bBM25\b','B M twenty-five' -replace '\bOCS\b','O C S' -replace '\bPDF\b','P D F'
    $voice.Speak($spoken)
    $voice.SetOutputToNull()
}
$voice.Dispose()
'''
    encoded = base64.b64encode(sound_script.encode('utf-16le')).decode('ascii')
    subprocess.run(['powershell.exe', '-NoProfile', '-EncodedCommand', encoded], cwd=directory, check=True)
    audio = directory / 'synthetic-preview.wav'
    segments = []
    rate = 22050
    timeline = 0
    index = 0
    with wave.open(str(audio), 'wb') as track:
        track.setparams((1, 2, rate, 0, 'NONE', 'not compressed'))
        for start, end, chunks in plan:
            samples = []
            for chunk in chunks:
                with wave.open(str(directory / f'{index}.wav'), 'rb') as sound:
                    if (sound.getnchannels(), sound.getsampwidth(), sound.getframerate()) != (1, 2, rate):
                        raise ValueError('Unexpected local narration sample format')
                    frames = sound.getnframes()
                    samples.append((chunk, frames, sound.readframes(frames)))
                index += 1
            available = round((end-start)*rate) - sum(frames for _, frames, _ in samples)
            if available < 0:
                raise ValueError(f'Narration exceeds its scene at {start} seconds')
            pause = min(round(.45*rate), available//(len(samples)+1))
            begin = round(start*rate) + pause
            track.writeframes(b'\0\0' * (begin-timeline))
            timeline = begin
            for chunk, frames, samples_bytes in samples:
                track.writeframes(samples_bytes)
                segments.append((timeline/rate, (timeline+frames)/rate, chunk))
                track.writeframes(b'\0\0' * pause)
                timeline += frames + pause
        track.writeframes(b'\0\0' * (240*rate-timeline))
    return audio, segments


def subtitles(plan, measured=None):
    if measured is None:
        measured = []
        for start, end, chunks in plan:
            count = sum(len(chunk.split()) for chunk in chunks)
            cursor = start
            for chunk in chunks:
                finish = cursor + (end-start) * len(chunk.split())/count
                measured.append((cursor, finish, chunk))
                cursor = finish
    captions = [f'{i}\n{timestamp(start)} --> {timestamp(end)}\n'
                + '\n'.join(textwrap.wrap(chunk, width=60)) + '\n'
                for i, (start, end, chunk) in enumerate(measured, 1)]
    (VIDEO / 'OCS_Demo_EN.srt').write_text('\n'.join(captions), encoding='utf-8')
    return sum(len(chunk.split()) for _, _, chunk in measured)


def result_card(path):
    card(path, ['Measured retrieval comparison'], [])
    image = Image.open(path).convert('RGB')
    plot = Image.open(VIDEO.parent / 'figures/report_paired_recall.png').convert('RGB')
    plot.thumbnail((900, 404), Image.Resampling.LANCZOS)
    image.paste(plot, ((1280-plot.width)//2, 213))
    image.save(path)


def main():
    parser = argparse.ArgumentParser()
    narration_options = parser.add_mutually_exclusive_group()
    narration_options.add_argument('--narration')
    narration_options.add_argument('--synthetic-preview', action='store_true')
    args = parser.parse_args()
    with TemporaryDirectory(prefix='ocs-demo-audio-') as temporary:
        build(args, Path(temporary))


def build(args, temporary):
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
    result_card(assets/'conclusion.png')
    plan = caption_plan()
    preview_audio, measured = synthesize(plan, temporary) if args.synthetic_preview else (None, None)
    word_count = subtitles(plan, measured)
    visual = VIDEO / 'OCS_Demo_EN_Visual_Draft.mp4'
    graph = ('[0:v]fps=30,format=yuv420p,setpts=PTS-STARTPTS[a];'
             '[1:v]fps=30,format=yuv420p,setpts=PTS-STARTPTS[b];'
             '[2:v]fps=30,format=yuv420p,setpts=PTS-STARTPTS[c];'
             "[a][b][c]concat=n=3:v=1:a=0,subtitles=OCS_Demo_EN.srt:"
             "force_style='FontName=Calibri,FontSize=18,Outline=1,Shadow=0,MarginV=18'[v]")
    command = [ffmpeg, '-y', '-loop', '1', '-t', '15', '-i', str(assets/'title.png'),
               '-ss', str(offset), '-t', '190', '-i', str(raw),
               '-loop', '1', '-t', '35', '-i', str(assets/'conclusion.png'),
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
    preview = None
    if preview_audio:
        preview = VIDEO / 'OCS_Demo_EN_Synthetic_Voice_Preview.mp4'
        badge = Image.new('RGB', (420, 42), '#173C68')
        font = ImageFont.truetype('C:/Windows/Fonts/calibrib.ttf', 21)
        ImageDraw.Draw(badge).text((13, 9), 'REVIEW PREVIEW  |  SYNTHETIC NARRATION', font=font, fill='white')
        badge_path = temporary / 'badge.png'
        badge.save(badge_path)
        subprocess.run([ffmpeg, '-v', 'error', '-y', '-i', str(visual), '-i', str(preview_audio),
                        '-i', str(badge_path), '-filter_complex', '[0:v][2:v]overlay=W-w-10:10[v]',
                        '-map', '[v]', '-map', '1:a:0', '-t', '240', '-c:v', 'libx264', '-crf', '22',
                        '-preset', 'fast', '-c:a', 'aac', '-movflags', '+faststart', str(preview)], check=True)
    receipt = {'raw_duration_seconds': duration, 'recording_lead_trim_seconds': offset,
               'output_seconds': final_seconds, 'resolution': [1280,720], 'frames_per_second': 30,
               'english_word_count': word_count, 'visual_bytes': visual.stat().st_size,
               'student_narration_present': bool(final), 'final_video': final.name if final else None,
               'synthetic_voice_preview': preview.name if preview else None,
               'synthetic_voice': 'Microsoft Zira Desktop' if preview else None,
               'remaining_action': None if final else 'Final narration and course suitability are pending.'}
    (VIDEO/'video_build_receipt.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
