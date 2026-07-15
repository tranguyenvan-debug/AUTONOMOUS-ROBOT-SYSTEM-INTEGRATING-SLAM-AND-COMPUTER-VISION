from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess, TimerAction

def generate_launch_description():
    nav2_params = '/home/vantra/robot_ws/src/robot_base/config/nav2_params.yaml'
    map_file = '/home/vantra/maps/my_map.yaml'

    return LaunchDescription([
        Node(package='robot_base', executable='serial_bridge', name='serial_bridge', output='screen'),
        Node(package='robot_base', executable='imu_publisher', name='imu_publisher', output='screen'),
        ExecuteProcess(cmd=['ros2', 'launch', 'rplidar_ros', 'rplidar.launch.py'], output='screen'),
        Node(package='tf2_ros', executable='static_transform_publisher',
             arguments=['0','0','0','0','0','0','base_link','laser']),
        Node(package='tf2_ros', executable='static_transform_publisher',
             arguments=['0','0','0','0','0','0','base_link','imu_link']),
        Node(package='robot_localization', executable='ekf_node', name='ekf_filter_node',
             output='screen', parameters=['/home/vantra/robot_ws/src/robot_base/config/ekf.yaml']),
        Node(package='rosbridge_server', executable='rosbridge_websocket',
             name='rosbridge_websocket', output='screen',
             parameters=[{'port': 9090}]),
        TimerAction(period=15.0, actions=[
            Node(package='nav2_map_server', executable='map_server', name='map_server',
                 output='screen', parameters=[{'use_sim_time': False, 'yaml_filename': map_file}]),
            Node(package='nav2_amcl', executable='amcl', name='amcl',
                 output='screen', parameters=[nav2_params]),
            Node(package='nav2_controller', executable='controller_server', name='controller_server',
                 output='screen', parameters=[nav2_params]),
            Node(package='nav2_planner', executable='planner_server', name='planner_server',
                 output='screen', parameters=[nav2_params]),
            Node(package='nav2_behaviors', executable='behavior_server', name='behavior_server',
                 output='screen', parameters=[nav2_params]),
            Node(package='nav2_bt_navigator', executable='bt_navigator', name='bt_navigator',
                 output='screen', parameters=[nav2_params]),
            Node(package='nav2_lifecycle_manager', executable='lifecycle_manager',
                 name='lifecycle_manager_navigation', output='screen',
                 parameters=[{'use_sim_time': False, 'autostart': True,
                               'node_names': ['map_server', 'amcl', 'controller_server',
                                              'planner_server', 'behavior_server', 'bt_navigator']}]),
        ]),
    ])
