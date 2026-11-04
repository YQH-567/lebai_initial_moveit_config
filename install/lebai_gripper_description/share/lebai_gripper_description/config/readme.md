 controller_manager:
   ros__parameters:
     update_rate: 100

     joint_state_broadcaster:
       type: joint_state_broadcaster/JointStateBroadcaster

     gripper_controller:
       type: joint_trajectory_controller/JointTrajectoryController

 gripper_controller:
   ros__parameters:
     joints:
       - gripper_r_joint1   #这是唯一的主动关节，其他都是被动的模仿关节，跟着它一起动。范围0~1

     command_interfaces:
       - position

     state_interfaces:
       - position
       - velocity

     allow_partial_joints_goal: false
     open_loop_control: true

# 上面是以为mimic能在gazebo中识别使用写的配置文件，但是用不了，只能都控制了

# 下面是修改后的配置文件，注释掉了mimic参数，并且把所有关节都加入控制器的joints列表中，范围也都改成了0~1或者-1~0