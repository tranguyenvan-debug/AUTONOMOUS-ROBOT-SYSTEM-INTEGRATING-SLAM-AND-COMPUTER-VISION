# 🤖 Hệ Thống Robot Tự Hành Tích Hợp SLAM và Thị Giác Máy Tính

> **Đồ Án 2** — Trường Đại học Bách Khoa TP.HCM, Khoa Điện - Điện Tử  
> **Sinh viên:** Nguyễn Văn Trà — MSSV: 2112472  
> **GVHD:** PGS. TS. Hà Hoàng Kha  
> **Năm:** 2026

---

## 📋 Giới thiệu

Hệ thống robot di động tự hành phục vụ môi trường trong nhà, xây dựng trên nền tảng **ROS2 Jazzy**. Tích hợp hoàn chỉnh các chức năng:

- 🗺️ **SLAM** — Tự động lập bản đồ môi trường 360° bằng LiDAR
- 📍 **Localization** — Định vị robot trên bản đồ đã lưu (AMCL)
- 🚗 **Navigation** — Tự hành đến waypoint, tránh vật cản (Nav2)
- 👁️ **Computer Vision** — Nhận diện và bám theo vật thể (YOLOv8n)
- 🌐 **Web Dashboard** — Điều khiển và giám sát qua trình duyệt

---

## 🔧 Phần cứng

| Thành phần | Model | Vai trò |
|---|---|---|
| Máy tính nhúng | Raspberry Pi 4 (4GB RAM) | Xử lý ROS2, SLAM, Nav2, AI |
| Vi điều khiển | ESP32 | Điều khiển động cơ PID, Odometry |
| LiDAR | RPLidar A1M8 | Quét môi trường 360°, 12m |
| Camera | Raspberry Pi Camera V2 | Stream video, nhận diện vật thể |
| IMU | MPU6050 | Đo gia tốc và vận tốc góc |
| Động cơ | JGB37-520 12V Encoder | Truyền động vi sai |
| Driver | L298N H-Bridge | Điều khiển động cơ DC |

---

## 💻 Phần mềm

| Thành phần | Công nghệ |
|---|---|
| OS | Ubuntu 24.04 (Raspberry Pi) |
| Framework | ROS2 Jazzy |
| SLAM | SLAM Toolbox (Graph-based SLAM) |
| Localization | AMCL (Adaptive Monte Carlo) |
| Navigation | Nav2 Stack (MPPI + NavFn/A*) |
| Sensor Fusion | EKF (robot_localization) |
| AI Model | YOLOv8n ONNX (80 classes, COCO) |
| Web | HTML/JavaScript + roslibjs |
| Backend | Python HTTP Server |

---

## 📁 Cấu trúc dự án

```
robot_project/
├── robot_ws/src/robot_base/
│   ├── robot_base/
│   │   ├── serial_bridge.py        # Giao tiếp ESP32 qua Serial USB
│   │   ├── imu_publisher.py        # Đọc IMU MPU6050 qua I2C
│   │   ├── camera_publisher.py     # Stream camera Pi V2 (OpenCV)
│   │   └── yolo_detector.py        # Nhận diện YOLOv8n + Visual Servoing
│   ├── launch/
│   │   ├── slam.launch.py          # Khởi động nodes cơ bản khi boot
│   │   ├── slam_only.launch.py     # SLAM Toolbox (mapping mode)
│   │   └── nav2_only.launch.py     # Nav2 Stack (navigation mode)
│   └── config/
│       ├── ekf.yaml                # Cấu hình Extended Kalman Filter
│       ├── slam.yaml               # Cấu hình SLAM Toolbox
│       └── nav2_params.yaml        # Cấu hình Nav2 (AMCL, costmap, planner)
├── robot_web/
│   ├── backend.py                  # HTTP server (port 8080)
│   └── index.html                  # Web Dashboard
├── maps/                           # Bản đồ đã lưu (.pgm, .yaml, waypoints.json)
├── yolov8n.onnx                    # AI model (12.7MB)
├── run_slam.sh                     # Script khởi động SLAM
├── run_nav2.sh                     # Script khởi động Nav2
├── send_ip.sh                      # Gửi IP qua Telegram khi boot
└── /etc/
    ├── systemd/system/
    │   ├── robot-ros.service       # Auto-start ROS2 khi boot
    │   └── robot-web.service       # Auto-start Web Dashboard khi boot
    └── udev/rules.d/
        └── 99-robot.rules          # Cố định port ESP32 và LiDAR
```

---

## 🚀 Cài đặt

### Yêu cầu

- Raspberry Pi 4 (Ubuntu 24.04)
- ROS2 Jazzy
- Python 3.12+

### 1. Cài đặt ROS2 Jazzy

```bash
# Theo hướng dẫn chính thức
https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html
```

### 2. Cài đặt dependencies

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

### 3. Clone và build

```bash
mkdir -p ~/robot_ws/src
cd ~/robot_ws/src
git clone <repo-url> robot_base
cd ~/robot_ws
colcon build --packages-select robot_base
source install/setup.bash
```

### 4. Cấu hình udev rules (cố định port)

```bash
sudo cp etc/udev/rules.d/99-robot.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules && sudo udevadm trigger
```

### 5. Cài đặt systemd services (auto-boot)

```bash
sudo cp etc/systemd/system/robot-ros.service /etc/systemd/system/
sudo cp etc/systemd/system/robot-web.service /etc/systemd/system/
sudo systemctl enable robot-ros.service robot-web.service
sudo systemctl start robot-ros.service robot-web.service
```

### 6. Cấu hình Telegram Bot (nhận IP khi boot)

Chỉnh sửa `send_ip.sh`:
```bash
TOKEN="your_bot_token"
CHAT_ID="your_chat_id"
```

---

## 📖 Hướng dẫn sử dụng

### Truy cập Web Dashboard

```
http://<IP_raspberry_pi>:8080
```

### Flow hoạt động

```
1. Boot Pi → services tự khởi động → nhận IP qua Telegram
2. Mở Web Dashboard trên browser
3. Tab Mapping:
   - Bấm "Bắt đầu SLAM"
   - Lái robot vẽ bản đồ bằng joystick
   - Bấm "Lưu Map" → đặt tên → "Dừng SLAM"
4. Tab Navigation:
   - Bấm "Bắt đầu Nav2" (đợi ~30s)
   - Bấm "Set vị trí ban đầu"
   - Lưu waypoint → Bấm waypoint để robot tự hành
5. Tab AI:
   - Bấm "Bắt đầu AI"
   - Camera hiện nhận diện vật thể
   - Bấm tên vật thể để robot bám theo
```

---

## 🌐 Web Dashboard

| Tab | Chức năng |
|---|---|
| **Mapping** | Vẽ bản đồ SLAM realtime, joystick điều khiển, lưu map |
| **Navigation** | Tự hành đến waypoint, hiển thị vị trí robot trên map |
| **AI** | Camera realtime, nhận diện vật thể, visual servoing |
| **Lịch sử** | Theo dõi các chuyến đi, thống kê hệ thống |

### Backend API Endpoints

| Endpoint | Chức năng |
|---|---|
| `GET /slam/start` | Khởi động SLAM |
| `GET /slam/stop` | Dừng SLAM |
| `GET /nav2/start` | Khởi động Nav2 (load map mới nhất) |
| `GET /nav2/stop` | Dừng Nav2 |
| `GET /map/save?name=X` | Lưu bản đồ |
| `GET /waypoint/save` | Lưu waypoint |
| `GET /waypoint/list` | Danh sách waypoints |
| `GET /waypoint/delete` | Xóa waypoint |
| `GET /ai/start` | Khởi động YOLO detector |
| `GET /ai/stop` | Dừng YOLO detector |
| `GET /set_initial_pose` | Set vị trí ban đầu cho AMCL |
| `GET /sysinfo` | Thông tin CPU/RAM/Disk/WiFi |
| `GET /status` | Trạng thái SLAM/Nav2 |

---

## 📊 Thông số kỹ thuật

### AI Model — YOLOv8n

| Thông số | Giá trị |
|---|---|
| Model | YOLOv8n (Nano) |
| Format | ONNX Runtime |
| Số class | 80 (COCO dataset) |
| Kích thước model | 12.7 MB |
| mAP50 (COCO) | 37.3% |
| mAP50-95 (COCO) | 52.9% |
| FPS trên Pi 4 | ~0.3-0.5 FPS |
| Confidence threshold | 0.4 |
| IoU threshold (NMS) | 0.45 |

### Navigation — Nav2

| Thông số | Giá trị |
|---|---|
| Global Planner | NavFn (A*) |
| Local Planner | MPPI Controller |
| Robot radius | 0.15 m |
| Inflation radius | 0.2 m |
| Max velocity | 0.2 m/s |
| Goal tolerance | 0.5 m |
| Map resolution | 0.02 m/pixel |

### LiDAR — RPLidar A1M8

| Thông số | Giá trị |
|---|---|
| Tầm đo | 0.15 — 12 m |
| Tốc độ quét | ~5.5 Hz (360°/vòng) |
| Số điểm/vòng | ~1450 điểm |
| Giao tiếp | Serial USB |

---

## 🔌 Kết nối phần cứng

```
Raspberry Pi 4
├── USB → ESP32 (/dev/ttyESP32)
├── USB → RPLidar A1M8 (/dev/ttyLIDAR)
├── CSI → Pi Camera V2
└── I2C (GPIO 2,3) → MPU6050

ESP32
├── GPIO → L298N (PWM motor control)
├── GPIO → Encoder JGB37-520 (Left)
└── GPIO → Encoder JGB37-520 (Right)
```

---

## 🐛 Debug

```bash
# Kiểm tra nodes đang chạy
ros2 node list

# Kiểm tra SLAM status
ros2 lifecycle get /slam_toolbox

# Kiểm tra AMCL pose
ros2 topic echo /amcl_pose --once

# Kiểm tra LiDAR data
ros2 topic hz /scan

# Kiểm tra logs
sudo journalctl -u robot-ros.service -f
sudo journalctl -u robot-web.service -f

# Restart services
sudo systemctl restart robot-ros.service robot-web.service

# Kill port conflict
sudo fuser -k 9090/tcp
```

---

## 📚 Tài liệu tham khảo

- [ROS2 Jazzy Documentation](https://docs.ros.org/en/jazzy/)
- [Nav2 Documentation](https://docs.nav2.org/)
- [SLAM Toolbox](https://slam-toolbox.readthedocs.io/)
- [YOLOv8 — Ultralytics](https://docs.ultralytics.com/models/yolov8/)
- [ONNX Runtime](https://onnxruntime.ai/docs/)
- [Probabilistic Robotics — Thrun, Burgard, Fox](http://www.probabilistic-robotics.org/)

---

## 📄 License

MIT License — Free to use for educational purposes.

---

> **Trường Đại học Bách Khoa TP.HCM** | Khoa Điện - Điện Tử | 2026
