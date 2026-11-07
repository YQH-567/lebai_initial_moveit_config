# 独立夹爪控制器

`gripper_controllers.yaml` 只给 `gripper_r_joint1` 发送位置命令。其余五个关节在 URDF 中通过 `<mimic>` 联动，并在 `ros2_control` 中只提供位置、速度状态接口。不要把 mimic 关节再加入轨迹控制器的命令关节列表。

启动方式、开合指令和检查方法见同包的 `readme.md`。夹爪参数以 `urdf/gripper_macro.xacro` 和本目录 YAML 为准。
