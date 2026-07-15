from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess

def generate_launch_description():
    return LaunchDescription([
        Node(package='robot_base', executable='serial_bridge', name='serial_bridge', output='screen'),
        Node(package='robot_base', executable='imu_publisher', name='imu_publisher', output='screen'),
        Node(package='robot_base', executable='camera_publisher', name='camera_publisher', output='screen'),
        ExecuteProcess(cmd=['ros2', 'launch', 'rplidar_ros', 'rplidar.launch.py', 'serial_port:=/dev/ttyLIDAR'], output='screen'),
        Node(package='tf2_ros', executable='static_transform_publisher',
            arguments=['0','0','0','0','0','0','base_link','laser']),
        Node(package='tf2_ros', executable='static_transform_publisher',
            arguments=['0','0','0','0','0','0','base_link','imu_link']),
        Node(package='robot_localization', executable='ekf_node', name='ekf_filter_node',
            output='screen', parameters=['/home/vantra/robot_ws/src/robot_base/config/ekf.yaml']),
        Node(package='rosbridge_server', executable='rosbridge_websocket',
            name='rosbridge_websocket', output='screen',
            parameters=[{'port': 9090}]),
    ])
