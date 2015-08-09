#!/usr/bin/python
import sys
import math
from copy import deepcopy


import rospy
import tf
from geometry_msgs.msg import Pose, PoseStamped
from moveit_msgs.msg import CollisionObject
from shape_msgs.msg import SolidPrimitive
from visualization_msgs.msg import Marker, InteractiveMarker, InteractiveMarkerControl
from interactive_markers.interactive_marker_server import *


class InteractiveObstacle:
    def __init__(self):

        #Specify a frame_id - transformation to root_frame of obstacle_distance node is handled in according subscriber callback
        self.root_frame = rospy.get_param("root_frame")

        self.pub = rospy.Publisher("obstacle_distance/registerObstacle", CollisionObject, queue_size=1, latch=True)
        self.br = tf.TransformBroadcaster()

        while self.pub.get_num_connections() < 1:
            rospy.logwarn("Please create a subscriber to '" + rospy.get_namespace() + "/obstacle_distance/registerObstacle' topic (Type: moveit_msgs/CollisionObject)")
            rospy.sleep(1.0)

        rospy.loginfo("Continue ...")

        # Compose CollisionObject (Box)
        self.co = CollisionObject()
        self.co.id = "Interactive Box"
        self.co.header.frame_id = "interactive_box_frame"
        self.co.operation = CollisionObject.ADD

        box = SolidPrimitive()
        box.type = SolidPrimitive.BOX
        box.dimensions = [0.2, 0.2, 0.2] # extent x, y, z
        self.co.primitives.append(box)

        pose = Pose()
        pose.orientation.w = 1.0;
        self.co.primitive_poses.append(pose)

        # Compose InteractiveMarker
        self.interactive_box_pose = PoseStamped()
        self.interactive_box_pose.header.stamp = rospy.Time.now()
        self.interactive_box_pose.header.frame_id = self.root_frame

        self.interactive_box_pose.pose.position.x = -0.5
        self.interactive_box_pose.pose.position.y =  0.3
        self.interactive_box_pose.pose.position.z =  0.8
        self.interactive_box_pose.pose.orientation.w = 1.0

        self.ia_server = InteractiveMarkerServer("marker_server")
        self.int_marker = InteractiveMarker()
        self.int_marker.header.frame_id = self.root_frame
        self.int_marker.pose = self.interactive_box_pose.pose
        self.int_marker.name = "interactive_box_marker"
        self.int_marker.scale = 0.5

        # Setup MarkerControls
        control_3d = InteractiveMarkerControl()
        control_3d.always_visible = True
        control_3d.name = "move_rotate_3D"
        control_3d.interaction_mode = InteractiveMarkerControl.MOVE_ROTATE_3D
        self.int_marker.controls.append(control_3d)

        control = InteractiveMarkerControl()
        control.always_visible = True
        control.orientation.w = 1
        control.orientation.x = 1
        control.orientation.y = 0
        control.orientation.z = 0
        control.name = "move_x"
        control.interaction_mode = InteractiveMarkerControl.MOVE_AXIS
        self.int_marker.controls.append(deepcopy(control))
        control.name = "move_y"
        control.orientation.x = 0
        control.orientation.y = 1
        control.interaction_mode = InteractiveMarkerControl.MOVE_AXIS
        self.int_marker.controls.append(deepcopy(control))
        control.name = "move_z"
        control.orientation.y = 0
        control.orientation.z = 1
        control.interaction_mode = InteractiveMarkerControl.MOVE_AXIS
        self.int_marker.controls.append(deepcopy(control))
        control.orientation.w = 1
        control.orientation.x = 1
        control.orientation.y = 0
        control.orientation.z = 0
        control.name = "rotate_x"
        control.interaction_mode = InteractiveMarkerControl.ROTATE_AXIS
        self.int_marker.controls.append(deepcopy(control))
        control.name = "rotate_y"
        control.orientation.x = 0
        control.orientation.y = 1
        control.interaction_mode = InteractiveMarkerControl.ROTATE_AXIS
        self.int_marker.controls.append(deepcopy(control))
        control.name = "rotate_z"
        control.orientation.y = 0
        control.orientation.z = 1
        control.interaction_mode = InteractiveMarkerControl.ROTATE_AXIS
        self.int_marker.controls.append(deepcopy(control))

        self.ia_server.insert(self.int_marker, self.marker_fb)
        self.ia_server.applyChanges()

        # initial send
        self.br.sendTransform(
            (self.interactive_box_pose.pose.position.x, self.interactive_box_pose.pose.position.y, self.interactive_box_pose.pose.position.z),
            (self.interactive_box_pose.pose.orientation.x, self.interactive_box_pose.pose.orientation.y, self.interactive_box_pose.pose.orientation.z, self.interactive_box_pose.pose.orientation.w),
             rospy.Time.now(), "interactive_box_frame", self.interactive_box_pose.header.frame_id)
        rospy.sleep(1.0)
        self.pub.publish(self.co)
        rospy.sleep(1.0)

    def marker_fb(self, fb):
        #p = feedback.pose.position
        #print feedback.marker_name + " is now at " + str(p.x) + ", " + str(p.y) + ", " + str(p.z)
        self.interactive_box_pose.header = fb.header
        self.interactive_box_pose.pose = fb.pose
        self.ia_server.applyChanges()

    def run(self):
        self.br.sendTransform(
            (self.interactive_box_pose.pose.position.x, self.interactive_box_pose.pose.position.y, self.interactive_box_pose.pose.position.z),
            (self.interactive_box_pose.pose.orientation.x, self.interactive_box_pose.pose.orientation.y, self.interactive_box_pose.pose.orientation.z, self.interactive_box_pose.pose.orientation.w),
             rospy.Time.now(), "interactive_box_frame", self.interactive_box_pose.header.frame_id)

        self.co.operation = CollisionObject.MOVE
        self.pub.publish(self.co)


if __name__ == "__main__":
    rospy.init_node("interactive_obstacle_node")

    io = InteractiveObstacle()

    r = rospy.Rate(20)
    while not rospy.is_shutdown():
        io.run()
        try:
            r.sleep()
        except rospy.ROSInterruptException as e:
            #print "ROSInterruptException"
            pass
