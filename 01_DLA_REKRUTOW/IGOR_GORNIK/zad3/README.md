# Virtual UR5e arm control (ROS 2 Jazzy, Python, RViz 2)

Keyboard in a terminal → `arm_teleop` → topic `/arm/command` → `arm_controller` → `/joint_states`
→ `robot_state_publisher` → TF → RViz 2.

## Architecture

| Element | File | Role |
|---|---|---|
| Model | `ur_description` (apt), `ur.urdf.xacro ur_type:=ur5e` | ready-made URDF of the 6-DOF UR5e manipulator |
| Publisher | `arm_teleop_node.py` (node `arm_teleop`) | reads single key presses, publishes `std_msgs/String` on `/arm/command` |
| Subscriber | `arm_controller_node.py` (node `arm_controller`) | receives commands, updates 6 joints (0.05 rad step, URDF limits), publishes `sensor_msgs/JointState` on `/joint_states` at 30 Hz |
| Visualization | `launch/display.launch.py`, `config/arm.rviz` | starts `robot_state_publisher`, the controller and RViz 2 |
| Tests | `tests/` | command logic and publisher → subscriber → `/joint_states` integration |

Command format on `/arm/command`: `"<joint 1-6><+|->"` (e.g. `"3+"`) or `"home"`.

Key bindings:

```
joint:    1   2   3   4   5   6
plus:     q   w   e   r   t   y
minus:    a   s   d   f   g   h
0 = home, x = quit
```

## How to run

Runs in Docker. The base image `tiryoh/ros2-desktop-vnc:jazzy` serves a desktop
in the browser (noVNC), because I'm too lazy to install VM on my work laptop (normally I'm using Linux, so don't worry, I know a thing or two about the ecosystem we'll be working in).

### 1. Build the image (once)

From the `IGOR_GORNIK/zad3` directory:

```bash
docker build -t zad3_arm .
```

### 2. Start the container with the desktop

```bash
docker run -d --name arm -p 6080:80 --shm-size=512m -v "$(pwd)":/workspace zad3_arm
```

Open http://localhost:6080 in a browser and **Connect**.

### 3. Terminal 1: model + controller + RViz 2

```bash
docker exec -it -u ubuntu -e DISPLAY=:1 arm bash
source /opt/ros/jazzy/setup.bash
cd /workspace
ros2 launch launch/display.launch.py
```

RViz 2 opens in the browser desktop with the UR5e arm in its home pose.

### 4. Terminal 2: keyboard control

```bash
docker exec -it -u ubuntu arm bash
source /opt/ros/jazzy/setup.bash
python3 /workspace/arm_teleop_node.py
```

Press `q`/`a`, `w`/`s` … and watch the arm move in RViz.

### 5. Terminal 3: inspect communication (optional)

```bash
docker exec -it -u ubuntu arm bash
source /opt/ros/jazzy/setup.bash
ros2 topic echo /arm/command          # commands from teleop
ros2 topic echo /joint_states         # joint positions
ros2 topic pub --once /arm/command std_msgs/msg/String "data: '2+'"   # command without teleop
```

## Tests

```bash
docker exec -u ubuntu arm bash -c "source /opt/ros/jazzy/setup.bash && cd /workspace && python3 -m pytest -q -p no:cacheprovider tests"
```

| Test | Requirement |
|---|---|
| `test_parse_valid_commands`, `test_parse_rejects_garbage` | 3: command format, invalid ones are ignored |
| `test_every_key_maps_to_a_valid_command` | 3: every teleop key produces a valid command |
| `test_move_changes_only_selected_joint`, `test_move_is_clamped_to_limits`, `test_home_resets_all_joints` | 5: joint configuration update |
| `test_controller_publishes_ur5e_joint_states` | 1, 5: `/joint_states` with the 6 UR5e joint names |
| `test_teleop_command_moves_joint` | 4, 5: a command from `arm_teleop` sent over the topic moves a joint in `arm_controller` |

## Cleanup

```bash
docker rm -f arm
```
