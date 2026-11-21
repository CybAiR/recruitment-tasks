import math
from typing import List, Optional, Tuple
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import String

COMMAND_TOPIC = "/arm/command"
JOINT_STATES_TOPIC = "/joint_states"
PUBLISH_RATE_HZ = 30.0
STEP_RAD = 0.05

JOINT_NAMES = [
    "shoulder_pan_joint",
    "shoulder_lift_joint",
    "elbow_joint",
    "wrist_1_joint",
    "wrist_2_joint",
    "wrist_3_joint",
]

JOINT_LIMITS = [
    (-2 * math.pi, 2 * math.pi),
    (-2 * math.pi, 2 * math.pi),
    (-math.pi, math.pi),
    (-2 * math.pi, 2 * math.pi),
    (-2 * math.pi, 2 * math.pi),
    (-2 * math.pi, 2 * math.pi),
]

HOME_POSITIONS = [0.0, -1.57, 1.57, -1.57, -1.57, 0.0]

# Returns ("home", 0, 0), ("move", joint_index, direction) or None
def parse_command(text: str) -> Optional[Tuple[str, int, int]]:
    cmd = text.strip().lower()
    if cmd == "home":
        return ("home", 0, 0)
    if len(cmd) == 2 and cmd[0] in "123456" and cmd[1] in "+-":
        return ("move", int(cmd[0]) - 1, 1 if cmd[1] == "+" else -1)
    return None

def apply_command(positions: List[float], parsed: Tuple[str, int, int]) -> List[float]:
    kind, index, direction = parsed
    if kind == "home":
        return list(HOME_POSITIONS)
    new_positions = list(positions)
    low, high = JOINT_LIMITS[index]
    new_positions[index] = min(high, max(low, positions[index] + direction * STEP_RAD))
    return new_positions

class ArmController(Node):
    def __init__(self) -> None:
        super().__init__("arm_controller")
        self._positions = list(HOME_POSITIONS)
        self._publisher = self.create_publisher(JointState, JOINT_STATES_TOPIC, 10)
        self.create_subscription(String, COMMAND_TOPIC, self._on_command, 10)
        self.create_timer(1.0 / PUBLISH_RATE_HZ, self._publish_state)
        self.get_logger().info(f"Listening on {COMMAND_TOPIC}, publishing {JOINT_STATES_TOPIC}")

    def _on_command(self, msg: String) -> None:
        parsed = parse_command(msg.data)
        if parsed is None:
            self.get_logger().warning(f"Unknown command: {msg.data!r}")
            return
        self._positions = apply_command(self._positions, parsed)
        self.get_logger().info(
            f"{msg.data} -> " + ", ".join(f"{p:+.2f}" for p in self._positions)
        )

    def _publish_state(self) -> None:
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = list(JOINT_NAMES)
        msg.position = list(self._positions)
        self._publisher.publish(msg)


def main() -> None:
    rclpy.init()
    node = ArmController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
