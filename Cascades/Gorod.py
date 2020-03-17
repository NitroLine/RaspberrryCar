import numpy as np
import cv2
import time
import serial
import time
import RPi.GPIO as GPIO

ser = serial.Serial("/dev/ttyUSB0",115200)  # change ACM number as found from ls /dev/tty/ACM* выбор 0-го последовательнного порта для общения межу платами
ser.baudrate = 115200  # скорость порта
GPIO.setmode(GPIO.BOARD)

cap = cv2.VideoCapture(0)
files = ['stopgitCas.xml', 'svetCas3.xml','pedUs.xml']
nameSing = ["Stop", "Svet","Pedus"]
cascades = dict()
for i in range(len(files)):
    cascades[nameSing[i]] = cv2.CascadeClassifier(files[i])

minColor = (77, 89, 142)
maxColor = (255, 255, 255)

def send2Arduino(x):
    encode_x = str.encode(x)  # закодированная строка, вроде в 16-тиричной системе счисления
    ser.write(encode_x)
def clasificateCirlce(frame, debug=True):
    height, weight,g = frame.shape
    circles = [[height//6,weight//2,5],[height//2,weight//2,5],[5*height//6,weight//2,5]]
    com = None
    for ind in range(3):
        y,x, r = circles[ind]
        blue, green, red = frame[y-1][x-1][0], frame[y-1][x-1][1], frame[y-1][x-1][2]
        if (ind == 0): # red color
            print("reds--> {}, {}, {}".format(red, green, blue))
            if (red >= 200 and green >= 20 and blue >= 20):
                cv2.circle(frame, (x, y), 1, (255, 0, 0), 2)
                com="RED#"
                print("RED FOUND")
                break
        elif (ind == 1): # yellow color
            print("yellow--> {}, {}, {}".format(red, green, blue))
            if (red >= 200 and green >= 200 and blue >= 10):
                cv2.circle(frame, (x, y), 1, (255, 0, 0), 2)
                com="YELLOW#"
                print("YELLOW FOUND")
                break
        else:
            print("green--> {}, {}, {}".format(red, green, blue))
            if (red >= 20 and green >= 190 and blue >= 0):
                com="GREEN#"
                cv2.circle(frame, (x, y), 1, (255, 0, 0), 2)
                print("GREEN FOUND")
                break
    if (debug):	
        cv2.imshow("Detected Circle", frame) 
    return com

def ClassificateByCascade(img):
    #img = cv2.resize(img, (60, 60))
    allfound = []
    for a in cascades:
        s = cascades[a].detectMultiScale(img)
        for (ex, ey, ew, eh) in s:
            cv2.rectangle(roFrame, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 1)
            allfound.append([ew * eh, a,img[ey:ey+eh,ex:ex+ew]])
    if len(allfound) == 0:
        return 0
    BigestSing = max(allfound, key=lambda x: x[0])
    print("I found " + BigestSing[1])
    return actionForSing(BigestSing[1],BigestSing[2])


def actionForSing(sing,img):
    if "Pedus" == sing:
        com = "Pedus#"
        print(com)
    elif "Stop" == sing:
        com = "Stop#"
        print(com)  # debug
    elif "Svet" == sing:
        com = clasificateCirlce(img,True)
        if com is not None:
            com="Light*"+com
        else:
            return 0
        print(com)
    send2Arduino(com)
    return time.time()

kernel = np.ones((5, 5), np.uint8)


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
save=True
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
        roFrame = img[:300, 350:]
        saveImg=roFrame.copy()
        #cv2.imshow("InputVideo", img)
        if (started):
            if time.time()-lastTrafficTime>1:
                lastTrafficTime=ClassificateByCascade(roFrame)
                cv2.imshow("ROI", roFrame)
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
            if len(saveImg)>1:
                if ch == 114:  # press R to save img
                    print("Save!")
                    cv2.imwrite(str(imgCount) + "_ss.jpg", saveImg)
                    imgCount += 1
        if ch == 27:  # "ESC" for exit
            break
    except KeyboardInterrupt:
        break
send2Arduino("End#")
cap.release()  # завершение чтения кадров
cv2.destroyAllWindows()  # закрытие всех окон
