"""
Controller.py 를 이용해 직접 드론을 제어함
카메라의 입력을 관리함
"""

import math
import os
import time

import cv2
from djitellopy import tello

import Controller


def nothing(null):
    pass


drone = tello.Tello()
drone.connect()


def change_goal():  # 목표 위치 바꾸기
    x = cv2.getTrackbarPos("position X", "controller")
    y = cv2.getTrackbarPos("position Y", "controller")
    z = cv2.getTrackbarPos("position Z", "controller")
    global goal_x, goal_y, goal_z
    goal_x = x
    goal_y = y
    goal_z = z
    pid_x.change_goal(goal_x)
    pid_y.change_goal(goal_y)
    pid_z.change_goal(goal_z)


cap1 = cv2.VideoCapture(cv2.CAP_DSHOW + 0)  # 왼쪽 카메라 (드론의 x 좌표가 더 큼)
cap2 = cv2.VideoCapture(cv2.CAP_DSHOW + 0)  # 오른쪽 카메라 (드론의 x 좌표가 더 작음)
cap1.set(cv2.CAP_PROP_FRAME_WIDTH, 1920), cap1.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080), cap1.set(cv2.CAP_PROP_FPS, 60)
cap2.set(cv2.CAP_PROP_FRAME_WIDTH, 1920), cap2.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080), cap2.set(cv2.CAP_PROP_FPS, 60)


'''기본 위치 설정 : 화면의 중앙, z축 거리는 90cm'''
goal_x = int(cap1.get(cv2.CAP_PROP_FRAME_WIDTH)/2)
goal_y = int(cap1.get(cv2.CAP_PROP_FRAME_HEIGHT)/2)
goal_z = 90

'''목표 위치 제어를 위한 창 생성'''
cv2.namedWindow("controller")
cv2.createTrackbar("position X", 'controller', goal_x, goal_x*2, nothing)
cv2.createTrackbar("position Y", 'controller', goal_y, goal_y*2, nothing)
cv2.createTrackbar("position Z", 'controller', goal_z, 300, nothing)

drone.takeoff()

'''PID 제어를 위한 클래스 생성'''
created_time_str = time.strftime("%Y-%m-%d-%H시%M분%S초", time.localtime(time.time()))
pid_x = Controller.Control(goal_x, 0.05, 0.01, 0, created_time_str, "X")
pid_y = Controller.Control(goal_y, 0.05, 0.01, 0, created_time_str, "Y")
pid_z = Controller.Control(goal_z, 0.5, 0.1, 0, created_time_str, "Z")

os.mkdir("D:/coding/PycharmProjects/graduation/data/" + created_time_str)  # 데이터 값 저장

get_center1 = Controller.GetCenter()
get_center2 = Controller.GetCenter()
initial_time = time.time()

while True:
    ret1, img1 = cap1.read()
    ret2, img2 = cap2.read()

    if not (ret1 and ret2):
        continue

    x1, y1, img_filtered1 = get_center1.cal_pos(img1)
    x2, y2, img_filtered2 = get_center2.cal_pos(img2)
    cv2.circle(img_filtered1, (goal_x, goal_y), 10, (0, 255, 255), 5)
    cv2.imshow('Image2', cv2.resize(img_filtered2, (0, 0), fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA))
    cv2.imshow('Image1', cv2.resize(img_filtered1, (0, 0), fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA))
    if x1 != x2:
        z1 = 15016.58805/(x1-x2) - 0.533044081
    else:
        z1 = -1

    controlX = pid_x.append(x1, time.time() - initial_time)
    controlY = pid_y.append(y1, time.time() - initial_time)
    controlZ = pid_z.append(z1, time.time() - initial_time)
    print("{}, {}, {}".format(x1, y1, z1))

    key_pressed = cv2.waitKey(1) & 0xFF
    if key_pressed == 13:
        change_goal()
    elif key_pressed == 27:
        break
    drone.send_rc_control(-1*math.ceil(controlX), -1*math.ceil(controlZ), -1*math.ceil(controlY), 0)

'''마지막으로 기록된 것 저장'''
pid_x.change_goal(-1)
pid_y.change_goal(-1)
pid_z.change_goal(-1)

'''저장된 데이터가 없으면 만들어둔 파일 경로를 삭제'''
if (pid_x.len == 0) and (pid_y.len == 0) and (pid_z.len == 0):
    os.rmdir("D:/coding/PycharmProjects/graduation/data/" + created_time_str)

drone.land()
cap1.release()
cap2.release()
cv2.destroyAllWindows()
