from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    sensors_config = os.path.join(
        get_package_share_directory('sig_stack'),
        'config',
        'sensors.yaml'
    )

    return LaunchDescription([
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='base_to_laser_tf',
            arguments=['0.27', '0.0', '0.11', '0', '0', '0', 'base_link', 'laser'],
            output='screen'
        ),

        Node(
            package='urg_node',
            executable='urg_node_driver',
            name='urg_node',
            parameters=[sensors_config],
            output='screen'
        ),

        Node(
            package='slam_toolbox',
            executable='async_slam_toolbox_node',
            name='slam_toolbox',
            output='screen',
            parameters=[{
                'odom_frame': 'odom',
                'map_frame': 'map',
                'base_frame': 'base_link',
                'scan_topic': '/scan',
                'use_sim_time': False
            }]
        ),
    ])