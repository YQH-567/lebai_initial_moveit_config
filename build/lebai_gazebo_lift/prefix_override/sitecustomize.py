import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/l/dev_ws_02/lebai_moveit2_ws/install/lebai_gazebo_lift'
