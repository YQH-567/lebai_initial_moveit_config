"""OpenCV-only helpers for square fiducial pose estimation."""

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass(frozen=True)
class PoseEstimate:
    """Pose of a marker in the camera optical frame."""

    rotation_vector: np.ndarray
    translation: np.ndarray
    quaternion_xyzw: np.ndarray
    reprojection_error: float


def marker_object_points(marker_size: float) -> np.ndarray:
    """Return IPPE_SQUARE points centered on a marker, in metres."""
    half = marker_size / 2.0
    return np.array([
        [-half, half, 0.0],
        [half, half, 0.0],
        [half, -half, 0.0],
        [-half, -half, 0.0],
    ], dtype=np.float64)


def rotation_matrix_to_quaternion(matrix: np.ndarray) -> np.ndarray:
    """Convert a 3x3 rotation matrix to a normalized x,y,z,w quaternion."""
    m = np.asarray(matrix, dtype=np.float64)
    trace = np.trace(m)
    if trace > 0.0:
        scale = np.sqrt(trace + 1.0) * 2.0
        q = np.array([
            (m[2, 1] - m[1, 2]) / scale,
            (m[0, 2] - m[2, 0]) / scale,
            (m[1, 0] - m[0, 1]) / scale,
            0.25 * scale,
        ])
    else:
        index = int(np.argmax(np.diag(m)))
        if index == 0:
            scale = np.sqrt(1.0 + m[0, 0] - m[1, 1] - m[2, 2]) * 2.0
            q = np.array([0.25 * scale,
                          (m[0, 1] + m[1, 0]) / scale,
                          (m[0, 2] + m[2, 0]) / scale,
                          (m[2, 1] - m[1, 2]) / scale])
        elif index == 1:
            scale = np.sqrt(1.0 + m[1, 1] - m[0, 0] - m[2, 2]) * 2.0
            q = np.array([(m[0, 1] + m[1, 0]) / scale,
                          0.25 * scale,
                          (m[1, 2] + m[2, 1]) / scale,
                          (m[0, 2] - m[2, 0]) / scale])
        else:
            scale = np.sqrt(1.0 + m[2, 2] - m[0, 0] - m[1, 1]) * 2.0
            q = np.array([(m[0, 2] + m[2, 0]) / scale,
                          (m[1, 2] + m[2, 1]) / scale,
                          0.25 * scale,
                          (m[1, 0] - m[0, 1]) / scale])
    return q / np.linalg.norm(q)


def estimate_square_pose(corners: np.ndarray, marker_size: float,
                         camera_matrix: np.ndarray,
                         distortion: np.ndarray) -> PoseEstimate | None:
    """Estimate marker-to-camera pose and reject solutions behind the camera."""
    image_points = np.asarray(corners, dtype=np.float64).reshape(4, 2)
    object_points = marker_object_points(marker_size)
    result = cv2.solvePnPGeneric(
        object_points,
        image_points,
        np.asarray(camera_matrix, dtype=np.float64).reshape(3, 3),
        np.asarray(distortion, dtype=np.float64),
        flags=cv2.SOLVEPNP_IPPE_SQUARE,
    )
    if not result[0]:
        return None

    candidates = []
    for rotation_vector, translation in zip(result[1], result[2]):
        translation = np.asarray(translation).reshape(3)
        if translation[2] <= 0.0:
            continue
        projected, _ = cv2.projectPoints(
            object_points, rotation_vector, translation,
            camera_matrix, distortion,
        )
        error = float(np.sqrt(np.mean(np.sum(
            (projected.reshape(4, 2) - image_points) ** 2, axis=1
        ))))
        candidates.append((error, rotation_vector, translation))

    if not candidates:
        return None
    error, rotation_vector, translation = min(candidates, key=lambda item: item[0])
    rotation, _ = cv2.Rodrigues(rotation_vector)
    return PoseEstimate(
        np.asarray(rotation_vector).reshape(3),
        translation,
        rotation_matrix_to_quaternion(rotation),
        error,
    )
