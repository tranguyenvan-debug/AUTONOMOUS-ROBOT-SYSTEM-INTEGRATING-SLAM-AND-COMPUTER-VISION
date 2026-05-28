import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage
import cv2
import time

class CameraPublisher(Node):
    def __init__(self):
        super().__init__('camera_publisher')
        self.pub = self.create_publisher(CompressedImage, '/image_raw/compressed', 10)
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        time.sleep(2)
        self.timer = self.create_timer(0.1, self.publish_frame)
        self.get_logger().info('Camera publisher started')

    def publish_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return
        _, buf = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
        msg = CompressedImage()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.format = 'jpeg'
        msg.data = buf.tobytes()
        self.pub.publish(msg)

def main():
    rclpy.init()
    node = CameraPublisher()
    rclpy.spin(node)
    node.cap.release()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
