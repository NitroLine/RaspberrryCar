import numpy as np
import cv2
cas = cv2.CascadeClassifier('svetCas3.xml')
cap = cv2.VideoCapture(0)
i=0
while True:
    ret, img = cap.read()  # читаем кадр
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = cas.detectMultiScale(gray)
    for (x, y, w, h) in faces:
        img = cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
    cv2.imshow("Img",img)
    k = cv2.waitKey(30) & 0xff
    if k==114:
        print("Save!")
        cv2.imwrite(str(i)+"ff.jpg",img)
        i+=1
    if k == 27:  # press 'ESC' to quit
        break

cap.release()  # close all windows
cv2.destroyAllWindows()
