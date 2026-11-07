"""Run a calibrated local UVC RGB camera and standalone ArUco 6D pose."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('device', default_value='/dev/video0'),
        DeclareLaunchArgument('calibration_file', default_value=''),
        DeclareLaunchArgument('marker_id', default_value='0'),
        DeclareLaunchArgument('marker_size', default_value='0.05'),
        Node(
            package='lebai_vision', executable='uvc_camera_node',
            name='uvc_camera_node', output='screen',
            parameters=[{
                'device': LaunchConfiguration('device'),
                'calibration_file': LaunchConfiguration('calibration_file'),
                'use_sim_time': False,
            }],
        ),
        Node(
            package='lebai_vision', executable='aruco_pose_node',
            name='aruco_pose_node', output='screen',
            parameters=[{
                'image_topic': '/camera/color/image_raw',
                'camera_info_topic': '/camera/color/camera_info',
                'marker_id': ParameterValue(LaunchConfiguration('marker_id'), value_type=int),
                'marker_size': ParameterValue(LaunchConfiguration('marker_size'), value_type=float),
                'output_frame': '',
                'use_sim_time': False,
            }],
        ),
    ])
