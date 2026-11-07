"""Spawn the LM3, gripper and eye-in-hand camera in Gazebo Sim."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    description = ParameterValue(
        Command([
            'xacro ',
            PathJoinSubstitution([
                FindPackageShare('lebai_arm_description'),
                'urdf',
                'lm3_with_gripper.xacro',
            ]),
            ' use_fake_hardware:=false use_gazebo:=true use_camera:=true',
        ]),
        value_type=str,
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare('ros_gz_sim'), 'launch', 'gz_sim.launch.py'
            ])
        ),
        launch_arguments={'gz_args': '-r empty.sdf'}.items(),
    )

    state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': description, 'use_sim_time': True}],
        output='screen',
    )
    spawn = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-name', 'lebai_lm3', '-topic', 'robot_description'],
        output='screen',
    )
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['--ros-args', '-p', 'config_file:=' + os.path.join(
            get_package_share_directory('lebai_bringup'),
            'config', 'gz_bridge.yaml',
        )],
        output='screen',
    )
    image_bridge = Node(
        package='ros_gz_image',
        executable='image_bridge',
        arguments=['/hand_camera/image_raw'],
        output='screen',
    )

    spawners = TimerAction(
        period=5.0,
        actions=[
            Node(
                package='controller_manager', executable='spawner',
                arguments=['joint_state_broadcaster',
                           '--controller-manager-timeout', '60'],
            ),
            Node(
                package='controller_manager', executable='spawner',
                arguments=['lebai_arm_controller', 'gripper_controller',
                           '--controller-manager-timeout', '60'],
            ),
        ],
    )

    return LaunchDescription([
        gazebo, bridge, image_bridge, state_publisher, spawn, spawners
    ])
