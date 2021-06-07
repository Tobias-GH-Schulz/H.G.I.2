import cv2
import mediapipe as mp
import time
import HandTrackingModule as htm
import math
import numpy as np
from pymemcache.client import base 

def hand_gesture_run():
    # initialize the base client to store information used in different scripts
    hand_client = base.Client(("localhost", 11211))
    hand_client.set("rotation_mode", "initialize")
    hand_client.set("zoom_mode", "initialize")
    hand_client.set("update_info", {"initialize":1.25})

    # initialize video
    video = cv2.VideoCapture(0)

    # initialize hand detector
    detector = htm.handDetector(min_detection_confidence=0.85)

    while True:
        ret, frame = video.read()

        if ret is not None:
            frame = cv2.flip(frame, 1)
            frame = detector.findHands(frame)
            left_lmList, right_lmList = detector.findPosition(frame, draw=False)
            tipIds = [4, 8, 12, 16, 20]
            lenght = None

            # check if there are two hands
            if len(left_lmList) != 0 and len(right_lmList) != 0:
                # count the number of raised fingers
                fingers = [] 
                for id in range(1, 5):
                    if left_lmList[tipIds[id]][2] < left_lmList[tipIds[id]-2][2]:
                        fingers.append(1)
                    if right_lmList[tipIds[id]][2] < right_lmList[tipIds[id]-2][2]:
                        fingers.append(1)
                num_fingers = fingers.count(1)

                # check if the second finger of both hands is up and all other fingers are down
                for i in range(2,5):           
                    if left_lmList[8][2] < left_lmList[6][2] and right_lmList[8][2] < right_lmList[6][2] and left_lmList[tipIds[id]][2] > left_lmList[tipIds[id]-2][2] and right_lmList[tipIds[id]][2] > right_lmList[tipIds[id]-2][2]:

                        # get the x,y coordinates for the tip of the second finger for the right hand
                        right_x, right_y = right_lmList[8][1], right_lmList[8][2]
                        # get the x,y coordinates for the tip of the second finger for the left hand
                        left_x, left_y = left_lmList[8][1], left_lmList[8][2]

                        # get center of distance between the two tips
                        cx, cy = (left_x+right_x)//2, (left_y+left_y)//2

                        # draw bigger circles on the two tips
                        cv2.circle(frame, (right_x, right_y), 15, (255,0,255), cv2.FILLED)
                        cv2.circle(frame, (left_x,left_y), 15, (255,0,255), cv2.FILLED)

                        # draw line between the two tips
                        cv2.line(frame, (left_x,left_y), (right_x,right_y), (255,0, 255), 3)

                        # use hypothenuse function to get distance between the two tips
                        lenght = math.hypot(abs(left_x-right_x), abs(left_y-right_y))

                        # transform distance into zoom scale of plotly 
                        zoom = np.interp(lenght, [15, 700], [4.0, 0.000001])

                        # as soon as 3 or more fingers ar up, write state "zoom off" in a txt file 
                        if num_fingers >= 3:
                            hand_client.set("zoom_mode", "zoom off")

                        # if only 2 fingers are up write the zoom value in a txt file
                        else:
                            hand_client.set("update_info", {"zoom":zoom})

            # check if there is only one hand
            if len(left_lmList) != 0 and len(right_lmList) <= 10:
                # count the number of raised fingers
                fingers = [] 
                for id in range(1, 5):
                    if left_lmList[tipIds[id]][2] < left_lmList[tipIds[id]-2][2]:
                        fingers.append(1)
                num_fingers = fingers.count(1)

                # check if the second finger is up
                if left_lmList[8][2] < left_lmList[6][2]:
                    # get the x,y coordinates for the tip of the second finger 
                    x1, y1 = left_lmList[8][1], left_lmList[8][2]
                    
                    # draw bigger circles on the two tips
                    cv2.circle(frame, (x1,y1), 15, (255,0,255), cv2.FILLED)
                    
                    # set an area in which the rotation value is written
                    if 500 < x1 < 1450:
                        theta = np.interp(x1, [500, 1450], [0.000001, 10.0])
                    
                    # as soon as 3 or more fingers ar up, write state "rotation off" in a txt file 
                    if num_fingers >= 3:
                        hand_client.set("rotation_mode", "rotation off")

                    # if only 2 fingers are up write the rotation value in a txt file
                    else:
                        hand_client.set("update_info", {"rotate_xy":theta})

            cv2.imshow("frame", frame)
            cv2.waitKey(1)

            if cv2.waitKey(30) & 0xFF == ord('q'):
                        break
        else:
            break

    video.release()
    cv2.destroyAllWindows()
    cv2.waitKey(1)



if __name__ == "__main__":
    hand_gesture_run()