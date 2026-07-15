import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from mpu6050 import mpu6050
import math
import smbus
import time

class ImuPublisher(Node):
    def __init__(self):
        super().__init__('imu_publisher')
        self.publisher = self.create_publisher(Imu, '/imu/data', 10)
        self.sensor = mpu6050(0x68)
        # Wake up sensor
        self._bus = smbus.SMBus(1)
        self._bus.write_byte_data(0x68, 0x6B, 0x00)

        time.sleep(0.5)

        self.timer = self.create_timer(0.05, self.publish_imu)  # 20Hz
        self.get_logger().info('IMU Publisher started')

    def publish_imu(self):
        try:
            msg = Imu()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.header.frame_id = 'imu_link'

            accel = self.sensor.get_accel_data()
            gyro = self.sensor.get_gyro_data()

            msg.linear_acceleration.x = accel['x']
            msg.linear_acceleration.y = accel['y']
            msg.linear_acceleration.z = accel['z']

            msg.angular_velocity.x = math.radians(gyro['x'])
            msg.angular_velocity.y = math.radians(gyro['y'])
            msg.angular_velocity.z = math.radians(gyro['z'])

            msg.linear_acceleration_covariance[0] = 0.01
            msg.linear_acceleration_covariance[4] = 0.01
            msg.linear_acceleration_covariance[8] = 0.01
            msg.angular_velocity_covariance[0] = 0.001
            msg.angular_velocity_covariance[4] = 0.001
            msg.angular_velocity_covariance[8] = 0.001
            msg.orientation_covariance[0] = -1

            self.publisher.publish(msg)

        except Exception as e:
            self.get_logger().warn(f'IMU read error: {e}', throttle_duration_sec=5.0)

def main(args=None):
    rclpy.init(args=args)
    node = ImuPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
