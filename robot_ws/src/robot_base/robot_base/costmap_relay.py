import rclpy
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid

class CostmapRelay(Node):
    def __init__(self):
        super().__init__('costmap_relay')
        self.pub1 = self.create_publisher(OccupancyGrid, '/explore_costmap/costmap', 10)
        self.pub2 = self.create_publisher(OccupancyGrid, '/costmap', 10)
        self.sub = self.create_subscription(OccupancyGrid, '/global_costmap/costmap', self.cb, 10)
        self.get_logger().info('Costmap relay started')

    def cb(self, msg):
        self.pub1.publish(msg)
        self.pub2.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    rclpy.spin(CostmapRelay())
    rclpy.shutdown()

if __name__ == '__main__':
    main()
