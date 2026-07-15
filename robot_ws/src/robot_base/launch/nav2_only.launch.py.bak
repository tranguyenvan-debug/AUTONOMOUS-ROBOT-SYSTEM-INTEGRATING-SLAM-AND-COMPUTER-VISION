from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import TimerAction, DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
import glob
import os

def generate_launch_description():
    nav2_params = '/home/vantra/robot_ws/src/robot_base/config/nav2_params.yaml'
    map_file = LaunchConfiguration('map_file')
    return LaunchDescription([
        DeclareLaunchArgument('map_file', default_value='/home/vantra/maps/map_1.yaml'),
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
        TimerAction(period=5.0, actions=[
            Node(package='nav2_lifecycle_manager', executable='lifecycle_manager',
                 name='lifecycle_manager_navigation', output='screen',
                 parameters=[{'use_sim_time': False, 'autostart': True,
                               'node_names': ['map_server', 'amcl', 'controller_server',
                                              'planner_server', 'behavior_server', 'bt_navigator']}]),
        ]),
    ])
