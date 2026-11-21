"""Pure-logic tests: command parsing, joint updates, limits, key bindings (req. 3 and 5)."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from arm_controller_node import (  # noqa: E402
    HOME_POSITIONS,
    JOINT_LIMITS,
    STEP_RAD,
    apply_command,
    parse_command,
)
from arm_teleop_node import KEY_BINDINGS, key_to_command  # noqa: E402


def test_parse_valid_commands():
    assert parse_command("1+") == ("move", 0, 1)
    assert parse_command(" 6- ") == ("move", 5, -1)
    assert parse_command("HOME") == ("home", 0, 0)


def test_parse_rejects_garbage():
    for bad in ["", "7+", "0+", "1", "1*", "+1", "jump"]:
        assert parse_command(bad) is None, bad


def test_move_changes_only_selected_joint():
    after = apply_command(HOME_POSITIONS, ("move", 2, 1))
    assert math.isclose(after[2], HOME_POSITIONS[2] + STEP_RAD)
    assert after[:2] == HOME_POSITIONS[:2] and after[3:] == HOME_POSITIONS[3:]


def test_move_is_clamped_to_limits():
    positions = list(HOME_POSITIONS)
    for _ in range(1000):
        positions = apply_command(positions, ("move", 2, 1))
    assert positions[2] == JOINT_LIMITS[2][1]


def test_home_resets_all_joints():
    moved = apply_command(HOME_POSITIONS, ("move", 0, 1))
    assert apply_command(moved, ("home", 0, 0)) == HOME_POSITIONS


def test_every_key_maps_to_a_valid_command():
    for key in KEY_BINDINGS:
        assert parse_command(key_to_command(key)) is not None, key
    assert key_to_command("z") is None
