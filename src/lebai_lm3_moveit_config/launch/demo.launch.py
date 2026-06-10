from moveit_configs_utils import MoveItConfigsBuilder
from moveit_configs_utils.launches import generate_demo_launch


def generate_launch_description():
    moveit_config = MoveItConfigsBuilder("lebai_lm3", package_name="lebai_lm3_moveit_config").to_moveit_configs()
    return generate_demo_launch(moveit_config)

# from moveit_configs_utils import MoveItConfigsBuilder
# from moveit_configs_utils.launches import generate_demo_launch


# def generate_launch_description():
#     moveit_config = (
#         MoveItConfigsBuilder("lebai_lm3", package_name="lebai_lm3_moveit_config")
#         .robot_description(file_path="config/lebai_lm3.urdf.xacro")
#         .robot_description_semantic(file_path="config/lebai_lm3.srdf")
#         .trajectory_execution(file_path="config/moveit_controllers.yaml")
#         .planning_pipelines(pipelines=["ompl"])
#         .to_moveit_configs()
#     )

#     return generate_demo_launch(moveit_config)
