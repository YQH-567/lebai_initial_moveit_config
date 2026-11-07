"""Interactively calibrate the UVC color camera using a checkerboard."""

import argparse
from pathlib import Path

import cv2
import numpy as np
import yaml


def calibration_data(camera_matrix, distortion, width, height):
    """Format OpenCV calibration results as standard ROS CameraInfo YAML."""
    projection = np.zeros((3, 4), dtype=np.float64)
    projection[:, :3] = camera_matrix
    return {
        'image_width': width,
        'image_height': height,
        'camera_name': 'uvc_color',
        'camera_matrix': {'rows': 3, 'cols': 3,
                          'data': camera_matrix.reshape(-1).tolist()},
        'distortion_model': 'plumb_bob',
        'distortion_coefficients': {'rows': 1, 'cols': distortion.size,
                                    'data': distortion.reshape(-1).tolist()},
        'rectification_matrix': {'rows': 3, 'cols': 3,
                                 'data': np.eye(3).reshape(-1).tolist()},
        'projection_matrix': {'rows': 3, 'cols': 4,
                              'data': projection.reshape(-1).tolist()},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--device', default='/dev/video0')
    parser.add_argument('--cols', type=int, default=9,
                        help='checkerboard INNER corners across')
    parser.add_argument('--rows', type=int, default=6,
                        help='checkerboard INNER corners down')
    parser.add_argument('--square-size', type=float, default=0.025,
                        help='measured checkerboard square size in metres')
    parser.add_argument('--samples', type=int, default=20)
    parser.add_argument('--output', default='camera_calibration.yaml')
    args = parser.parse_args()
    if args.cols < 3 or args.rows < 3 or args.square_size <= 0 or args.samples < 8:
        parser.error('invalid checkerboard dimensions or sample count')

    capture = cv2.VideoCapture(args.device, cv2.CAP_V4L2)
    if not capture.isOpened():
        parser.error(f'cannot open {args.device}')
    capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    pattern = (args.cols, args.rows)
    points_3d = np.zeros((args.cols * args.rows, 3), np.float32)
    points_3d[:, :2] = np.mgrid[:args.cols, :args.rows].T.reshape(-1, 2)
    points_3d *= args.square_size
    object_points = []
    image_points = []
    image_size = None
    print('Move the checkerboard across the image at varied angles and distances.')
    print('Press SPACE to capture a valid view, q to finish. No camera images are saved.')
    try:
        while len(image_points) < args.samples:
            ok, frame = capture.read()
            if not ok:
                continue
            image_size = (frame.shape[1], frame.shape[0])
            grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            found, corners = cv2.findChessboardCorners(
                grey, pattern, cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_NORMALIZE_IMAGE
            )
            if found:
                corners = cv2.cornerSubPix(
                    grey, corners, (11, 11), (-1, -1),
                    (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001),
                )
                cv2.drawChessboardCorners(frame, pattern, corners, found)
            cv2.putText(frame, f'{len(image_points)}/{args.samples} views', (15, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.imshow('Camera calibration - SPACE capture, q finish', frame)
            key = cv2.waitKey(1) & 0xff
            if key == ord('q'):
                break
            if key == ord(' ') and found:
                object_points.append(points_3d.copy())
                image_points.append(corners.copy())
                print(f'Captured {len(image_points)}/{args.samples}')
    finally:
        capture.release()
        cv2.destroyAllWindows()

    if len(image_points) < 8:
        parser.error('need at least 8 varied valid views; calibration not saved')
    rms, matrix, distortion, _, _ = cv2.calibrateCamera(
        object_points, image_points, image_size, None, None
    )
    if not np.isfinite(rms) or rms > 1.0:
        parser.error(f'reprojection RMS {rms:.3f} pixels is too high; retake views')
    data = calibration_data(matrix, distortion, *image_size)
    with Path(args.output).open('w', encoding='utf-8') as stream:
        yaml.safe_dump(data, stream, sort_keys=False)
    print(f'Saved {args.output}; reprojection RMS={rms:.3f} pixels')
