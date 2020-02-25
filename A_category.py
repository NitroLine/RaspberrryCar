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
files = ['stopgitCas.xml', 'roadCas.xml', 'preim2.6Znak5.xml', 'preim2.7Znak5.xml']
nameSing = ["Stop", "Road", "advantageRound", "advantageSquare"]
cascades = dict()
for i in range(len(files)):
    cascades[nameSing[i]] = cv2.CascadeClassifier(files[i])

minColor = (77, 89, 142)
maxColor = (255, 255, 255)

def send2Arduino(x):
    encode_x = str.encode(x)  # закодированная строка, вроде в 16-тиричной системе счисления
    ser.write(encode_x)

def FindSingBox(img,debug=False,save=False,Canny=False):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    height, weight = gray.shape
    if Canny:
        finalImg = cv2.Canny(gray, 126, 208)  # 278 130
    else:
        finalImg = preprocess_img(img)
    if debug:
        cv2.imshow("procesed image", finalImg)
    bi, conturs, hierarchy = cv2.findContours(finalImg, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    # conturs, hierarchy = cv2.findContours(finalImg, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    conturs = sorted(conturs, key=cv2.contourArea, reverse=True)
    if conturs:
        BigContur = conturs[0]
        approx = cv2.approxPolyDP(BigContur, cv2.arcLength(BigContur, True) * 0.03, True)
        area = abs(cv2.contourArea(BigContur))
        # debug
        # cv2.drawContours(img2,contur,0,(255,0,255),3)
        # cv2.polylines(img2,  approx,  True,  (0, 255, 0),  2,8)
        if (area > 130000):
            if save:
                return [0]
            return 0
        x, y, w, h = cv2.boundingRect(approx)
        # cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 1)
        roImg = gray[max(y - 10, 0):min(y + h + 10, height - 1), max(x - 10, 0):min(x + w + 10, weight - 1)]
        if save:
            roIm=img[max(y - 10, 0):min(y + h + 10, height - 1), max(x - 10, 0):min(x + w + 10, weight - 1)]
        if roImg is None or len(roImg) == 1 or len(roImg) == 0 or len(roImg[0]) == 0:
            if save:
                return [0]
            return 0
        if save or debug:
            cv2.imshow("Box", roImg)
        if save:
            ClassificateByCascade(roImg)
            return roIm
        else:
            return ClassificateByCascade(roImg)
    if save:
        return [0]
    return 0


def preprocess_img(imgBGR, erode_dilate=True):
    """preprocess the image for contour detection.
    Args:
        imgBGR: source image.
        erode_dilate: erode and dilate or not.
    Return:
        img_bin: a binary image (blue and red).

    """
    rows, cols, _ = imgBGR.shape
    imgHSV = cv2.cvtColor(imgBGR, cv2.COLOR_BGR2HSV)

    Bmin = np.array([100, 43, 46])
    Bmax = np.array([124, 255, 255])
    img_Bbin = cv2.inRange(imgHSV, Bmin, Bmax)

    Rmin1 = np.array([0, 43, 46])
    Rmax1 = np.array([10, 255, 255])
    img_Rbin1 = cv2.inRange(imgHSV, Rmin1, Rmax1)

    Rmin2 = np.array([156, 43, 46])
    Rmax2 = np.array([180, 255, 255])
    img_Rbin2 = cv2.inRange(imgHSV, Rmin2, Rmax2)
    img_Rbin = np.maximum(img_Rbin1, img_Rbin2)
    img_bin = np.maximum(img_Bbin, img_Rbin)

    if erode_dilate is True:
        kernelErosion = np.ones((3, 3), np.uint8)
        kernelDilation = np.ones((3, 3), np.uint8)
        img_bin = cv2.erode(img_bin, kernelErosion, iterations=1)
        img_bin = cv2.dilate(img_bin, kernelDilation, iterations=5)

    return img_bin


def ClassificateByCascade(img):
    img = cv2.resize(img, (60, 60))
    allfound = []
    for a in cascades:
        s = cascades[a].detectMultiScale(img)
        for (ex, ey, ew, eh) in s:
            allfound.append([ew * eh, a])
    if len(allfound) == 0:
        return 0

    BigestSing = max(allfound, key=lambda x: x[0])[1]
    print("I found " + BigestSing)
    actionForSing(BigestSing)
    return time.time()


def actionForSing(sing):
    if "advantageSquare" == sing:
        com = "Obgon#"
        print(com)
    elif "advantageRound" == sing:
        com = "Reverse#"
        print(com)
    elif "Stop" == sing:
        com = "Stop#"
        print(com)  # debug
    elif "Road" == sing:
        com = "Road#"
        print(com)
    send2Arduino(com)

kernel = np.ones((5, 5), np.uint8)


def FindSvetofor(img,debug=False):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    tmpImg = cv2.inRange(hsv, (0, 0, 0), (188, 255, 32))
    tmpImg = cv2.morphologyEx(tmpImg, cv2.MORPH_CLOSE, kernel)
    finalImg = cv2.morphologyEx(tmpImg, cv2.MORPH_OPEN, kernel)
    if debug:
        cv2.imshow("SvetoforDetector", finalImg)
    bi, conturs, hierarchy = cv2.findContours(finalImg, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    conturs = sorted(conturs, key=cv2.contourArea, reverse=True)
    if conturs:
        BigContur = conturs[0]
        approx = cv2.approxPolyDP(BigContur, cv2.arcLength(BigContur, True) * 0.03, True)
        area = abs(cv2.contourArea(BigContur))
        if (area < 700 or area > 130000 or not cv2.isContourConvex(approx)):
            return 0
        x, y, w, h = cv2.boundingRect(approx)
        # cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 1)
        roSvet = hsv[y:y + h, x:x + w]
        print(w/h)
        if roSvet is None or w < 30 or len(approx) != 4 or not (round(w/h,1)==0.5 or round(w/h,1)==0.6 or round(w/h,1)==0.7 or round(w/h,1)==0.8 or round(w/h,1)==0.9) :
            return 0 
        if debug:
            cv2.imshow("FoundSvetBox", roSvet)
        return classificateSvetCollor(roSvet)
    return 0


def classificateSvetCollor(img,debug=False):
    img = cv2.resize(img, (60, 120))
    v = img[:, :, 2]
    if debug:
        cv2.imshow("v", v)
        cv2.imshow("red", v[10:40, 15:44])
        cv2.imshow("yellow", v[40:74, 15:44])
        cv2.imshow("green", v[75:110, 15:44])
    red_sum = np.sum(v[10:40, 15:44])
    yellow_sum = np.sum(v[40:74, 15:44])
    green_sum = np.sum(v[75:110, 15:44])
    maxCol = max(red_sum, max(yellow_sum, green_sum))
    print(maxCol)
    if maxCol < 10000:
        return 0
    if maxCol == red_sum:
        com = "Light*1#"
    elif maxCol == yellow_sum:
        com = "Light*3#"
    elif maxCol == green_sum:
        com = "Light*2#"
    print(com)  # debug
    send2Arduino(com)
    return time.time()


imgCount = 0
# main
debug=False
save=False
lastTime=0
lastTrafficTime=0
#send2Arduino("Start#")
send2Arduino("Start#")
startTime=time.time()
if save:
    roIm=[]
else:
    roIm=0
started=0
#time.sleep(15)
#send2Arduino("Start#")
while True:
    try:
        if not started and time.time()-startTime>15:
            print("I_AM_READY")
            send2Arduino("Start#")
            started=1
        ret, img = cap.read()
        img1 = img[:300, 150:]
        cv2.imshow("InputVideo", img1)
        img2 = img[:300, 300:]
        #cv2.imshow("InputVideo2", img2)
        #img3= img[50:300, 250:600]
        #img3=cv2.cvtColor(img3,BGR2GRAY)
        if (started):
            if time.time()-lastTrafficTime>1:
                lastTrafficTime = FindSvetofor(img2,debug)
            if time.time()-lastTime>4 or save:
                roIm=FindSingBox(img1,debug,save)
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
