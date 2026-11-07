import cv2
from lebai_vision.pose_estimation import estimate_square_pose, marker_object_points
import numpy as np


def test_pose_is_recovered_from_synthetic_projection():
    camera_matrix = np.array([[600.0, 0.0, 320.0],
                              [0.0, 600.0, 240.0],
                              [0.0, 0.0, 1.0]])
    distortion = np.zeros(5)
    expected_rotation = np.array([0.12, -0.08, 0.04])
    expected_translation = np.array([0.03, -0.02, 0.65])
    corners, _ = cv2.projectPoints(
        marker_object_points(0.08), expected_rotation, expected_translation,
        camera_matrix, distortion,
    )

    result = estimate_square_pose(corners, 0.08, camera_matrix, distortion)

    assert result is not None
    assert np.allclose(result.translation, expected_translation, atol=1e-5)
    assert result.reprojection_error < 1e-5
    assert np.isclose(np.linalg.norm(result.quaternion_xyzw), 1.0)


def test_marker_points_have_requested_metric_size():
    points = marker_object_points(0.05)
    assert np.isclose(np.linalg.norm(points[1] - points[0]), 0.05)
    assert np.isclose(np.linalg.norm(points[2] - points[1]), 0.05)
