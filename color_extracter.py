import cv2
import numpy as np

hsv = 0
floor1 = 0
ceiling1 = 0
floor2 = 0
ceiling2 = 0
floor3 = 0
ceiling3 = 0


def nothing(null):
    pass


def mouse_callback(event, x_position, y_position, flags, param):
    global hsv, floor1, floor2, floor3, ceiling1, ceiling2, ceiling3
    h_threshold = 10    # under 90

    if event == cv2.EVENT_LBUTTONDOWN:
        color = img_color[y_position, x_position]
        one_pixel = np.uint8([[color]])
        hsv = cv2.cvtColor(one_pixel, cv2.COLOR_BGR2HSV)
        hsv = hsv[0][0]

        threshold = cv2.getTrackbarPos('threshold', 'img_result')

        if hsv[0] < h_threshold:
            floor1 = np.array([hsv[0]-h_threshold+180, threshold, threshold])
            ceiling1 = np.array([180, 255, 255])
            floor2 = np.array([0, threshold, threshold])
            ceiling2 = np.array([hsv[0], 255, 255])
            floor3 = np.array([hsv[0], threshold, threshold])
            ceiling3 = np.array([hsv[0]+h_threshold, 255, 255])

        elif hsv[0] > 180-h_threshold:
            floor1 = np.array([hsv[0], threshold, threshold])
            ceiling1 = np.array([180, 255, 255])
            floor2 = np.array([0, threshold, threshold])
            ceiling2 = np.array([hsv[0]+h_threshold-180, 255, 255])
            floor3 = np.array([hsv[0]-h_threshold, threshold, threshold])
            ceiling3 = np.array([hsv[0], 255, 255])

        else:
            floor1 = np.array([hsv[0], threshold, threshold])
            ceiling1 = np.array([hsv[0]+h_threshold, 255, 255])
            floor2 = np.array([hsv[0]-h_threshold, threshold, threshold])
            ceiling2 = np.array([hsv[0], 255, 255])
            floor3 = np.array([hsv[0]-h_threshold, threshold, threshold])
            ceiling3 = np.array([hsv[0], 255, 255])

        print("@1", floor1, "~", ceiling1)
        print("@2", floor2, "~", ceiling2)
        print("@3", floor3, "~", ceiling3)
        print("")


cv2.namedWindow('img_color')
cv2.setMouseCallback('img_color', mouse_callback)

cv2.namedWindow('img_result')
cv2.createTrackbar('threshold', 'img_result', 0, 255, nothing)
cv2.setTrackbarPos('threshold', 'img_result', 30)
camera_number = 0
cap = cv2.VideoCapture(cv2.CAP_DSHOW+camera_number)

while True:
    ret, img_color = cap.read()
    height, width = img_color.shape[:2]
    img_color = cv2.resize(img_color, (width, height), interpolation=cv2.INTER_AREA)

    # HSV 색공간으로 변형
    img_hsv = cv2.cvtColor(img_color, cv2.COLOR_BGR2HSV)
    img_hsv = cv2.blur(img_hsv, (5, 5), 0)
    img_mask1 = cv2.inRange(img_hsv, floor1, ceiling1)
    img_mask2 = cv2.inRange(img_hsv, floor2, ceiling2)
    img_mask3 = cv2.inRange(img_hsv, floor3, ceiling3)
    img_mask = img_mask1 | img_mask2 | img_mask3

    kernel = np.ones((11, 11), np.uint8)
    img_mask = cv2.morphologyEx(img_mask, cv2.MORPH_OPEN, kernel)
    img_mask = cv2.morphologyEx(img_mask, cv2.MORPH_CLOSE, kernel)

    img_result = cv2.bitwise_and(img_color, img_color, mask=img_mask)

    num_label, img_label, stats, centroids = cv2.connectedComponentsWithStats(img_mask)

    for ids, centroid in enumerate(centroids):
        if stats[ids][0] == 0 and stats[ids][1] == 0:
            continue

        if np.any(np.isnan(centroid)):
            continue

        x, y, width, height, area = stats[ids]
        centerX, centerY = int(centroid[0]), int(centroid[1])

        if area > 1500:
            cv2.circle(img_color, (centerX, centerY), 10, (0, 0, 255), 10)
            cv2.rectangle(img_color, (x, y), (x+width, y+height), (0, 0, 255))

    cv2.imshow('img_color', img_color)
    cv2.imshow('img_mask', img_mask)
    cv2.imshow('img_result', img_result)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
