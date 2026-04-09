import rclpy
import math
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped

class LocalPlanner(Node):
  def __init__(self):
    super().__init__('local_planner')
    self.publisher_ = self.create_publisher(PoseStamped, 'drive_to', 10)
    self.subscription_ = self.create_subscription(PoseStamped, 'pose', self.pose_callback,  10)
    self.currentX = 0.0
    self.currentY = 0.0
    self.currentYaw = 0.0
    
    # subscribers = current pose, global planner line
    # publisher = future pose to pure pursuit

  def location_callback(self):
    msg = PoseStamped()
    msg.pose.position.x = 0.0
    msg.pose.position.y = 0.0
    msg.pose.position.z = 0.0
    self.publisher_.publish(msg)
    
  def pose_callback(self, msg):
    currentX = msg.pose.position.x
    currentY = msg.pose.position.y
    currentYaw = self.get_yaw(msg.pose.orientation.w, msg.pose.orientation.x, msg.pose.orientation.y, msg.pose.orientation.z)
    self.get_logger().info(msg.pose.position.x)
    
  def get_yaw(self, w, x, y, z):
    return math.atan2(2 * (w * x + y * z), 1 - 2 * (pow(x, 2) + pow(y, 2)))
  
def main(args=None):
  rclpy.init(args=args)
  local_planner = LocalPlanner()
  rclpy.spin(local_planner)
  local_planner.destroy_node()
  rclpy.shutdown()

if __name__ == '__main__':
  main()