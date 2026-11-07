"""Generate a printable ArUco marker image."""

import argparse

import cv2
import numpy as np


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--id', type=int, default=0, dest='marker_id')
    parser.add_argument('--dictionary', default='DICT_4X4_50')
    parser.add_argument('--pixels', type=int, default=1000)
    parser.add_argument('--border-pixels', type=int, default=100)
    parser.add_argument('--output', default='aruco_0.png')
    arguments = parser.parse_args()

    dictionary_id = getattr(cv2.aruco, arguments.dictionary, None)
    if dictionary_id is None:
        parser.error(f'unsupported dictionary: {arguments.dictionary}')
    dictionary = cv2.aruco.getPredefinedDictionary(dictionary_id)
    if not 0 <= arguments.marker_id < dictionary.bytesList.shape[0]:
        parser.error('marker id is outside the selected dictionary')
    if arguments.pixels <= 0 or arguments.border_pixels < 0:
        parser.error('pixel sizes must be positive')
    marker = cv2.aruco.drawMarker(
        dictionary, arguments.marker_id, arguments.pixels
    )
    border = arguments.border_pixels
    output = np.full(
        (arguments.pixels + 2 * border, arguments.pixels + 2 * border),
        255,
        dtype=np.uint8,
    )
    output[border:border + arguments.pixels,
           border:border + arguments.pixels] = marker
    if not cv2.imwrite(arguments.output, output):
        parser.error(f'cannot write {arguments.output}')
    print(arguments.output)
