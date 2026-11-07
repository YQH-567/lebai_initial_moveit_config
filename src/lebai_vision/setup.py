from glob import glob
import os
from setuptools import find_packages, setup

package_name = 'lebai_vision'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='yqh',
    maintainer_email='19978531651@163.com',
    description='Camera-based 6D object pose estimation for Lebai LM3.',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'aruco_pose_node = lebai_vision.aruco_pose_node:main',
            'generate_aruco_marker = lebai_vision.generate_marker:main',
            'uvc_camera_node = lebai_vision.uvc_camera_node:main',
            'calibrate_uvc = lebai_vision.calibrate_uvc:main',
            'generate_checkerboard = lebai_vision.generate_checkerboard:main',
        ],
    },
)
