import numpy as np
import cv2
import os

def nothimg(x):
    pass

cv2.namedWindow("Result")
cap = cv2.VideoCapture(0)  # объявляем камеру под номером 0 в переменную cap


cv2.createTrackbar("Trash1", "Result", 0, 10000, nothimg)
cv2.createTrackbar("Trash2", "Result", 0, 10000, nothimg)
cv2.createTrackbar("edges", "Result", 0, 10000, nothimg)

while True:
    flag, img = cap.read()  # захват кадра flag - успешность захвата кадра, img - кадр, как массив пикселей
    #img=cv2.imread("25.jpg",cv2.IMREAD_GRAYSCALE)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # перевод картинки в шестнадцатиричные цвета
    cv2.imshow("InputImg", gray)
    tr1 = cv2.getTrackbarPos("Trash1", "Result")
    tr2 = cv2.getTrackbarPos("Trash2", "Result")
    cany = cv2.getTrackbarPos("edges", "Result")
    gray=cv2.Canny(gray,tr1,tr2,cany)
    cv2.imshow("result", gray)
    ch = cv2.waitKey(5)  # ожидание кнопки для закрытия P.S. не помню какая кнопка, но ESC работает
    if ch == 27:
        break

cap.release()  # завершение чтения кадров
cv2.destroyAllWindows()  # закрытие всех окон
