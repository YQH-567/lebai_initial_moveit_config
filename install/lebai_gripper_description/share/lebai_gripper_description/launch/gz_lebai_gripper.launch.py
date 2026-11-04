import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue
#from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    gripper_share_dir = get_package_share_directory('lebai_gripper_description')
    gripper_share_parent = os.path.dirname(gripper_share_dir)
    #default_world_path = gripper_share_dir + '/world/'
    robot_description = ParameterValue(
        Command([
            'xacro ',
            PathJoinSubstitution([
                # FindPackageShare('lebai_gripper_description'),
                gripper_share_dir,
                'urdf',
                'standalone_gripper.urdf.xacro'
            ])
        ]),
        value_type=str
    )

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare('ros_gz_sim'),
                'launch',
                'gz_sim.launch.py'
            ])
        ),
        launch_arguments={
            'gz_args': '-r empty.sdf'
        }.items()
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[
            {'robot_description': robot_description},
            {'use_sim_time': True}
        ],
        output='screen'
    )

    spawn_gripper = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'lebai_gripper',
            '-topic', 'robot_description',
            '-x', '0',
            '-y', '0',
            '-z', '0.0'
        ],
        output='screen'
    )

    clock_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'
        ],
        output='screen'
    )

    joint_state_broadcaster_spawner = TimerAction(
        #period=3.0,
        period=10.0,#这是为了适配gazebo的启动时间，gazebo启动较慢，过早启动会失败
        actions=[
            Node(
                package='controller_manager',
                executable='spawner',
                arguments=[
                    'joint_state_broadcaster',
                    '--controller-manager', '/controller_manager'
                    #'--controller-manager-timeout', '60'
                ],
                output='screen'
            )
        ]
    )

    gripper_controller_spawner = TimerAction(
        #period=4.0,
        period = 14.0, #这是为了适配gazebo的启动时间，gazebo启动较慢，过早启动会失败
        actions=[
            Node(
                package='controller_manager',
                executable='spawner',
                arguments=[
                    'gripper_controller',
                    '--controller-manager', '/controller_manager'
                    #'--controller-manager-timeout', '60'
                ],
                output='screen'
            )
        ]
    )

    return LaunchDescription([
        SetEnvironmentVariable(
            name='GZ_SIM_RESOURCE_PATH',
            value=gripper_share_parent
        ),
        gz_sim,
        clock_bridge,
        robot_state_publisher,
        spawn_gripper,
        joint_state_broadcaster_spawner,
        gripper_controller_spawner,
    ])