import sys
import termios
import tty
from typing import Optional
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

COMMAND_TOPIC = "/arm/command"

KEY_BINDINGS = {
    "q": "1+", "a": "1-",
    "w": "2+", "s": "2-",
    "e": "3+", "d": "3-",
    "r": "4+", "f": "4-",
    "t": "5+", "g": "5-",
    "y": "6+", "h": "6-",
    "0": "home",
}
QUIT_KEYS = {"x", "\x03"}

HELP = """
Arm teleop (UR5e) -- publishes on /arm/command
  joint:   1   2   3   4   5   6
  plus:    q   w   e   r   t   y
  minus:   a   s   d   f   g   h
  0 = home, x = quit
"""


def key_to_command(key: str) -> Optional[str]:
    return KEY_BINDINGS.get(key.lower())


def read_key() -> str:
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


class ArmTeleop(Node):
    def __init__(self) -> None:
        super().__init__("arm_teleop")
        self._publisher = self.create_publisher(String, COMMAND_TOPIC, 10)

    def send(self, command: str) -> None:
        self._publisher.publish(String(data=command))


def main() -> None:
    if not sys.stdin.isatty():
        sys.exit("arm_teleop needs an interactive terminal (docker exec -it ...)")
    rclpy.init()
    node = ArmTeleop()
    print(HELP)
    try:
        while True:
            key = read_key()
            if key in QUIT_KEYS:
                break
            command = key_to_command(key)
            if command is None:
                continue
            node.send(command)
            print(f"sent: {command}\r")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
