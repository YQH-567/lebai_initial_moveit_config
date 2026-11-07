"""ROS 2 node that publishes the 6D pose of a selected ArUco marker."""

import cv2
from cv_bridge import CvBridge
from geometry_msgs.msg import PoseStamped, TransformStamped
import numpy as np
import rclpy
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import CameraInfo, Image
from tf2_geometry_msgs import do_transform_pose_stamped
from tf2_ros import Buffer, TransformBroadcaster, TransformException, TransformListener

from .pose_estimation import estimate_square_pose


class ArucoPoseNode(Node):
    """Detect one square marker and expose its filtered 6D pose."""

    def __init__(self):
        super().__init__('aruco_pose_node')
        self.declare_parameter('image_topic', '/hand_camera/image_raw')
        self.declare_parameter('camera_info_topic', '/hand_camera/camera_info')
        self.declare_parameter('marker_id', 0)
        self.declare_parameter('marker_size', 0.05)
        self.declare_parameter('dictionary', 'DICT_4X4_50')
        self.declare_parameter('output_frame', '')
        self.declare_parameter('child_frame', 'detected_object')
        self.declare_parameter('max_reprojection_error', 3.0)
        self.declare_parameter('publish_debug_image', True)

        if self.get_parameter('marker_size').value <= 0.0:
            raise ValueError('marker_size must be positive (metres)')
        if self.get_parameter('max_reprojection_error').value <= 0.0:
            raise ValueError('max_reprojection_error must be positive (pixels)')

        dictionary_name = self.get_parameter('dictionary').value
        dictionary_id = getattr(cv2.aruco, dictionary_name, None)
        if dictionary_id is None:
            raise ValueError(f'Unsupported ArUco dictionary: {dictionary_name}')
        self.dictionary = cv2.aruco.getPredefinedDictionary(dictionary_id)
        self.detector_parameters = cv2.aruco.DetectorParameters_create()
        self.detector_parameters.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX

        self.bridge = CvBridge()
        self.camera_info = None
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.tf_broadcaster = TransformBroadcaster(self)
        self.pose_publisher = self.create_publisher(PoseStamped, 'object_pose', 10)
        self.debug_publisher = self.create_publisher(Image, 'debug_image', 2)
        self.create_subscription(
            CameraInfo, self.get_parameter('camera_info_topic').value,
            self._camera_info_callback, qos_profile_sensor_data,
        )
        self.create_subscription(
            Image, self.get_parameter('image_topic').value,
            self._image_callback, qos_profile_sensor_data,
        )

    def _camera_info_callback(self, message):
        if message.k[0] > 0.0 and message.k[4] > 0.0:
            self.camera_info = message

    def _image_callback(self, message):
        if self.camera_info is None:
            self.get_logger().warn(
                'Waiting for a valid CameraInfo message',
                throttle_duration_sec=5.0,
            )
            return
        image = self.bridge.imgmsg_to_cv2(message, desired_encoding='bgr8')
        corners, ids, _ = cv2.aruco.detectMarkers(
            image, self.dictionary, parameters=self.detector_parameters
        )
        target_id = self.get_parameter('marker_id').value
        estimate = None
        selected_corners = None
        if ids is not None:
            for marker_corners, marker_id in zip(corners, ids.flatten()):
                if int(marker_id) == target_id:
                    selected_corners = marker_corners
                    estimate = estimate_square_pose(
                        marker_corners,
                        self.get_parameter('marker_size').value,
                        np.array(self.camera_info.k).reshape(3, 3),
                        np.array(self.camera_info.d),
                    )
                    break

        if estimate is not None and estimate.reprojection_error <= self.get_parameter(
                'max_reprojection_error').value:
            pose = self._make_pose(message, estimate)
            pose = self._transform_pose_if_requested(pose)
            if pose is not None:
                self.pose_publisher.publish(pose)
                self.tf_broadcaster.sendTransform(self._make_transform(pose))
            cv2.drawFrameAxes(
                image, np.array(self.camera_info.k).reshape(3, 3),
                np.array(self.camera_info.d), estimate.rotation_vector,
                estimate.translation,
                self.get_parameter('marker_size').value * 0.5,
            )
        if ids is not None:
            cv2.aruco.drawDetectedMarkers(image, corners, ids)
        if selected_corners is None and ids is not None:
            cv2.putText(image, f'marker {target_id} not visible', (20, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        if self.get_parameter('publish_debug_image').value:
            debug = self.bridge.cv2_to_imgmsg(image, encoding='bgr8')
            debug.header = message.header
            self.debug_publisher.publish(debug)

    @staticmethod
    def _make_pose(image_message, estimate):
        pose = PoseStamped()
        pose.header = image_message.header
        pose.pose.position.x, pose.pose.position.y, pose.pose.position.z = (
            float(value) for value in estimate.translation
        )
        pose.pose.orientation.x, pose.pose.orientation.y, \
            pose.pose.orientation.z, pose.pose.orientation.w = (
                float(value) for value in estimate.quaternion_xyzw
            )
        return pose

    def _transform_pose_if_requested(self, pose):
        output_frame = self.get_parameter('output_frame').value
        if not output_frame or output_frame == pose.header.frame_id:
            return pose
        try:
            transform = self.tf_buffer.lookup_transform(
                output_frame, pose.header.frame_id, pose.header.stamp,
                timeout=Duration(seconds=0.05),
            )
            return do_transform_pose_stamped(pose, transform)
        except TransformException as error:
            self.get_logger().warn(
                f'Cannot transform detection to {output_frame}: {error}',
                throttle_duration_sec=2.0,
            )
            return None

    def _make_transform(self, pose):
        transform = TransformStamped()
        transform.header = pose.header
        transform.child_frame_id = self.get_parameter('child_frame').value
        transform.transform.translation.x = pose.pose.position.x
        transform.transform.translation.y = pose.pose.position.y
        transform.transform.translation.z = pose.pose.position.z
        transform.transform.rotation = pose.pose.orientation
        return transform


def main(args=None):
    rclpy.init(args=args)
    node = ArucoPoseNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
