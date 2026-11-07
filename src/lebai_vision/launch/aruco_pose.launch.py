"""Launch the ArUco 6D pose estimator."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('image_topic', default_value='/camera/color/image_raw'),
        DeclareLaunchArgument('camera_info_topic', default_value='/camera/color/camera_info'),
        DeclareLaunchArgument('marker_id', default_value='0'),
        DeclareLaunchArgument('marker_size', default_value='0.05'),
        DeclareLaunchArgument('output_frame', default_value=''),
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        Node(
            package='lebai_vision',
            executable='aruco_pose_node',
            name='aruco_pose_node',
            parameters=[PathJoinSubstitution([
                FindPackageShare('lebai_vision'), 'config', 'aruco.yaml'
            ]), {
                'image_topic': LaunchConfiguration('image_topic'),
                'camera_info_topic': LaunchConfiguration('camera_info_topic'),
                'marker_id': ParameterValue(LaunchConfiguration('marker_id'), value_type=int),
                'marker_size': ParameterValue(LaunchConfiguration('marker_size'), value_type=float),
                'output_frame': LaunchConfiguration('output_frame'),
                'use_sim_time': ParameterValue(LaunchConfiguration('use_sim_time'), value_type=bool),
            }],
            output='screen',
        )
    ])
