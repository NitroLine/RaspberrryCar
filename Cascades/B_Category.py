import numpy as np
import cv2
import time
import serial
import time
import RPi.GPIO as GPIO
ser = serial.Serial("/dev/ttyUSB0",9600)  # change ACM number as found from ls /dev/tty/ACM* выбор 0-го последовательнного порта для общения межу платами
ser.baudrate = 9600  # скорость порта
GPIO.setmode(GPIO.BOARD)

cap = cv2.VideoCapture(0)

def send2Arduino(x):
    encode_x = str.encode(x)  # закодированная строка, вроде в 16-тиричной системе счисления
    ser.write(encode_x)

def line2FindLine(img,minold,View,debug=False):
    N=View
    w=0
    centr=0
    r=0
    mas=[0]*640
    c=150
    while c<len(img[0])-150:
        b=c
        e=b
        while (e<640-150 and img[N][e][2]<50 and img[N][e][1]<50 and img[N][e][0]<50):
            e+=1
        w=e
        lin=e-b
        if (lin<50):
            c+=1
            continue
        if lin>200:
            return minold
        #print("Line "+str(lin))
        centr=(b+w)//2
        c=e
        mas[r]=centr
        r+=1
        c+=1
    mi=640
    #print(mas[:r+1])
    for i in range(r):
        if (abs(mas[i])-minold<mi):
            mi=mas[i]
    if debug:
        cv2.circle(img,(mi,View),10,(0,255,0),1)
        cv2.imshow("Line2Debug",img)
    return mi



imgCount = 0
# main
debug=False
save=False
send2Arduino("Start#")
startTime=time.time()
roIm=0
started=0
lastTime=0
lastTrafficTime=0
View=410 
x=90
kkk=0
minold=320
send2Arduino("Start#")
while True:
    try:
        if not started and time.time()-startTime>6:
            print("I_AM_READY")
            send2Arduino("Start#")
            started=1
        
        ret, img = cap.read()
        #roFrame = img[:300, 350:]
        #cv2.imshow("InputVideo", img)
        if (started):
            x=line2FindLine(img,minold,View,debug)
            #print(x)
            if (x==640 and minold!=640):
                kkk+=1
                x=minold
                if (kkk>0):
                    #print("Not autocontrast")
                    k=0
                    minold=640
            else:
                kkk=0
                minold=x
            if x==640:
                View=460
            else:
                View=370
            send2Arduino("Line*"+str(x)+"#")
        else:
            cv2.imshow("InputVideo", img)
        ch = cv2.waitKey(1)
        if save:
            if len(roIm)>1:
                if ch == 114:  # press R to save img
                    print("Save!")
                    cv2.imwrite(str(imgCount) + "_save.jpg", roIm)
                    imgCount += 1
        else:
            lastTime=roIm
        if ch == 27:  # "ESC" for exit
            break
    except KeyboardInterrupt:
        break
send2Arduino("End#")
cap.release()  # завершение чтения кадров
cv2.destroyAllWindows()  # закрытие всех окон
