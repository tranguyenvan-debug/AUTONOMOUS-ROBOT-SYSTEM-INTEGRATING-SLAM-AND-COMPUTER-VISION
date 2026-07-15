from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import TimerAction

def generate_launch_description():
    nav2_params = '/home/vantra/robot_ws/src/robot_base/config/nav2_params.yaml'

    return LaunchDescription([
        TimerAction(
            period=5.0,
            actions=[
                Node(
                    package='nav2_controller',
                    executable='controller_server',
                    name='controller_server',
                    output='screen',
                    parameters=[nav2_params]
                ),
                Node(
                    package='nav2_planner',
                    executable='planner_server',
                    name='planner_server',
                    output='screen',
                    parameters=[nav2_params]
                ),
                Node(
                    package='nav2_behaviors',
                    executable='behavior_server',
                    name='behavior_server',
                    output='screen',
                    parameters=[nav2_params]
                ),
                Node(
                    package='nav2_bt_navigator',
                    executable='bt_navigator',
                    name='bt_navigator',
                    output='screen',
                    parameters=[nav2_params]
                ),
                Node(
                    package='nav2_lifecycle_manager',
                    executable='lifecycle_manager',
                    name='lifecycle_manager_navigation',
                    output='screen',
                    parameters=[{
                        'use_sim_time': False,
                        'autostart': True,
                        'node_names': [
                            'controller_server',
                            'planner_server',
                            'behavior_server',
                            'bt_navigator'
                        ]
                    }]
                ),
            ]
        ),
        TimerAction(
            period=30.0,
            actions=[
                Node(
                    package='explore_lite',
                    executable='explore',
                    name='explore_costmap',
                    output='screen',
                    parameters=[{
                        'use_sim_time': False,
                        'robot_base_frame': 'base_link',
                        'costmap_topic': '/global_costmap/costmap',
                        'costmap_updates_topic': '/global_costmap/costmap_updates',
                        'visualize': True,
                        'planner_frequency': 0.33,
                        'progress_timeout': 30.0,
                        'potential_scale': 3.0,
                        'gain_scale': 1.0,
                        'transform_tolerance': 0.5,
                        'min_frontier_size': 0.1,
                    }]
                ),
            ]
        ),
    ])
