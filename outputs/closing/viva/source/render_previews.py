"""Render the exported Viva PDF and check its page geometry."""
from argparse import ArgumentParser
from pathlib import Path
import json
import pymupdf
from PIL import Image, ImageDraw

parser = ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parents[1])
root = parser.parse_args().output
(root / 'validation').mkdir(exist_ok=True)
preview = root / 'previews'
preview.mkdir(exist_ok=True)
document = pymupdf.open(root / 'OCS_Viva_EN.pdf')
assert len(document) == 18
outside = []
images = []
for i, page in enumerate(document):
    path = preview / f'slide-{i+1:02}.png'
    page.get_pixmap(matrix=pymupdf.Matrix(1280/page.rect.width, 1280/page.rect.width)).save(path)
    image = Image.open(path).convert('RGB')
    image.thumbnail((480, 270))
    tile = Image.new('RGB', (500, 300), 'white')
    tile.paste(image, ((500-image.width)//2, 0))
    ImageDraw.Draw(tile).text((12, 280), str(i+1), fill='black')
    images.append(tile)
    for block in page.get_text('blocks'):
        if not isinstance(block[4], str) or not block[4].strip():
            continue
        if block[0] < -1 or block[1] < -1 or block[2] > page.rect.width+1 or block[3] > page.rect.height+1:
            outside.append({'slide': i+1, 'text': block[4], 'bounds': block[:4]})
montage = Image.new('RGB', (1500, 1800), '#DFE6ED')
for i, image in enumerate(images):
    montage.paste(image, ((i % 3)*500, (i//3)*300))
montage.save(root / 'overview.png')
(root / 'validation/render_check.json').write_text(json.dumps({
    'slides': len(document), 'outside_page_text': outside}, ensure_ascii=False, indent=2), encoding='utf-8')
print({'slides': len(document), 'outside_page_text': outside})
