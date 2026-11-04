"""Check actual PDF table outlines, including top/bottom edges on continuation pages."""
from __future__ import annotations

import argparse
from pathlib import Path

import pymupdf


def check_frames(pdf_path, pages=None):
    checked = []
    failures = []
    with pymupdf.open(pdf_path) as pdf:
        for number in pages or range(1, len(pdf) + 1):
            page = pdf[number - 1]
            horizontal, vertical = [], []
            for drawing in page.get_drawings():
                for item in drawing['items']:
                    if item[0] != 'l':
                        continue
                    a, b = item[1:3]
                    if min(a.y, b.y) < 90:
                        continue  # school-header rule, outside the report table
                    if abs(a.x - b.x) < 0.1 and abs(a.y - b.y) > 40:
                        vertical.append((a.x, min(a.y, b.y), max(a.y, b.y)))
                    if abs(a.y - b.y) < 0.1:
                        horizontal.append((a.y, min(a.x, b.x), max(a.x, b.x)))
            if not vertical:
                failures.append(f'Page {number}: no table side edges')
                continue
            left = min(v[0] for v in vertical)
            right = max(v[0] for v in vertical)
            sides = [v for v in vertical if abs(v[0] - left) < 1 or abs(v[0] - right) < 1]
            top = min(v[1] for v in sides)
            bottom = max(v[2] for v in sides)
            for name, y in [('top', top), ('bottom', bottom)]:
                intervals = sorted((x0, x1) for yy, x0, x1 in horizontal if abs(yy - y) <= 1)
                end = left
                for start, stop in intervals:
                    if start <= end + 1:
                        end = max(end, stop)
                if end < right - 1:
                    failures.append(f'Page {number}: open {name} edge at y={y:.2f}; '
                                    f'coverage {end - left:.2f}/{right - left:.2f} pt')
            checked.append({'page': number, 'left': left, 'right': right, 'top': top, 'bottom': bottom})
    assert not failures, '\n'.join(failures)
    return checked


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pdf', type=Path)
    parser.add_argument('--page', type=int, action='append')
    args = parser.parse_args()
    result = check_frames(args.pdf, args.page)
    print(f'PASS: {len(result)} page(s), all table top/bottom edges closed.')
