"""Start the LM3 + gripper MoveIt demo with mock ros2_control hardware."""

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    demo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare('lebai_lm3_moveit_config'),
                'launch',
                'demo.launch.py',
            ])
        )
    )
    return LaunchDescription([demo])
