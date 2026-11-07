"""Run ArUco pose estimation with the Gazebo eye-in-hand camera."""

from launch import LaunchDescription
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='lebai_vision', executable='aruco_pose_node',
            name='aruco_pose_node', output='screen',
            parameters=[PathJoinSubstitution([
                FindPackageShare('lebai_vision'), 'config', 'aruco_sim.yaml'
            ])],
        )
    ])
