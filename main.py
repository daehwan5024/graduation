import cv2
from djitellopy import tello
import time
import Controller
import os

# drone = tello.Tello()
# drone.connect()

# time.strftime("%Y-%m-%d-%H시%M분%S초", time.localtime(time.time()))
cap1 = cv2.VideoCapture(cv2.CAP_DSHOW + 0)
cap2 = cv2.VideoCapture(cv2.CAP_DSHOW + 0)

# drone.takeoff()

created_time_str = time.strftime("%Y-%m-%d-%H시%M분%S초", time.localtime(time.time()))
pid_x = Controller.Control(360, 0.5, 0, 0, created_time_str)
pid_y = Controller.Control(240, 0.5, 0, 0, created_time_str)
pid_z = Controller.Control(120, 0.5, 0, 0, created_time_str)
initial_time = time.time()
os.mkdir("D:/coding/PycharmProjects/graduation/data/" + created_time_str)
while True:
    ret1, img1 = cap1.read()
    ret2, img2 = cap2.read()

    if not (ret1 and ret2):
        continue

    x1, y1, img_filtered1 = Controller.get_center(img1, pid_x.get_last(), pid_y.get_last())
    x2, y2, img_filtered2 = Controller.get_center(img2, -1, -1)
    cv2.imshow('Image', img_filtered1)
    z1 = 120

    controlX = pid_x.append(x1, time.time() - initial_time)
    controlY = pid_y.append(y1, time.time() - initial_time)
    controlZ = pid_z.append(z1, time.time() - initial_time)

    if cv2.waitKey(1) & 0xFF == 27:
        break

    # drone.send_rc_control(-int(controlX), -int(controlZ), int(controlY), 0)

pid_x.save("X_position")
pid_y.save("Y_position")
pid_z.save("Z_position")

cap1.release()
cv2.destroyAllWindows()
