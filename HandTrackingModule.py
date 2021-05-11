import cv2
import mediapipe as mp
import time

class handDetector():
    def __init__(self, mode=False, 
                        maxHands = 2, 
                        min_detection_confidence = 0.5, 
                        min_tracking_confidence = 0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode,self.maxHands, 
                                        self.min_detection_confidence, 
                                        self.min_tracking_confidence)
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, frame, draw=True):
        # convert to rgb because Hands takes rgb image as input
        frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # get detected hands
        self.results = self.hands.process((frameRGB))

        if self.results.multi_hand_landmarks:
            for handLMS in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(frame, handLMS, 
                                                self.mpHands.HAND_CONNECTIONS)
        return frame

    def findPosition(self, frame, handNo=0, draw=True):
    
        left_lmList = []
        right_lmList = []
        if self.results.multi_hand_landmarks:
            if len(self.results.multi_hand_landmarks) == 1:
                myHand = self.results.multi_hand_landmarks[0]
                
                for id, lm in enumerate(myHand.landmark):
                    h, w, c = frame.shape
                    cx, cy = int(lm.x*w), int(lm.y*h)
                    left_lmList.append([id, cx, cy])
                    if draw:
                        cv2.circle(frame, (cx,cy), 15, (255,0,255), cv2.FILLED)            

            elif len(self.results.multi_hand_landmarks) == 2:
                right_Hand = self.results.multi_hand_landmarks[1]
                left_Hand = self.results.multi_hand_landmarks[0]

                for id, lm in enumerate(left_Hand.landmark):
                    h, w, c = frame.shape
                    cx, cy = int(lm.x*w), int(lm.y*h)
                    left_lmList.append([id, cx, cy])
                    if draw:
                        cv2.circle(frame, (cx,cy), 15, (255,0,255), cv2.FILLED)
                
                for id, lm in enumerate(right_Hand.landmark):
                    h, w, c = frame.shape
                    cx, cy = int(lm.x*w), int(lm.y*h)
                    right_lmList.append([id, cx, cy])
                    if draw:
                        cv2.circle(frame, (cx,cy), 15, (255,0,255), cv2.FILLED)
            
        return left_lmList, right_lmList

                

def main():
    pTime = 0
    cTime = 0

    video = cv2.VideoCapture(0)
    detector = handDetector()
    while True:
        ret, frame = video.read()

        if ret is not None:
            frame = detector.findHands(frame)
            lmList = detector.findPosition(frame)
            if len(lmList) != 0:
                print(lmList[4])
            cTime = time.time()
            fps = 1/(cTime - pTime)
            pTime = cTime

            cv2.putText(frame, str(int(fps)), (10,70), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 2, (255, 0, 255), 1)

            cv2.imshow("frame", frame)
            cv2.waitKey(1)

            if cv2.waitKey(30) & 0xFF == ord('q'):
                        break
        else:
            break

    video.release()
    cv2.destroyAllWindows()
    cv2.waitKey(1)


if __name__ == '__main__':
    main()