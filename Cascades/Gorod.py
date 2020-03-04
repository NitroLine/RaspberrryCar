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
def distance(x1, y1, x2, y2):
	return (x1-x2)**2 + (y1 - y2)**2

def detect3xCircle(gray, frame, debug=True):
	detected_circles = cv2.HoughCircles(gray,  
	               cv2.HOUGH_GRADIENT, 1, 20, param1 = 40, 
	           param2 = 30, minRadius = 10, maxRadius = 30) 
	tmp = []
	if (detected_circles is not None):
		detected_circles = np.uint16(np.around(detected_circles))

		for (x1, y1, r1) in detected_circles[0, :]:
			tmp = []
			cv2.circle(frame, (x1, y1), r1, (0, 0, 255), 3)
			tmp.append((x1, y1, r1))
			for (x2, y2, r2) in detected_circles[0, :]:
				if (x1 == x2 and y1 == y2 and r1 == r2):
					continue
				cv2.circle(frame, (x2, y2), r2, (0, 0, 255), 3)
				if (distance(x1,y1, x2, y2) <= 12000):
					tmp.append((x2,y2, r2))
				if (len(tmp) == 3):
					break
			if (len(tmp) == 3):
				break

		if (debug):
			print("Lenght 3x-circle: {}".format(len(tmp)))

	return (frame, tmp)


def clasificateCirlce(frame, debug=True):
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	gray = cv2.blur(gray, (3, 3))

	frame, circles = detect3xCircle(gray, frame)

	if (len(circles) == 3):
		circles = sorted(circles, key=lambda x:x[1])
		
		for ind in range(3):
			x, y, r = circles[ind]
			blue, green, red = frame[y-1][x-1][0], frame[y-1][x-1][1], frame[y-1][x-1][2]

			if (ind == 0): # red color
				print("reds--> {}, {}, {}".format(red, green, blue))
				if (red >= 200 and green >= 20 and blue >= 20):
					cv2.circle(frame, (x, y), 1, (255, 0, 0), 2)
					print("RED FOUND")
					break
			elif (ind == 1): # yellow color
				print("yellow--> {}, {}, {}".format(red, green, blue))
				if (red >= 200 and green >= 200 and blue >= 20):
					cv2.circle(frame, (x, y), 1, (255, 0, 0), 2)
					print("YELLOW FOUND")
					break
			else:
				print("green--> {}, {}, {}".format(red, green, blue))
				if (red >= 20 and green >= 190 and blue >= 0):
					cv2.circle(frame, (x, y), 1, (255, 0, 0), 2)
					print("GREEN FOUND")
					break
	if (debug):	
		cv2.imshow("Detected Circle", frame) 


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
        if debug:
            cv2.imshow("Box", roImg)
        if save:
            cv2.imshow("Box", roImg)
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
        img_bin = cv2.erode(img_bin, kernelErosion, iterations=2)
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
        print(area)
        if (area < 1500 or area > 15000 or not cv2.isContourConvex(approx)):
            return 0
        x, y, w, h = cv2.boundingRect(approx)
        # cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 1)
        roSvet = hsv[y:y + h, x:x + w]
        print("Weight: " + str(w))
        print(w/h)
        if roSvet is None or w < 30 or len(approx) != 4 or not (round(w/h,1)==0.5 or round(w/h,1)==0.6 or round(w/h,1)==0.7 or round(w/h,1)==0.8) :
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
    print("Founded maximum color:" +str(maxCol))
    if maxCol < 20000:
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
        roFrame = img[:300, 350:]
        #cv2.imshow("InputVideo", img)
        if (started):
            if time.time()-lastTrafficTime>1:
                clasificateCirlce(roFrame)
                # lastTrafficTime = FindSvetofor(roFrame,False)
            #if time.time()-lastTime>6 or save:
            #    roIm=FindSingBox(roFrame,debug,save)
            
            #img,x,View = Lin.CheckLine(img,x,View)
            x=line2FindLine(img,minold,View,debug)
            print(x)
            if (x==640 and minold!=640):
                kkk+=1
                x=minold
                if (kkk>0):
                    print("Not autocontrast")
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
