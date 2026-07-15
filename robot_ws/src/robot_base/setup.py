from setuptools import setup, find_packages

package_name = 'robot_base'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', [
                                               'launch/slam.launch.py',
                                               'launch/nav2.launch.py',
                                               'launch/explore.launch.py',
                                               'launch/nav2_only.launch.py',
                                               'launch/slam_only.launch.py'
                                               ]),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    entry_points={
        'console_scripts': [
            'camera_publisher = robot_base.camera_publisher:main',
            'yolo_detector = robot_base.yolo_detector:main',
            'serial_bridge = robot_base.serial_bridge:main',
            'imu_publisher = robot_base.imu_publisher:main',
            'costmap_relay = robot_base.costmap_relay:main',
        ],
    },
)
