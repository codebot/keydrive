#!/usr/bin/env python
import rospy
from geometry_msgs.msg import Twist
import sys, select, tty, termios

key_mapping = {
    'q': [-1, -1],
    'w': [ 0, -1],
    'e': [ 1, -1],
    'a': [-1,  0],
    's': [ 0,  0],
    'd': [ 1,  0],
    'z': [-1,  1],
    'x': [ 0,  1],
    'c': [ 1,  1]
}


if __name__ == '__main__':
    rospy.init_node('keys_to_twist')
    twist_pub = rospy.Publisher('cmd_vel', Twist, queue_size=1)
    last_twist = Twist() # initializes to zero
    vel_scales = [0.1, 0.1] # default to very slow
    if rospy.has_param('~linear_scale'):
        vel_scales[1] = rospy.get_param('~linear_scale')
    else:
        rospy.logwarn("linear scale not provided; using %.1f" %\
                      vel_scales[1])

    if rospy.has_param('~angular_scale'):
        vel_scales[0] = rospy.get_param('~angular_scale')
    else:
        rospy.logwarn("angular scale not provided; using %.1f" %\
                      vel_scales[0])

    old_attr = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin.fileno())
    rate = rospy.Rate(100)
    last_auto_pub_time = rospy.Time.now()
    max_pub_interval = rospy.Duration(0.2)
    while not rospy.is_shutdown():
        t = rospy.Time.now()
        if t - last_auto_pub_time > max_pub_interval:
            print('auto pub: ' + str(last_twist.linear.x) + ' ' + str(last_twist.angular.z))
            twist_pub.publish(last_twist)
            last_auto_pub_time = t

        rate.sleep()
        if select.select([sys.stdin], [], [], 0)[0] == [sys.stdin]:
            key = sys.stdin.read(1)
            print('key: ' + key)
            if len(key) == 1 and key[0] in key_mapping:
                vels = key_mapping[key[0]]
                last_twist.angular.z = vels[0] * vel_scales[0]
                last_twist.linear.x  = vels[1] * vel_scales[1]
                twist_pub.publish(last_twist)

    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_attr)

    print('goodbye')
