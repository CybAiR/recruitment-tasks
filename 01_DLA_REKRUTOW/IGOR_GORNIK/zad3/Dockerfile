FROM tiryoh/ros2-desktop-vnc:jazzy

RUN apt-get update && apt-get install -y \
    ros-jazzy-ur-description \
    ros-jazzy-xacro \
    ros-jazzy-robot-state-publisher \
    python3-pytest \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
