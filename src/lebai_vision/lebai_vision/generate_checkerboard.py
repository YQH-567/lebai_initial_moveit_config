"""Create an A4 landscape checkerboard SVG for UVC camera calibration."""

import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cols', type=int, default=9,
                        help='inner corners across')
    parser.add_argument('--rows', type=int, default=6,
                        help='inner corners down')
    parser.add_argument('--square-mm', type=float, default=25.0)
    parser.add_argument('--output', default='checkerboard_9x6_25mm.svg')
    args = parser.parse_args()
    if args.cols < 3 or args.rows < 3 or args.square_mm <= 0:
        parser.error('invalid checkerboard dimensions')
    board_width = (args.cols + 1) * args.square_mm
    board_height = (args.rows + 1) * args.square_mm
    if board_width > 277 or board_height > 190:
        parser.error('checkerboard does not fit A4 landscape with margins')
    left = (297 - board_width) / 2
    top = (210 - board_height) / 2
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="297mm" height="210mm" '
        'viewBox="0 0 297 210">',
        '<rect width="297" height="210" fill="white"/>',
    ]
    for row in range(args.rows + 1):
        for col in range(args.cols + 1):
            if (row + col) % 2 == 0:
                x = left + col * args.square_mm
                y = top + row * args.square_mm
                lines.append(
                    f'<rect x="{x:g}" y="{y:g}" width="{args.square_mm:g}" '
                    f'height="{args.square_mm:g}" fill="black"/>'
                )
    lines.append('</svg>')
    Path(args.output).write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'{args.output}: print A4 landscape at 100%, measure a square')
