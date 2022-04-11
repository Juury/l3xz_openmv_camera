#!/usr/bin/python3
#-*- coding: utf-8 -*-
'''
This software is distributed under the terms of the MIT License.
Copyright (c) 2022 107-Systems
Author: Jonas Wühr
'''

import threading
import cv2
import numpy as np
import time

import rospy
import roslib
from sensor_msgs.msg import Image
from sensor_msgs.msg import CompressedImage
from sensor_msgs.msg import CameraInfo 

from l3xz_openmv_camera.srv import rgb, rgbResponse
from camera_interface import OpenMvInterface

omv_cam = None
mutex = threading.Lock() # Mutex for asynchronous services and publishing.

def rgb_callback(request): # rgb service implementation
  global omv_cam
  global mutex
  mutex.acquire()
  success = omv_cam.rgb_led(request.r, request.g, request.b)
  mutex.release()
  return rgbResponse(success)

def main():
  global omv_cam
  # Initialize node, camera, services, publishers and subscribers with parameters.
  rospy.init_node('openmv')

  frame_id = rospy.get_param("~frame_id", "openmv_camera_frame")

  show = rospy.get_param("~show_image", False)

  rate = rospy.Rate(rospy.get_param("~rate_hz", 10))

  omv_cam = OpenMvInterface(rospy.get_param("~port", "/dev/ttyACM0"),
     rospy.get_param("~resolution", "QQVGA"))

  service = rospy.Service(rospy.get_name() + '/rgb', rgb, rgb_callback)

  img_name = rospy.get_name() + "/" + rospy.get_param("~image_topic", "image_color")
  
  pub_image = rospy.Publisher(img_name,
          Image, queue_size = rospy.get_param("~image_queue", 1))

  pub_image_compressed = rospy.Publisher(img_name + "_compressed",
          CompressedImage, queue_size = rospy.get_param("~image_queue", 1))

  pub_info = rospy.Publisher(rospy.get_name() + "/" + rospy.get_param("~info_topic", "camera_info"),
          CameraInfo, queue_size = rospy.get_param("~image_queue", 1))

  # Initialize messages.
  img_msg = Image()
  img_msg.header.frame_id = frame_id
  img_compressed_msg = CompressedImage()
  img_compressed_msg.header.frame_id = frame_id

  info_msg = CameraInfo()
  info_msg.header.frame_id = frame_id

  global mutex
  while not rospy.is_shutdown():
    mutex.acquire()
    framedump = omv_cam.dump() # Get new frame from camera buffer.
    mutex.release()
    if framedump is not None:
      if show: # Show if required.
        cv2.imshow(img_name, framedump.pixels)
        cv2.waitKey(1)
      # Publish what we have.
      pub_image.publish(framedump.fill_img_msg(img_msg))
      pub_image_compressed.publish(framedump.fill_jpeg_msg(img_compressed_msg))
      pub_info.publish(framedump.fill_info_msg(info_msg))
      
    rate.sleep()

if __name__ == '__main__':
  main()
