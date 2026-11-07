# 独立夹爪检查

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 launch lebai_gripper_description view_lebai_gripper.launch.py
```

在 `joint_state_publisher_gui` 中只调整 `gripper_r_joint1`，观察两侧五个 mimic 关节随动。Gazebo 单独仿真使用：

```bash
ros2 launch lebai_gripper_description gz_lebai_gripper.launch.py
```

待两个控制器激活后，另开终端发送主动关节目标：

```bash
ros2 action send_goal /gripper_controller/follow_joint_trajectory \
  control_msgs/action/FollowJointTrajectory \
  '{trajectory: {joint_names: [gripper_r_joint1], points: [{positions: [0.7], time_from_start: {sec: 2}}]}}'
```

`0.0` 是模型默认张开位置，`1.0` 是闭合位置；真机方向和机械限位需实物确认。可用 `ros2 topic echo /joint_states` 查看主动关节和从动关节反馈。Gazebo 使用一个主动命令接口和五个从动状态接口，符合 [gz_ros2_control 的 mimic 约定](https://github.com/ros-controls/gz_ros2_control/blob/rolling/doc/index.rst)。

组合机械臂和 MoveIt 的说明见工作区根目录 `README.md`。
