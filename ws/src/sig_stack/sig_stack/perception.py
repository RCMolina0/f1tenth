import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import PoseStamped

class Perception(Node):
    def __init__(self):
        super().__init__('percetion')

        # subscribes to odom published from tech stack 
        self.subscription = self.create_subscription(Odometry, 'odom', self.odom_callback, 10)
        self.publisher = self.create_publisher(PoseStamped, 'pose', 10)
        
        # publishes pose required 
        
        self.get_logger().info('Perception Node has been started.')

    def odom_callback(self, msg):
        
        # msg.pose.pose contains the geometry_msgs/Pose part
        current_pose = PoseStamped()
        current_pose.header = msg.header
        current_pose.pose = msg.pose.pose

        # log position
        self.get_logger().info(f'publishing position: x={current_pose.pose.position.x:.2f}, y={current_pose.pose.position.y:.2f}, z={current_pose.pose.position.z}')

        # Publish the extracted pose
        self.publisher.publish(current_pose)

def main(args=None):
    rclpy.init(args=args)
    perception = Perception()
    try:
        rclpy.spin(perception)
    except KeyboardInterrupt:
        pass
    finally:
        perception.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()