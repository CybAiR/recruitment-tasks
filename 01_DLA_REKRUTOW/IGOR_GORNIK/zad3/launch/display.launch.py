import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch.substitutions import Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

CURRENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def generate_launch_description() -> LaunchDescription:
    xacro_file = os.path.join(
        get_package_share_directory("ur_description"), "urdf", "ur.urdf.xacro"
    )
    robot_description = ParameterValue(
        Command(["xacro ", xacro_file, " ur_type:=ur5e name:=ur5e"]), value_type=str
    )

    return LaunchDescription([
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            parameters=[{"robot_description": robot_description}],
            output="screen",
        ),
        ExecuteProcess(
            cmd=["python3", os.path.join(CURRENT_DIR, "arm_controller_node.py")],
            output="screen",
        ),
        Node(
            package="rviz2",
            executable="rviz2",
            arguments=["-d", os.path.join(CURRENT_DIR, "config", "arm.rviz")],
            output="screen",
        ),
    ])
