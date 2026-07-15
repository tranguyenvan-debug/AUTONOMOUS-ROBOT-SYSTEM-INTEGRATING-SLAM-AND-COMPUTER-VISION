#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, TransformStamped
from nav_msgs.msg import Odometry
from tf2_ros import TransformBroadcaster
from std_msgs.msg import Bool
import serial
import json
import math
from rclpy.time import Time

class SerialBridge(Node):
    def __init__(self):
        super().__init__('serial_bridge')
        self.declare_parameter('port', '/dev/ttyESP32')
        self.declare_parameter('baud', 115200)
        port = self.get_parameter('port').value
        baud = self.get_parameter('baud').value
        try:
            self.ser = serial.Serial(port, baud, timeout=0.1)
            self.get_logger().info(f'Opened serial port: {port}')
        except Exception as e:
            self.get_logger().error(f'Cannot open serial: {e}')
            raise
        self.odom_pub = self.create_publisher(Odometry, '/odom', 10)
        self.tf_broadcaster = TransformBroadcaster(self)
        self.estop = False
        self.create_subscription(Bool, '/estop', lambda msg: setattr(self, 'estop', msg.data), 10)
        self.cmd_vel_sub = self.create_subscription(Twist, '/cmd_vel', self.cmd_vel_callback, 10)
        self.timer = self.create_timer(0.05, self.read_serial)
        self.get_logger().info('Serial Bridge node started!')

    def cmd_vel_callback(self, msg: Twist):
        if self.estop:
            try: self.ser.write(b'{"lx":0,"az":0}\n')
            except: pass
            return
        cmd = {'lx': round(msg.linear.x, 4), 'az': round(msg.angular.z, 4)}
        try:
            self.ser.write((json.dumps(cmd) + '\n').encode())
        except Exception as e:
            self.get_logger().warn(f'Serial write error: {e}')

    def read_serial(self):
        try:
            if self.ser.in_waiting == 0:
                return
            line = self.ser.readline().decode('utf-8', errors='ignore').strip()
            if not line:
                return
            data = json.loads(line)
            x   = float(data.get('x',   0.0))
            y   = float(data.get('y',   0.0))
            yaw = float(data.get('yaw', 0.0))
            vl  = float(data.get('vl',  0.0))
            va  = float(data.get('va',  0.0))
            now = self.get_clock().now().to_msg()
            odom = Odometry()
            odom.header.stamp    = now
            odom.header.frame_id = 'odom'
            odom.child_frame_id  = 'base_link'
            odom.pose.pose.position.x = x
            odom.pose.pose.position.y = y
            odom.pose.pose.position.z = 0.0
            odom.pose.pose.orientation.z = math.sin(yaw / 2.0)
            odom.pose.pose.orientation.w = math.cos(yaw / 2.0)
            odom.twist.twist.linear.x  = vl
            odom.twist.twist.angular.z = va
            odom.pose.covariance[0]  = 0.01
            odom.pose.covariance[7]  = 0.01
            odom.pose.covariance[35] = 0.01
            odom.twist.covariance[0]  = 0.01
            odom.twist.covariance[7]  = 0.01
            odom.twist.covariance[35] = 0.01
            self.odom_pub.publish(odom)
            tf = TransformStamped()
            tf.header.stamp    = now
            tf.header.frame_id = 'odom'
            tf.child_frame_id  = 'base_link'
            tf.transform.translation.x = x
            tf.transform.translation.y = y
            tf.transform.translation.z = 0.0
            tf.transform.rotation.z = math.sin(yaw / 2.0)
            tf.transform.rotation.w = math.cos(yaw / 2.0)
            self.tf_broadcaster.sendTransform(tf)
        except json.JSONDecodeError:
            pass
        except Exception as e:
            self.get_logger().warn(f'Serial read error: {e}')

    def destroy_node(self):
        if self.ser.is_open:
            self.ser.write(b'{"lx":0,"az":0}\n')
            self.ser.close()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = SerialBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
