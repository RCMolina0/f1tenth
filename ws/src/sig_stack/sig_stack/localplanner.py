import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from sig_stack_msgs.msg import WayPoint, GlobalLine  
import math
import copy

# NOTE: We are using a new data strucuture I created called a WayPoint. 
# NOTE: A WayPoint has .x (x pos) .y (y pos) .o (yaw orientation i.e. where are we facing) and .v (current velcity)
# NOTE: The GlobalLine is a list of waypoints. They are at each x time interval. x needs to be tuned. This means more dense when slower, less dense when faster

class LocalPlanner(Node):
  def __init__(self):
    super().__init__('local_planner')
    self.publisher_ = self.create_publisher(WayPoint, 'drive_to', 10)
    self.position_subscription = self.create_subscription(Odometry, 'odom', self.odom_callback,  10)
    self.global_line_subscription = self.create_subscription(GlobalLine, 'global_line', self.global_line_callback, 10)
    # position_subscription = current pose
    # global_line_subscription = global planner line. This should almost never fire except once at the beging of our race.
    # publisher = future pose to pure pursuit
    self.curr_pos = None
    self.orientation = None
    self.velocity = None
    self.global_line = None
    self.recent_idx = 0
    self.dest = None

  def global_line_callback(self, msg):
    self.global_line = msg

  # triggers all real functionality- main implentation function
  def odom_callback(self, msg):
    self.curr_pos = msg.pose.pose.position
    # roll, pitch, yaw = euler_from_quaternion([
    #     self.orientation.x,
    #     self.orientation.y,
    #     self.orientation.z,
    #     self.orientation.w                                                                                                                                      
    # ])
    # face_to_waypoint = math.atan2(                                                                                                                             
    #     waypoint.y - self.curr_pos.y,                                                                                                                           
    #     waypoint.x - self.curr_pos.x 
    # ) 
    self.orientation = msg.pose.pose.orientation
    self.velocity = msg.twist.twist.linear.x

    # we have no sense of direction to go. Maybe could implmement wall following here - but I dont think we should
    if (self.global_line == None):
      self.get_logger().error('No global line exists')
      return
    
    #if we can still follow the previous steps?
    # NOTE: This will follow ay preovisly calcuated waypoints
    if (self.dest):
      next_point = self.dest.pop(0)
      self.publisher_.publish(next_point)
      return
    
    # should find the most current pos of the global race line- 'our on track equiv'
    # NOTE: we can change this function to get a different 'start' line for searhcing the global race line
    self.recent_idx = self.closestEclideanPointGL()

    #find our next waypoint- if the waypoints in the global raceline have varible density by time realtive to the car 
    # i.e. a tight corner would ahve more turns and a long striaght would have less
    # This is the number of waypoints from the global line that will be skipped an opimtined for the next
    #i.e. the gobal_line step length
    # NOTE:SKIP_NUMBER needs to be tuned
    SKIP_NUMBER = 5
    # NOTE: findNextWayPoint makes a linear line between our current pos and SKIP_NUMBER.
    # NOTE: This line moves short and longer when teh global race line moves faster and slower, i.e. arounf turns and trhough striaghts
    self.dest = self.findNextWayPoint(SKIP_NUMBER)
    # NOTE: This is a list of the nest SKIP_NUMBER of waypoints
    if (self.dest):
      next_point = self.dest.pop(0)
      self.publisher_.publish(next_point)
      return




  def findNextWayPoint(self, SKIP_NUMBER):
    # code to find waypoint we want to go to
    goal = self.global_line.waypoints[(self.recent_idx + SKIP_NUMBER) % len(self.global_line.waypoints)]
    # total_distance = math.sqrt((goal.pose.position.x - self.curr_pos.x)**2 + (goal.pose.position.y - self.curr_pos.y)**2)
    dest_points = []
    change_in_v = (goal.v - self.velocity) / SKIP_NUMBER
    change_in_x = (goal.x - self.curr_pos.x) / SKIP_NUMBER
    change_in_y = (goal.y - self.curr_pos.y) / SKIP_NUMBER
    new_orientation = math.atan2(goal.y - self.curr_pos.y, goal.x - self.curr_pos.x) 
    for i in range(SKIP_NUMBER):
      if (i == 0):
        new_point = WayPoint()
        new_point.x = self.curr_pos.x
        new_point.y = self.curr_pos.y
        new_point.v = self.velocity
      else:
        new_point = copy.deepcopy(dest_points[i - 1])
      new_point.v += change_in_v
      new_point.x += change_in_x
      new_point.y += change_in_y
      new_point.o = new_orientation
      dest_points.append(new_point)
    return dest_points

  # returns the index of the global reacing line coordinates for the closest point on the global racing line
  def closestEclideanPointGL(self):
    # distance = sqrt((global_x - x)^2 + (global_y - y)^2)
    min_dist = None
    break_count = 0
    idx = 0
    for i in range(self.recent_idx, len(self.global_line.waypoints)):
      distance = math.sqrt((self.global_line.waypoints[i].x - self.curr_pos.x)**2 + (self.global_line.waypoints[i].y - self.curr_pos.y)**2)
      if (min_dist == None or min_dist >= distance):
        min_dist = distance
        break_count = 0
        idx = i
      if (min_dist < distance):
        break_count += 1
      if (break_count == 3):
        return idx
    return idx
    
def main(args=None):
  rclpy.init(args=args)
  local_planner = LocalPlanner()
  rclpy.spin(local_planner)
  local_planner.destroy_node()
  rclpy.shutdown()

if __name__ == '__main__':
  main()