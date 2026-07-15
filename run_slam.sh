#!/bin/bash
source /opt/ros/jazzy/setup.bash
source /home/vantra/robot_ws/install/setup.bash

# Start SLAM node
ros2 launch robot_base slam_only.launch.py &
SLAM_PID=$!

# Chờ SLAM node xuất hiện
echo "Cho SLAM node khoi dong..."
for i in $(seq 1 30); do
    if ros2 lifecycle get /slam_toolbox 2>/dev/null | grep -q "unconfigured\|inactive\|active"; then
        echo "SLAM node san sang!"
        break
    fi
    sleep 2
done

# Configure và activate
echo "Configuring SLAM..."
ros2 lifecycle set /slam_toolbox configure
sleep 3
echo "Activating SLAM..."
ros2 lifecycle set /slam_toolbox activate
echo "SLAM da active!"

wait $SLAM_PID
