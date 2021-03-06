"""
마커의 중앙 위치, PID 제어와 같은 연산을 위해 제작한 라이브러리
"""

import math

import cv2
import numpy as np

floor = np.array([83, 120, 120])
ceiling = np.array([103, 255, 255])


def get_center(img, location_x, location_y):  # img에서 기존의 위치에서 가장 가까운 마커의 중앙 값을 리턴
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    img_mask = cv2.inRange(img_hsv, floor, ceiling)
    kernel = np.ones((11, 11), np.uint8)
    img_mask = cv2.morphologyEx(img_mask, cv2.MORPH_OPEN, kernel)

    label_num, img_label, stats, centroids = cv2.connectedComponentsWithStats(img_mask)
    return_x = -1
    return_y = -1
    dist_min = float(10000.0)

    for ids, centroid in enumerate(centroids):
        if stats[ids][0] == 0 and stats[ids][1] == 0:
            continue
        if np.any(np.isnan(centroid)):
            continue

        x, y, width, height, area = stats[ids]
        center_x, center_y = int(centroid[0]), int(centroid[1])

        if area > 500:
            dist = math.dist((location_x, location_y), (center_x, center_y))
            if dist <= dist_min:
                return_x = center_x
                return_y = center_y
                dist_min = dist
                cv2.circle(img, (center_x, center_y), 10, (0, 0, 255), 5)
                cv2.rectangle(img, (x, y), (x + width, y + height), (0, 0, 255))
    return return_x, return_y, img


def make_str(obj):  # obj내의 값을 String 형태로 리턴
    return_str = ""
    enumerate_obj = enumerate(obj)
    for x, value in enumerate_obj:
        return_str = return_str + str(value) + "\n"
    return return_str


class GetCenter:  # 마커의 위치를 기록하고 img에서 마커의 중앙 위치를 계산
    def __init__(self):
        self.x_position = []
        self.y_position = []
        self.len = 0

    def cal_pos(self, img):
        if self.len == 0:
            x_position, y_position, ret_img = get_center(img, -1, -1)
            if x_position != -1:
                self.x_position.append(x_position)
                self.y_position.append(y_position)
                self.len += 1
            return x_position, y_position, ret_img
        else:
            x_position, y_position, ret_img = get_center(img, self.x_position[-1], self.y_position[-1])
            if x_position != -1:
                self.x_position.append(x_position)
                self.y_position.append(y_position)
                self.len += 1
            return x_position, y_position, ret_img


class Control:  # PID 제어의 연산을 위해 만든 클래스
    def __init__(self, goal, k_p, k_i, k_d, create_time, name):
        self.goal = goal
        self.name = name
        self.k_p = k_p
        self.k_i = k_i
        self.k_d = k_d
        self.location = []
        self.error = []
        self.time = []
        self.create_time = create_time
        self.Integral = 0
        self.goal_changed = 0
        self.len = 0
        self.return_value = []

    def append(self, location, time):
        if location == -1:
            return 0
        self.len += 1
        self.location.append(location)
        self.error.append(self.goal - location)
        self.time.append(time)
        if self.len == 1:
            derivative = 0
        else:
            derivative = (self.error[-1] - self.error[-2]) / (self.time[-1] - self.time[-2])
            self.Integral += (self.error[-1] + self.error[-2]) * (self.time[-1] - self.time[-2]) / 2
        self.return_value.append(self.error[-1] * self.k_p + self.Integral * self.k_i + derivative * self.k_d)
        return self.return_value[-1]

    def change_goal(self, goal):
        self.goal_changed += 1
        self.save(self.name+str(self.goal_changed))
        if goal == -1:
            return
        self.goal = goal
        self.location = []
        self.error = []
        self.time = []
        self.return_value = []
        self.Integral = 0
        self.len = 0

    def save(self, name):
        if self.len == 0:
            return
        f = open("./data/" + self.create_time + "/" + name + "_time.txt", 'w')
        f.write("goal : " + str(self.goal) + "\n")
        f.write(str(self.len) + '\n\n\n')
        f.write("time\n")
        f.write(make_str(self.time))
        f.close()

        f = open("./data/" + self.create_time + '/' + name + "_location.txt", 'w')
        f.write("location\n")
        f.write(make_str(self.location))
        f.close()

        f = open("./data/" + self.create_time + '/' + name + "_return_value.txt", 'w')
        f.write("return value\n")
        f.write(make_str(self.return_value))
        f.close()
