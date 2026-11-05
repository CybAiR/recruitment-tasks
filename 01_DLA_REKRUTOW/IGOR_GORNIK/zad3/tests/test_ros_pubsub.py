"""ROS 2 integration: command published on /arm/command reaches the controller,
which updates /joint_states (req. 4 and 5). Needs a sourced ROS 2 environment."""
import math
import os
import sys
import time

import pytest

rclpy = pytest.importorskip("rclpy")
from rclpy.executors import SingleThreadedExecutor  # noqa: E402
from sensor_msgs.msg import JointState  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from arm_controller_node import HOME_POSITIONS, JOINT_NAMES, STEP_RAD, ArmController  # noqa: E402
from arm_teleop_node import ArmTeleop  # noqa: E402


@pytest.fixture
def ros_graph():
    rclpy.init()
    controller = ArmController()
    teleop = ArmTeleop()
    probe = rclpy.create_node("test_probe")
    received = []
    probe.create_subscription(JointState, "/joint_states", received.append, 10)
    executor = SingleThreadedExecutor()
    for node in (controller, teleop, probe):
        executor.add_node(node)
    yield executor, teleop, received
    executor.shutdown()
    for node in (controller, teleop, probe):
        node.destroy_node()
    rclpy.shutdown()


def spin_until(executor, condition, timeout=5.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        executor.spin_once(timeout_sec=0.05)
        if condition():
            return True
    return False


def test_controller_publishes_ur5e_joint_states(ros_graph):
    executor, _, received = ros_graph
    assert spin_until(executor, lambda: len(received) > 0)
    assert list(received[-1].name) == JOINT_NAMES
    assert list(received[-1].position) == pytest.approx(HOME_POSITIONS)


def test_teleop_command_moves_joint(ros_graph):
    executor, teleop, received = ros_graph
    # Wait until discovery connects teleop -> controller before sending.
    assert spin_until(executor, lambda: teleop._publisher.get_subscription_count() > 0)
    teleop.send("2+")
    expected = HOME_POSITIONS[1] + STEP_RAD
    assert spin_until(
        executor,
        lambda: received and math.isclose(received[-1].position[1], expected, abs_tol=1e-9),
    ), "joint 2 did not move after '2+'"
