#!/usr/bin/env python
# license removed for brevity
import rospy
from nav_msgs.msg import Odometry
from sensor_msgs.msg import JointState
from geometry_msgs.msg import Twist
from tf.transformations import euler_from_quaternion
import time
import math

pos=0
x_speed = 1.0
Angle=0
maxDist = 10

def stop(twist,pub):
    twist.linear.x = 0;
    twist.angular.z = 0;
    rospy.loginfo("Stop "+str(twist))
    pub.publish(twist)
    time.sleep(1)

def adelante(twist, pub, rate):
    twist.linear.x = x_speed;
    twist.angular.z = 0;
    counter = 0
    obj=[pos[0]+maxDist,pos[1]]
    while ((not rospy.is_shutdown()) and (abs(obj[0]-pos[0])>0.8)):
        rospy.loginfo(twist)
        pub.publish(twist)
        rate.sleep()
    stop(twist,pub)

def atras(twist, pub, rate):
    counter = 0
    obj=[pos[0]-maxDist,pos[1]]
    twist.linear.x=-x_speed
    while ((not rospy.is_shutdown()) and (abs(obj[0]-pos[0])>0.8)):
        rospy.loginfo(twist)
        pub.publish(twist)
        rate.sleep()
    stop(twist,pub)

def detGiro(grados):
    global Angle
    algo=grados- Angle
    if ((algo<180 and algo>0) or algo<-180):
	return 1
    else:
        return -1


#obj debe estar en grados normales
def girar(twist, pub, rate,obj):
    if (obj<0):
       obj=obj+360
    global Angle
    twist.linear.x=0.0
    twist.linear.y=0.0
    twist.angular.z=0.6*detGiro(obj)

    while ((not rospy.is_shutdown()) and (abs(obj-Angle)>5.0)):
        rospy.loginfo("obj: " + str(obj) + " angulo: " + str(Angle) +" delta: " + str(abs(obj-Angle)))
        rospy.loginfo(twist)
        pub.publish(twist)
        rate.sleep()
    stop(twist,pub)

def reciver_odom(data):
    global Angle
    pose=data.pose.pose
    quaternion = (
    pose.orientation.x,
    pose.orientation.y,
    pose.orientation.z,
    pose.orientation.w)
    (roll , pitch , yaw) = euler_from_quaternion(quaternion)
    tAngle = math.degrees(yaw)
    if (tAngle<0):
       tAngle = tAngle+360
    Angle = tAngle

def reciver_joint_states(algo):
    global pos
    #rospy.loginfo(pos)
    pos=algo.position

def talker():
    global x_speed
    global pos
    pub = rospy.Publisher('cmd_vel_mux/input/teleop', Twist, queue_size=10)
    rospy.Subscriber("joint_states",JointState, reciver_joint_states)
    rospy.Subscriber('odom',Odometry, reciver_odom)
    rospy.init_node('Baile', anonymous=True)
    rate = rospy.Rate(10) # 10hz
    twist = Twist()
    twist.linear.x = x_speed;
    giro = 180
    girar(twist, pub, rate,giro)
    while(1==1):
        girar(twist, pub, rate,giro+45)
        adelante(twist, pub, rate)
        atras(twist, pub, rate)
	girar(twist, pub, rate,giro-45)
        adelante(twist, pub, rate)
        atras(twist, pub, rate)
        giro = (giro + 45) % 360
        
    
    

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
