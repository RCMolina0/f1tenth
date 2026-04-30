import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'sig_stack'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/config', ['config/sensors.yaml']),
        ('share/' + package_name + '/launch', ['launch/slam_launch.py']),
        
        # Required to compile your map, config, and launch folders
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[pxy][yma]*'))),
        (os.path.join('share', package_name, 'config'), glob(os.path.join('config', '*.yaml'))),
        (os.path.join('share', package_name, 'maps'), glob(os.path.join('maps', '*'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='root',
    maintainer_email='root@todo.todo',
    description='F1Tenth Main Stack',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            # Required to run your Python script from the terminal
            'global_location = sig_stack.global_location:main'
          
            'perception = sig_stack.perception:main',
        ],
    },
)