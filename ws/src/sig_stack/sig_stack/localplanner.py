import rclpy
import math
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from geometry_msgs.msg import PoseArray

class LocalPlanner(Node):
  def __init__(self):
    super().__init__('local_planner')
    self.publisher_ = self.create_publisher(PoseStamped, 'drive_to', 10)
    self.subscription_ = self.create_subscription(PoseStamped, 'pose', self.pose_callback,  10)
    self.global_planner_subscription_ = self.create_subscription(PoseArray, 'global_planner', self.global_planner_callback,  10)
    self.currentX = 0.0
    self.currentY = 0.0
    self.currentYaw = 0.0
    self.minRadius = 0.25
    self.maxRadius = 1.5
    self.maxAngle = math.pi / 4
    self.poses = []
    
    # subscribers = current pose, global planner line
    # publisher = future pose to pure pursuit
    
  def global_planner_callback(self, msg):
    self.poses = msg.poses

  def location_callback(self):
    poseList = []
    for pose in self.poses:
      r = pow(pose.position.x - self.currentX, 2) + pow(pose.position.y - self.currentY, 2)
      if r <= self.maxRadius and r >= self.minRadius:
        poseList.append(pose)
    
    waypoint = poseList[0]
    for pose in poseList:
      new_yaw = self.get_yaw(pose.orientation.w, pose.orientation.x, pose.orientation.y, pose.orientation.z)
      if abs(new_yaw - self.currentYaw) < self.maxAngle:
        waypoint = pose
        break
        
    msg = PoseStamped()
    msg.pose.position.x = waypoint.position.x
    msg.pose.position.y = waypoint.position.y
    msg.pose.position.z = 0.0
    msg.pose.orientation.w = waypoint.orientation.w
    msg.pose.orientation.x = waypoint.orientation.x
    msg.pose.orientation.y = waypoint.orientation.y
    msg.pose.orientation.z = waypoint.orientation.z
    
    self.publisher_.publish(msg)
    
  def pose_callback(self, msg):
    self.currentX = msg.pose.position.x
    self.currentY = msg.pose.position.y
    self.currentYaw = self.get_yaw(msg.pose.orientation.w, msg.pose.orientation.x, msg.pose.orientation.y, msg.pose.orientation.z)
    
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