import numpy as np
import cv2
def nothimg(x):
    pass
cap = cv2.VideoCapture(0)
cv2.namedWindow("Result")

cv2.createTrackbar("MinB","Result",0,255,nothimg)
cv2.createTrackbar("MinG","Result",0,255,nothimg)
cv2.createTrackbar("MinR","Result",0,255,nothimg)

cv2.createTrackbar("MaxB","Result",0,255,nothimg)
cv2.createTrackbar("MaxG","Result",0,255,nothimg)
cv2.createTrackbar("MaxR","Result",0,255,nothimg)

while True:
    ret, img = cap.read() # читаем кадр
    cv2.imshow("inpt", img)
    hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    minb=cv2.getTrackbarPos("MinB","Result")
    ming = cv2.getTrackbarPos("MinG", "Result")
    minr = cv2.getTrackbarPos("MinR", "Result")

    maxb = cv2.getTrackbarPos("MaxB", "Result")
    maxg = cv2.getTrackbarPos("MaxG", "Result")
    maxr = cv2.getTrackbarPos("MaxR", "Result")
    hsv=cv2.blur(hsv,(5,5))
    mask=cv2.inRange(hsv,(minb,ming,minr),(maxb,maxg,maxr))

    cv2.imshow("Res",mask)
    k = cv2.waitKey(30) & 0xff
    if k == 27: # press 'ESC' to quit
        break

cap.release() # close all windows
cv2.destroyAllWindows()