import cv2
import mediapipe as mp
import numpy as np
import time
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import HandTrackingModule as htm


def VolumeBar(x,img,volbar):
    if x:
        cv2.rectangle(img,(50,150),(85,400),(0,0,0),2)
        cv2.rectangle(img, (50, int(volbar)), (85, 400), (255, 0, 0), cv2.FILLED)
        cVol = int(volume.GetMasterVolumeLevelScalar() * 100)
        cv2.putText(img,f'{int(volper)}%',(40,450),cv2.FONT_HERSHEY_COMPLEX,1,
                    (255,0,0),2)
        cv2.putText(img, f'Vol set: {int(cVol)}%', (400, 450), cv2.FONT_HERSHEY_COMPLEX, 1,
                    (255, 0, 0), 2)

wCam, hCam = 640, 480

cap = cv2.VideoCapture(0)
cap.set(3,wCam)
cap.set(4,hCam)

detector = htm.handDetector(detectionCon=0.7,maxHands=1)

devices = AudioUtilities.GetSpeakers()
interface=devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

volrange=volume.GetVolumeRange()
minVol=volrange[0]
maxVol = volrange[1]

vol, volbar, volper = 0, 400, 0
while True:
    success,img=cap.read()
    # Find Hand
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img,draw=False)
    if len(lmList)!=0:
        # Bounding Box
        cv2.rectangle(img,(bbox[0]-20,bbox[1]-20), (bbox[2]+20,bbox[3]+20),(0,255,0), 3)    #BBOX requires width and height
        area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])//100
        #Filter based on hand
        if 250 < area < 1000:
            #Find Distance  between index and Thumb
            length, img, lineinfo= detector.findDistance(4, 8,img)

            #Convert Volumeu
            volbar = np.interp(length, [50, 250], [400, 150])
            volper = np.interp(length, [50, 250], [0, 100])
            #volume.SetMasterVolumeLevel(vol, None)

            #Reduce Resolution to make it smoother
            smoothness = 10
            volper = smoothness * round(volper/smoothness)

            
            #if pinky is down set the volume
            fingers= detector.fingerup()
            if sum(fingers) == 0:
                exit()
            if fingers[4] == 0:
                volume.SetMasterVolumeLevelScalar(volper / 100, None)
                cv2.circle(img, (lineinfo[4], lineinfo[5]), 15, (0, 255, 0), cv2.FILLED)

            #cv2.putText(img, str(sum(fingers)), (550, 100), cv2.FONT_HERSHEY_PLAIN, 5, (255,0,0))


            #Hand range 50 - 300
            #Volume Range -65 - 0


    VolumeBar(True,img,volbar)
    cv2.imshow("Image",img)
    cv2.waitKey(1)