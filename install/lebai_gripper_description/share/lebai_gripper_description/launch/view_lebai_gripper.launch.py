import os
from ament_index_python.packages import get_package_share_path
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch.conditions import IfCondition
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    lebai_gripper_description_path = get_package_share_path('lebai_gripper_description')
    lebai_gripper_model_path = lebai_gripper_description_path / 'urdf/gripper.xacro'
    default_rviz_config_path = lebai_gripper_description_path / 'rviz/view.rviz'
    rviz_config_arg = DeclareLaunchArgument(name='rvizconfig', default_value=str(default_rviz_config_path),
                                            description='Absolute path to rviz config file')
    #gripper_urdf = Command(['xacro ', str(lebai_gripper_model_path)])
    gripper_urdf = ParameterValue(
    Command(['xacro ', str(lebai_gripper_model_path)]),
    value_type=str)
    joint_state_publisher_arg = DeclareLaunchArgument(name='joint_state_publisher',default_value='true', choices=['true', 'false'],
                                                      description='Flag to enable joint_state_publisher_gui')
    
    # model_file= LaunchConfiguration('model')
    joint_state_publisher_condition = LaunchConfiguration('joint_state_publisher')
    # rviz_condition = LaunchConfiguration('rviz')

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': gripper_urdf}],
        output='screen'
    )
    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        parameters=[{'robot_description': gripper_urdf}],
        output='screen',
        condition=IfCondition(joint_state_publisher_condition),
    )
    rviz_node=Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', LaunchConfiguration('rvizconfig')],
    )
    return LaunchDescription([
        joint_state_publisher_arg,
        rviz_config_arg,
        joint_state_publisher_gui_node,
        robot_state_publisher_node,
        rviz_node
    ])
