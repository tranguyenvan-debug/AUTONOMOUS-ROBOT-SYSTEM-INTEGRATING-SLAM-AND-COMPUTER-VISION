# 🤖 Autonomous Robot System Integrating SLAM and Computer Vision

**Final Year Project (Đồ Án 2)** — Ho Chi Minh City University of Technology (HCMUT)

Bachelor of Engineering in Electronics and Telecommunications

**Student:** Nguyen Van Tra

**Supervisor:** Assoc. Prof. Dr. Ha Hoang Kha

**Year:** 2026

**Achievement:** 9/10

## 📋 Overview

An indoor autonomous mobile robot system built on **ROS2 Jazzy**, integrating:

- 🗺️ **SLAM** — Real-time 360° environment mapping via LiDAR
- 📍 **Localization** — Robot positioning on saved maps (AMCL)
- 🚗 **Navigation** — Autonomous waypoint navigation with obstacle avoidance (Nav2)
- 👁️ **Computer Vision** — Object detection and visual servoing (YOLOv8n)
- 🌐 **Web Dashboard** — Browser-based monitoring and control via WiFi

---

## 🖼️ Hardware Gallery

> 📸 **Add your hardware photos here** — upload images to the `docs/images/` folder and link them below.

| Component | Image | Purchase Link |
|---|---|---|
| Raspberry Pi 4 (4GB) | *(add photo)* | [Official Store](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/) |
| ESP32 DevKit v1 | *(add photo)* | [Shopee](https://shopee.vn) / [Amazon](https://amazon.com) |
| RPLidar A1M8 | *(add photo)* | [SLAMTEC Store](https://www.slamtec.com/en/Lidar/A1) |
| Raspberry Pi Camera V2 | *(add photo)* | [Official Store](https://www.raspberrypi.com/products/camera-module-v2/) |
| MPU6050 IMU | *(add photo)* | [Shopee](https://shopee.vn) |
| JGB37-520 Motor w/ Encoder | *(add photo)* | [Shopee](https://shopee.vn) |
| L298N Motor Driver | *(add photo)* | [Shopee](https://shopee.vn) |

> 💡 **Tip:** Replace `*(add photo)*` with `![name](docs/images/filename.jpg)` after uploading your photos.

---

## 🔧 Hardware Components

| Component | Model | Role |
|---|---|---|
| Embedded Computer | Raspberry Pi 4 (4GB RAM) | ROS2, SLAM, Nav2, AI processing |
| Microcontroller | ESP32 DevKit v1 | PID motor control, Odometry |
| LiDAR | RPLidar A1M8 | 360° environment scanning, 12m range |
| Camera | Raspberry Pi Camera V2 | Video stream, object detection |
| IMU | MPU6050 | Acceleration & angular velocity |
| Motors | JGB37-520 12V w/ Encoder | Differential drive |
| Motor Driver | L298N H-Bridge | DC motor control |
| Power | 12V LiPo Battery | Main power supply |

---

## 🔌 Pin Wiring Table

### ESP32 → L298N (Motor Driver)

| ESP32 Pin | L298N Pin | Description |
|---|---|---|
| GPIO 25 | IN1 | Left motor direction A |
| GPIO 26 | IN2 | Left motor direction B |
| GPIO 27 | IN3 | Right motor direction A |
| GPIO 14 | IN4 | Right motor direction B |
| GPIO 32 | ENA (PWM) | Left motor speed |
| GPIO 33 | ENB (PWM) | Right motor speed |
| GND | GND | Common ground |

### ESP32 → Encoder (JGB37-520)

| ESP32 Pin | Encoder Pin | Description |
|---|---|---|
| GPIO 18 | Left Encoder A | Left wheel channel A |
| GPIO 19 | Left Encoder B | Left wheel channel B |
| GPIO 22 | Right Encoder A | Right wheel channel A |
| GPIO 23 | Right Encoder B | Right wheel channel B |
| 3.3V | VCC | Encoder power |
| GND | GND | Common ground |

### Raspberry Pi 4 → MPU6050 (I2C)

| Raspberry Pi Pin | MPU6050 Pin | Description |
|---|---|---|
| Pin 1 (3.3V) | VCC | Power supply |
| Pin 6 (GND) | GND | Ground |
| Pin 3 (GPIO 2, SDA) | SDA | I2C data |
| Pin 5 (GPIO 3, SCL) | SCL | I2C clock |
| — | AD0 | Left floating → address 0x68 |

### Raspberry Pi 4 → Other Peripherals

| Raspberry Pi | Device | Interface |
|---|---|---|
| USB Port 1 | ESP32 | USB Serial (/dev/ttyESP32) |
| USB Port 2 | RPLidar A1M8 | USB Serial (/dev/ttyLIDAR) |
| CSI Camera Port | Pi Camera V2 | CSI Ribbon Cable |

---

## 💻 Software Stack

| Component | Technology |
|---|---|
| OS | Ubuntu 24.04 (Raspberry Pi) |
| Framework | ROS2 Jazzy |
| SLAM | SLAM Toolbox (Graph-based SLAM) |
| Localization | AMCL (Adaptive Monte Carlo) |
| Navigation | Nav2 Stack (MPPI + NavFn/A*) |
| Sensor Fusion | EKF (robot_localization) |
| AI Model | YOLOv8n ONNX (80 classes, COCO) |
| Web Frontend | HTML/JavaScript + roslibjs |
| Web Backend | Python HTTP Server |
| Notification | Telegram Bot API |

---

## 📁 Project Structure

```
robot_project/
├── robot_ws/src/robot_base/
│   ├── robot_base/
│   │   ├── serial_bridge.py        # ESP32 communication via Serial USB
│   │   ├── imu_publisher.py        # MPU6050 IMU reading via I2C
│   │   ├── camera_publisher.py     # Pi Camera V2 stream (OpenCV)
│   │   └── yolo_detector.py        # YOLOv8n detection + Visual Servoing
│   ├── launch/
│   │   ├── slam.launch.py          # Boot: start base nodes
│   │   ├── slam_only.launch.py     # SLAM Toolbox (mapping mode)
│   │   └── nav2_only.launch.py     # Nav2 Stack (navigation mode)
│   └── config/
│       ├── ekf.yaml                # Extended Kalman Filter config
│       ├── slam.yaml               # SLAM Toolbox parameters
│       └── nav2_params.yaml        # Nav2 config (AMCL, costmap, planner)
├── robot_web/
│   ├── backend.py                  # HTTP server (port 8080)
│   └── index.html                  # Web Dashboard
├── maps/                           # Saved maps (.pgm, .yaml, waypoints.json)
├── yolov8n.onnx                    # AI model (12.7MB)
├── run_slam.sh                     # SLAM startup script
├── run_nav2.sh                     # Nav2 startup script
├── send_ip.sh                      # Send IP via Telegram on boot
├── docs/images/                    # Hardware photos (add yours here)
└── /etc/
    ├── systemd/system/
    │   ├── robot-ros.service       # Auto-start ROS2 on boot
    │   └── robot-web.service       # Auto-start Web Dashboard on boot
    └── udev/rules.d/
        └── 99-robot.rules          # Fixed port symlinks for ESP32 & LiDAR
```

---

## ⬇️ Download

### Option 1 — Download from GitHub Releases (Recommended)

1. Go to the [**Releases**](../../releases) tab on GitHub
2. Download the latest `.zip` file (e.g. `robot-slam-v1.0.zip`)
3. Extract and follow the installation steps below

### Option 2 — Clone via Git

```bash
git clone https://github.com/nguyenvantra-debug/autonomous-robot-slam.git
cd autonomous-robot-slam
```

### Option 3 — Download ZIP directly

Click **Code → Download ZIP** at the top of this page.

---

## 🚀 Installation

### Requirements

- Raspberry Pi 4 (Ubuntu 24.04)
- ROS2 Jazzy
- Python 3.12+

### 1. Install ROS2 Jazzy

```bash
# Follow official guide
https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html
```

### 2. Install dependencies

```bash
sudo apt install -y \
  ros-jazzy-slam-toolbox \
  ros-jazzy-nav2-bringup \
  ros-jazzy-robot-localization \
  ros-jazzy-rosbridge-server \
  ros-jazzy-rplidar-ros \
  ros-jazzy-nav2-mppi-controller

pip install onnxruntime opencv-python smbus2 pyserial --break-system-packages
```

### 3. Clone and build

```bash
mkdir -p ~/robot_ws/src
cd ~/robot_ws/src
git clone https://github.com/nguyenvantra-debug/autonomous-robot-slam.git robot_base
cd ~/robot_ws
colcon build --packages-select robot_base
source install/setup.bash
```

### 4. Setup udev rules (fixed serial ports)

```bash
sudo cp etc/udev/rules.d/99-robot.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules && sudo udevadm trigger
# Verify: ls -la /dev/ttyESP32 /dev/ttyLIDAR
```

### 5. Install systemd services (auto-boot)

```bash
sudo cp etc/systemd/system/robot-ros.service /etc/systemd/system/
sudo cp etc/systemd/system/robot-web.service /etc/systemd/system/
sudo systemctl enable robot-ros.service robot-web.service
sudo systemctl start robot-ros.service robot-web.service
```

### 6. Configure Telegram Bot (receive IP on boot)

Edit `send_ip.sh`:
```bash
TOKEN="your_bot_token_here"
CHAT_ID="your_chat_id_here"
```

Get your token from [@BotFather](https://t.me/botfather) on Telegram.

---

## 📖 Usage

### Access Web Dashboard

```
http://<raspberry_pi_ip>:8080
```

> 💡 The robot sends its IP to your Telegram on every boot — no need to check manually.

### Operating Flow

```
1. Power on Pi → services auto-start → receive IP via Telegram
2. Open Web Dashboard in browser
3. Tab [Mapping]:
   - Click "Start SLAM"
   - Drive robot around the room using joystick
   - Click "Save Map" → enter name → "Stop SLAM"
4. Tab [Navigation]:
   - Click "Start Nav2" (wait ~30s for initialization)
   - Click "Set Initial Pose" (place robot at starting position)
   - Save waypoints → click any waypoint to start autonomous navigation
5. Tab [AI]:
   - Click "Start AI"
   - Camera shows real-time object detection
   - Click object name to activate visual servoing (robot follows target)
```

---

## 🌐 Web Dashboard

| Tab | Features |
|---|---|
| **Mapping** | Real-time SLAM map, joystick control, emergency stop, save map |
| **Navigation** | Autonomous waypoint navigation, robot position on map, camera feed |
| **AI** | Live camera, YOLOv8n detection overlay, visual servoing target selection |
| **History** | Trip log, obstacle count, distance traveled, system stats |

### Backend API Endpoints

| Endpoint | Description |
|---|---|
| `GET /slam/start` | Start SLAM mapping |
| `GET /slam/stop` | Stop SLAM |
| `GET /nav2/start` | Start Nav2 (loads latest map) |
| `GET /nav2/stop` | Stop Nav2 |
| `GET /map/save?name=X` | Save current map |
| `GET /waypoint/save` | Save current position as waypoint |
| `GET /waypoint/list` | List all waypoints for current map |
| `GET /waypoint/delete` | Delete a waypoint |
| `GET /ai/start` | Start YOLO detector |
| `GET /ai/stop` | Stop YOLO detector |
| `GET /set_initial_pose` | Publish initial pose to AMCL |
| `GET /sysinfo` | CPU / RAM / Disk / WiFi stats |
| `GET /status` | SLAM / Nav2 running status |

---

## 📊 Technical Specifications

### AI Model — YOLOv8n

| Parameter | Value |
|---|---|
| Model | YOLOv8n (Nano) |
| Format | ONNX Runtime |
| Number of classes | 80 (COCO dataset) |
| Model size | 12.7 MB |
| mAP50 (COCO) | 37.3% |
| mAP50-95 (COCO) | 52.9% |
| FPS on Raspberry Pi 4 | ~0.3–0.5 FPS |
| Confidence threshold | 0.4 |
| IoU threshold (NMS) | 0.45 |

### Navigation — Nav2

| Parameter | Value |
|---|---|
| Global Planner | NavFn (A*) |
| Local Planner | MPPI Controller |
| Robot radius | 0.15 m |
| Inflation radius | 0.2 m |
| Max linear velocity | 0.2 m/s |
| Goal tolerance | 0.5 m |
| Map resolution | 0.02 m/pixel |

### LiDAR — RPLidar A1M8

| Parameter | Value |
|---|---|
| Range | 0.15 — 12 m |
| Scan frequency | ~5.5 Hz (360°/revolution) |
| Points per scan | ~1,450 points |
| Interface | USB Serial |

---

## 🐛 Debugging

```bash
# Check running nodes
ros2 node list

# Check SLAM status
ros2 lifecycle get /slam_toolbox

# Check AMCL pose
ros2 topic echo /amcl_pose --once

# Check LiDAR data rate
ros2 topic hz /scan

# View service logs
sudo journalctl -u robot-ros.service -f
sudo journalctl -u robot-web.service -f

# Restart all services
sudo systemctl restart robot-ros.service robot-web.service

# Fix port conflict (rosbridge)
sudo fuser -k 9090/tcp

# Check CPU load
top -bn1 | head -5
```

---

## 📚 References

- [ROS2 Jazzy Documentation](https://docs.ros.org/en/jazzy/)
- [Nav2 Documentation](https://docs.nav2.org/)
- [SLAM Toolbox](https://slam-toolbox.readthedocs.io/)
- [YOLOv8 — Ultralytics](https://docs.ultralytics.com/models/yolov8/)
- [ONNX Runtime](https://onnxruntime.ai/docs/)
- [Probabilistic Robotics — Thrun, Burgard, Fox](http://www.probabilistic-robotics.org/)
- [Telegram Bot API](https://core.telegram.org/bots/api)

---

## 📄 License

MIT License — Free to use for educational and research purposes.

---

## ⭐ Support This Project

If this project helped you or inspired your own robot build, please consider giving it a **star** ⭐ on GitHub — it means a lot and helps others discover this project!

[![GitHub stars](https://img.shields.io/github/stars/nguyenvantra-debug/autonomous-robot-slam?style=social)](https://github.com/nguyenvantra-debug/autonomous-robot-slam/stargazers)

---

<div align="center">

**Made with ❤️ by [nguyenvantra-debug](https://github.com/nguyenvantra-debug) (Văn Trà)**

*Ho Chi Minh City University of Technology (HCMUT) | Faculty of Electrical & Electronics Engineering | 2026*

</div>
