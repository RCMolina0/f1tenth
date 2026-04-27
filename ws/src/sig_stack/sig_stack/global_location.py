import rclpy
from rclpy.node import Node
from tf2_ros import Buffer, TransformListener
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
import math

class GlobalLocationNode(Node):
    def __init__(self):
        super().__init__('global_location_node')
        
        # 1. FRAME TOPIC: TF2 listener for Global Coordinates (map -> base_link)
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        
        # 2. LIDAR TOPIC: Subscriber for LaserScan
        self.lidar_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.lidar_callback,
            10)
            
        # 3. ODOMETRY TOPIC: Subscriber for Speed and Local Pose
        self.odom_sub = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10)

        # Timer to print the dashboard every 0.5 seconds
        self.timer = self.create_timer(0.5, self.status_report)
        
        # Variables to store the latest sensor data
        self.latest_scan_dist = 0.0
        self.latest_speed = 0.0

    def lidar_callback(self, msg):
        # Extract the distance of the laser beam pointing directly in front of the car
        middle_index = len(msg.ranges) // 2
        self.latest_scan_dist = msg.ranges[middle_index]

    def odom_callback(self, msg):
        # Extract the current linear velocity (speed)
        self.latest_speed = msg.twist.twist.linear.x

    def status_report(self):
        try:
            # Lookup the Coordinate Frame (Where is the car on the map?)
            trans = self.tf_buffer.lookup_transform('map', 'base_link', rclpy.time.Time())
            x = trans.transform.translation.x
            y = trans.transform.translation.y
            
            # Convert Quaternion rotation to standard Yaw (heading)
            q = trans.transform.rotation
            siny_cosp = 2 * (q.w * q.z + q.x * q.y)
            cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
            yaw = math.atan2(siny_cosp, cosy_cosp)
            
            # Print the dashboard
            self.get_logger().info(
                f"\n--- PERCEPTION TEAM DASHBOARD ---\n"
                f"Location (Map Frame) : X: {x:.2f} m, Y: {y:.2f} m, Yaw: {yaw:.2f} rad\n"
                f"Speed (Odom Topic)   : {self.latest_speed:.2f} m/s\n"
                f"Front Wall (LIDAR)   : {self.latest_scan_dist:.2f} m"
            )
        except Exception:
            self.get_logger().info("Waiting for full system startup (LIDAR, Odom, and Map)...")

def main(args=None):
    rclpy.init(args=args)
    node = GlobalLocationNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()