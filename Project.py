'''
    Python Project Created by Aditya Jindal.
    This code specifically is for control mouse movements using hand gestures.
    Till now this code includes the following gestures:
        1. Cursor Movement 
        2. Single Click
        3. Double Click 
        4. Scroll up
        5. Scroll Down
    
    And planning to add the following gestures:
        • Screenshot
        • Type a specific Letter/ Word/ Line.
        • 
        
'''

import cv2 as cv 
import mediapipe as mp # type: ignore
import pyautogui as pag 
import time as t
import math as m
from util import get_angle, get_distance

''' Initialise Mediapipe and show lines on our one Hand'''
mp_hands=mp.solutions.hands
mp_drawing=mp.solutions.drawing_utils
hands=mp_hands.Hands(max_num_hands=2,min_detection_confidence=0.8)

''' To Start Webcam '''
cap=cv.VideoCapture(1)
# I have used "1" in the VideoCapture as I was using an apple ecosystem while creating this and in this the iphone camera is given preference 
# over the inbuilt webcam. So if the camera is not working then try changing the '1' to '0'.

''' Gesture Time Control '''
click_start_time = None
click_time = []
click_cooldown = 0.5
scroll_mode = False
freeze_cursor = False

''' To detect hand on Whole Screen '''
screen_w,screen_h = pag.size()
print("\nSmart Hand Mouse Control System \n ")
prev_screen_x , prev_screen_y = 0 , 0

''' If camera doesn't open then what to do'''
if not cap.isOpened():
    print("Camera could not been OPENED !!")
    exit()

''' Camera opens then '''
while True:
    ret,frame=cap.read()
    if not ret:
        print("Frame could not be received !!")
        break
    frame=cv.flip(frame,1)
    rgb=cv.cvtColor(frame,cv.COLOR_BGR2RGB)
    result=hands.process(rgb) 
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame,hand_landmarks,mp_hands.HAND_CONNECTIONS)

        ''' Get Fingertips '''
        thumb_tip = hand_landmarks.landmark[4]
        index_tip = hand_landmarks.landmark[8]
        middle_tip = hand_landmarks.landmark[12]
        ring_tip = hand_landmarks.landmark[16]
        pinky_tip = hand_landmarks.landmark[20]

        fingers = [
            1 if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip-2].y else 0
            for tip in [8,12,16,20]
        ]

        ''' Distance between Thumb and Index Finger '''
        dist = m.hypot( thumb_tip.x - index_tip.x , thumb_tip.y - index_tip.y )
        if dist < 0.06 :
            if not freeze_cursor:
                freeze_cursor = True 
                click_time.append(t.time())

                ''' Double Click Check'''
                if len(click_time) >= 2 and click_time[-1]-click_time[-2] < 0.4:
                    pag.doubleClick()
                    cv.putText(frame , "Double Click" , (10,50) , cv.FONT_HERSHEY_SIMPLEX , 1 , (0,255,255) , 2)
                    click_time=[]
                
                else: 
                    pag.click()
                    cv.putText(frame , "Single Click" , (10,50) , cv.FONT_HERSHEY_SIMPLEX , 1 , (255,255,0) , 2)

        else:
            if freeze_cursor:
                t.sleep(0.1)
            freeze_cursor = False

        ''' Move  cursor by using Index Finger '''
        if not freeze_cursor:
            screen_x = int(index_tip.x * screen_w)
            screen_y = int(index_tip.y * screen_h)
            pag.moveTo(screen_x,screen_y,duration=0.1)
            prev_screen_x,prev_screen_y = screen_x,screen_y

        ''' Scroll Mode '''
        if sum(fingers)==4:
            scroll_mode = True
        else :
            scroll_mode = False 

        ''' Scroll Action '''
        if scroll_mode:
            if index_tip.y < 0.35 :
                pag.scroll(10)
                cv.putText(frame , "Scroll Up" , (10,90) , cv.FONT_HERSHEY_SIMPLEX , 1 , (0,0,255) , 2)
            elif index_tip.y > 0.65:
                pag.scroll(-10)
                cv.putText(frame , "Scroll Down" , (10,90) , cv.FONT_HERSHEY_SIMPLEX , 1 , (255,0,0) , 2)

    cv.imshow("Live Video",frame)
    if(cv.waitKey(1)==ord('q')):
        break

cap.release()
cv.destroyAllWindows()