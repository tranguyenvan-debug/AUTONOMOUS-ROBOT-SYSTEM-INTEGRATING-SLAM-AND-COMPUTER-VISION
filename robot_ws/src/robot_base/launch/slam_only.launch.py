from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess, TimerAction

def generate_launch_description():
    return LaunchDescription([
        Node(package='slam_toolbox', executable='async_slam_toolbox_node',
            name='slam_toolbox', output='screen',
            parameters=['/home/vantra/robot_ws/src/robot_base/config/slam.yaml']),
        TimerAction(period=20.0, actions=[
            ExecuteProcess(cmd=['ros2', 'lifecycle', 'set', '/slam_toolbox', 'configure'], output='screen'),
        ]),
        TimerAction(period=25.0, actions=[
            ExecuteProcess(cmd=['ros2', 'lifecycle', 'set', '/slam_toolbox', 'activate'], output='screen'),
        ]),
    ])
