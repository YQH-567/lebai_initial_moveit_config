# 怎么单独加载加爪到gazebo(gz_sim)或者rviz中

## 怎么快速启动这个包的项目
   - 启动rviz和joint_state_publisher_gui：
    ```
    ros2 launch lebai_gripper_description view_lebai_gripper
    ```
   - 启动gz_sim仿真：
    ```
    ros2 launch lebai_gripper_description gz_lebai_gripper
    ```
   - 启动 gz_sim仿真之后怎么给它下发指令
    ```
        ros2 action send_goal /gripper_controller/follow_joint_trajectory \
            control_msgs/action/FollowJointTrajectory \
            "{
            trajectory: {
                joint_names: [
                'gripper_r_joint1',
                'gripper_r_joint2',
                'gripper_r_joint_finger',
                'gripper_l_joint1',
                'gripper_l_joint2',
                'gripper_l_joint_finger'
                ],
                points: [
                {
                    positions: [1.0, -1.0, -1.0, 1.0, -1.0, -1.0], 
                    time_from_start: {sec: 2}
                }
                ]
            }
            }"
    ```
    上名是张开，闭合是把 `positions` 改成 `positions: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]`
    半开则是 把 `positions` 改成 `positions: [0.5, -0.5, -0.5, 0.5, -0.5, -0.5]`

    - 保险操作：
    1. 启动 Gazebo
    2. 等模型完全显示 / 稳定
    3. 手动启动 joint_state_broadcaster
    4. 手动启动 gripper_controller
    5. 下发夹爪开合命令
    - 具体步骤
    那就可以先把 launch 里的两个 spawner 注释掉：
    ```
    # joint_state_broadcaster_spawner,
    # gripper_controller_spawner,
    ```

    启动 Gazebo 后手动执行：
    ```
    ros2 run controller_manager spawner joint_state_broadcaster \
    --controller-manager /controller_manager \
    --controller-manager-timeout 60
    ```
    再执行：
    ```
    ros2 run controller_manager spawner gripper_controller \
    --controller-manager /controller_manager \
    --controller-manager-timeout 60
    ```
    确认：

    `ros2 control list_controllers`

    应该看到：

    `joint_state_broadcaster    active`
    `gripper_controller         active`

## 1 加爪模型和机械臂模型同样collision和vision是不一样的

## 2 怎么首先写launch文件在rviz中显示加爪

## 3 要在gazebo中加载需要怎么加依赖，修改txt,写launch文件，yaml配置文件

### 1 加载什么依赖
### 2 怎么修改txt，怎么理解更好记忆
### 3 如果你有写launch文件的基础，怎么快速复制以及修改launch
### 4 ros2-control的对应逻辑以及这个yaml怎么快速配置

## 4 本体文件和两个宏文件的配置方法和注意事项（特别是mimic等的函数问题）

## 5 启动时一些节点需要延时的原因

## 6 怎么测试你写的是否成功



