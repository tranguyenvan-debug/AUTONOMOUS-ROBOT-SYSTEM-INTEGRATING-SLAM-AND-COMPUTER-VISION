# Autonomous Robot System Integrating SLAM and Computer Vision

This project features an autonomous mobile robot system built on **ROS 2 Jazzy** and an **ESP32** microcontroller. It integrates advanced capabilities like Simultaneous Localization and Mapping (SLAM), autonomous navigation (Nav2), and real-time object detection via **YOLOv8** using computer vision.

**Advisor:** Assoc. Prof. Dr. Ha Hoang Kha

---

## 🚀 Key Features
* **SLAM & Mapping:** Real-time 2D map generation utilizing LiDAR/depth data.
* **Autonomous Navigation:** Path planning and dynamic obstacle avoidance powered by ROS 2 Nav2.
* **Computer Vision (YOLOv8):** Real-time object detection and classification running seamlessly on edge nodes.
* **Hardware Interface:** Low-level motor control and sensor feedback managed by ESP32 via Micro-ROS.
* **Web Dashboard:** An intuitive web interface for remote monitoring and control.

---

## 📁 Repository Structure

* `robot_ws/` - Core ROS 2 Workspace (contains custom navigation, SLAM configurations, and map-merging packages).
* `Firmware ESP32/` - Low-level firmware code developed using PlatformIO.
* `robot_web/` - Source code for the remote web control dashboard.
* `SolidWorks Robot/` - Mechanical design files (`.sldprt`, `.sldasm`) and chassis assembly blueprints.
* `Schematic System/` - Electronic circuit schematics and wiring connections.
* `System Block Diagram/` - High-level system architecture and data flow diagrams.
* `*.sh` - Automation scripts for fast execution (`run_slam.sh`, `run_nav2.sh`, `send_ip.sh`).
* `*.onnx` / `*.pt` - Pre-trained YOLOv8 object detection model weights.

---

## 🛠️ Getting Started

### 1. Prerequisites & Dependencies
Ensure you have a machine running Linux with **ROS 2 Jazzy** installed. 

For the Computer Vision & Web modules, you will need to install the required Python packages manually based on your needs:
```bash
pip install ultralytics opencv-python flask numpy
