"""Publish a calibrated UVC RGB camera without a robot or Gazebo."""

from pathlib import Path

import cv2
from cv_bridge import CvBridge
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import CameraInfo, Image
import yaml


def load_camera_info(path: str, width: int, height: int) -> CameraInfo:
    """Load a ROS camera calibration YAML and reject mismatched resolution."""
    with Path(path).open(encoding='utf-8') as stream:
        data = yaml.safe_load(stream)
    if data['image_width'] != width or data['image_height'] != height:
        raise ValueError(
            f'Calibration resolution {data["image_width"]}x{data["image_height"]}'
            f' differs from camera stream {width}x{height}'
        )
    info = CameraInfo()
    info.width = width
    info.height = height
    info.distortion_model = data.get('distortion_model', 'plumb_bob')
    info.d = [float(value) for value in data['distortion_coefficients']['data']]
    info.k = [float(value) for value in data['camera_matrix']['data']]
    info.r = [float(value) for value in data['rectification_matrix']['data']]
    info.p = [float(value) for value in data['projection_matrix']['data']]
    if info.k[0] <= 0.0 or info.k[4] <= 0.0:
        raise ValueError('Camera calibration has invalid focal lengths')
    return info


class UvcCameraNode(Node):
    """Read the Orbbec UVC color stream and publish matching CameraInfo."""

    def __init__(self):
        super().__init__('uvc_camera_node')
        self.declare_parameter('device', '/dev/video0')
        self.declare_parameter('width', 640)
        self.declare_parameter('height', 480)
        self.declare_parameter('fps', 30.0)
        self.declare_parameter('frame_id', 'camera_color_optical_frame')
        self.declare_parameter('calibration_file', '')

        device = self.get_parameter('device').value
        self.capture = cv2.VideoCapture(device, cv2.CAP_V4L2)
        if not self.capture.isOpened():
            raise RuntimeError(f'Cannot open UVC RGB camera {device}')
        self.capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.get_parameter('width').value)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.get_parameter('height').value)
        self.capture.set(cv2.CAP_PROP_FPS, self.get_parameter('fps').value)
        width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = float(self.capture.get(cv2.CAP_PROP_FPS))
        if width <= 0 or height <= 0:
            self.capture.release()
            raise RuntimeError('Camera returned invalid image dimensions')

        calibration_file = self.get_parameter('calibration_file').value
        self.camera_info = None
        if calibration_file:
            try:
                self.camera_info = load_camera_info(calibration_file, width, height)
            except (OSError, KeyError, TypeError, ValueError) as error:
                self.capture.release()
                raise RuntimeError(f'Invalid camera calibration: {error}') from error
        else:
            self.get_logger().warn(
                'No calibration_file provided: publishing RGB only. '
                '6D metric pose requires a calibrated CameraInfo.'
            )
        self.bridge = CvBridge()
        self.image_publisher = self.create_publisher(
            Image, '/camera/color/image_raw', qos_profile_sensor_data
        )
        self.info_publisher = self.create_publisher(
            CameraInfo, '/camera/color/camera_info', qos_profile_sensor_data
        )
        self.frame_id = self.get_parameter('frame_id').value
        self.get_logger().info(f'Opened {device}: {width}x{height} at {fps:g} FPS')
        self.timer = self.create_timer(1.0 / max(fps, 1.0), self._publish_frame)

    def _publish_frame(self):
        ok, frame = self.capture.read()
        if not ok:
            self.get_logger().warn('Camera frame read failed', throttle_duration_sec=5.0)
            return
        image = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
        image.header.stamp = self.get_clock().now().to_msg()
        image.header.frame_id = self.frame_id
        self.image_publisher.publish(image)
        if self.camera_info is not None:
            self.camera_info.header = image.header
            self.info_publisher.publish(self.camera_info)

    def destroy_node(self):
        self.capture.release()
        return super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = UvcCameraNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
