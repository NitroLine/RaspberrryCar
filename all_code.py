import cv2 # импортироем opencv
import numpy as np # импортироем модуль numpy для работы с многомерными массивами
import time  # импортироем модуль для работы со временм

kernel = np.ones((5, 5), np.uint8)

def classificateSvetCollor(img,debug=False):
    img = cv2.resize(img, (60, 120)) # приветсти размер картикнки img к 60 на 120 пикселей
    v = img[:, :, 2] # делаем срез у картнки ( вроде как мы берём у неё яркость)
    if debug:
        cv2.imshow("v", v)
        cv2.imshow("red", v[10:40, 15:44])
        cv2.imshow("yellow", v[40:74, 15:44])
        cv2.imshow("green", v[75:110, 15:44])
    red_sum = np.sum(v[10:40, 15:44]) # суммируем яркость на кусочке изображение где красный свет
    yellow_sum = np.sum(v[40:74, 15:44]) # суммируем яркость на кусочке изображение где жёлтый свет
    green_sum = np.sum(v[75:110, 15:44]) # суммируем яркость на кусочке изображение где зелёный свет
    maxCol = max(red_sum, max(yellow_sum, green_sum)) # выбираем максимальную сумму
    print(maxCol)
    if maxCol < 10000: # проверим что яркости достаточно
        return 0
    if maxCol == red_sum:  # находим какой именно цвет окзался максимальным
        com = "Light*1#"
    elif maxCol == yellow_sum:
        com = "Light*3#"
    elif maxCol == green_sum:
        com = "Light*2#"
    print(com)  # debug
    #send2Arduino(com) # отправка на Arduino нужной команды
    return time.time() # возвращаем текущее время, чтобы была возможность не искать светофор в течение какого-то времени

def FindSvetofor(img,debug=False):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV) # перевродим картинку img в hsv формат ( вроде 16-ричные цвета, но это не точно) )
    tmpImg = cv2.inRange(hsv, (0, 0, 0), (188, 255, 32)) # выбраем писксили подходящие под фильтр чёрного цвета, в результате получится картинка, где подходяшиие пиксили белые(255), а те что не вошли в заданный диапаозон - чёрные(0)
    tmpImg = cv2.morphologyEx(tmpImg, cv2.MORPH_CLOSE, kernel) # убираем шумы
    finalImg = cv2.morphologyEx(tmpImg, cv2.MORPH_OPEN, kernel) # убираем шумы
    if debug:
        cv2.imshow("SvetoforDetector", finalImg) # можно вывести получившуюся после обработки картинку на экран
    conturs, hierarchy = cv2.findContours(finalImg, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE) # находим все контуры на получившимся finalImg
    conturs = sorted(conturs, key=cv2.contourArea, reverse=True) # сортируем все контуры по площади
    if conturs: # проверяем нашлись ли контуры
        BigContur = conturs[0] # берём самый большой контур
        approx = cv2.approxPolyDP(BigContur, cv2.arcLength(BigContur, True) * 0.03, True) # находит все углы у контура, возвращая их массивом => можно проверить количество углов len(approx)
        area = abs(cv2.contourArea(BigContur)) # счиатем площать контура
        #cv2.drawContours(img, conturs, 0, (255, 0, 255), 3) # можно нарисовать контур на исходной картике. НО при этом надо учитывать, что мы будем рисовать на подданной нам картике, не копируя её, а значит и вне функции она будет изрисована, плсле выполнения функции
        #cv2.polylines(img,  approx,  True,  (0, 255, 0),  2,8)
        #cv2.imshow("Svetofor Konturs", img)
        if (area < 700 or area > 130000 or not cv2.isContourConvex(approx)): # проверям что площадь не слишком маленькая и не слишком большая. Также проверяем что контур замкнутый
            return 0
        x, y, w, h = cv2.boundingRect(approx) # вычисляем координаты, высоту и ширину прямоугольника, в котором лежит контур
        #cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 1)
        #cv2.imshow("Rectangle", img)
        roSvet = hsv[y:y + h, x:x + w] # вырезаем из картики этот прямоугольник по найденным кооринатам
        #print(w/h)
        # проверям что прямоугольник нашёлся, он не слишком узкий, количество углов у него ровно 4, и соотношение его сторон 0,5 или 0,6 или 0,7 или 0,8 или 0,9 (оно не всегда 0.5 тк зависит от перспективы)
        if roSvet is None or w < 30 or len(approx) != 4 or not (round(w/h,1)==0.5 or round(w/h,1)==0.6 or round(w/h,1)==0.7 or round(w/h,1)==0.8 or round(w/h,1)==0.9) :
            return 0
        cv2.imshow("FoundSvetBox", roSvet) # вывод на экран получившегося прямоугольника
        return classificateSvetCollor(roSvet) # вызывем функцию для узнавания цвета на вырезанной области
    return 0


files = ['stopgitCas.xml', 'roadCas.xml', 'preim2.6Znak2.xml', 'preim2.7Znak4.xml'] # список имён файлов, с каскадами
nameSing = ["Stop", "Road", "advantageRound", "advantageSquare"] # названия каскадов
cascades = dict() # создаём словарь, где будем хранить по названию каскадов сами открыте файлы
for i in range(len(files)):
    cascades[nameSing[i]] = cv2.CascadeClassifier(files[i]) # открываем соответствующий файл


def classificate_by_cascade(img):
    img = cv2.resize(img, (60, 60)) # приветсти размер картикнки img к 60 на 60 пикселей (чем меньше картинка тем быстрее будет поиск, но менее качественно)
    cv2.imshow('resized box',img)
    allfound = [] # список найденного
    for a in cascades: # перебираем названия каскадов из словаря
        s = cascades[a].detectMultiScale(img) # поиск на картинке img, соотвествущим открытым каскадом из словаря. Возвращает список прямоугольников
        for (ex, ey, ew, eh) in s: # перебираем все прямоугольники ( у них берём координаты и высоту с шириной)
            allfound.append([ew * eh, a]) # добавляем в список найденного площадь прямоугольика и имя каскада, который его нашёл
    if len(allfound) == 0: # проверям что хоть что-то нашлось
        return 0

    BigestSing = max(allfound, key=lambda x: x[0])[1] # выбираем самый большой прямоугольник по площади и берём название каскада, который его нашёл. Это и будет найденным знаком
    print("I found " + BigestSing) #
    #actionForSing(BigestSing) # делаем какое-то действие в зависимости от знака (отправляем соответсвующую команду на arduino)
    return time.time() # возвращаем текущее время, чтобы была возможность не искать знак в течение какого-то времени (так у нас время отъехать от знака после рекции на него)


def FindSingBox(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # ковертируем картинку img в чёрно-белый формат и сорхрняем результат в переменную gray
    height, weight = gray.shape # берём высоту и ширину картинки
    finalImg = preprocess_img(img) # делаем обработку картинки нашей функцией
    conturs, hierarchy = cv2.findContours(finalImg, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE) # находим все контуры на получившимся finalImg
    conturs = sorted(conturs, key=cv2.contourArea, reverse=True) # сортируем все контуры по площади
    if conturs: # проверяем нашлись ли контуры
        BigContur = conturs[0] # берём самый большой контур
        approx = cv2.approxPolyDP(BigContur, cv2.arcLength(BigContur, True) * 0.03, True) # находит все углы у контура, возвращая их массивом => можно проверить количество углов len(approx)
        area = abs(cv2.contourArea(BigContur)) # счиатем площать контура
        # debug
        #cv2.drawContours(img,conturs,0,(255,0,255),3)
        #cv2.polylines(img,  approx,  True,  (0, 255, 0),  2,8)
        if (area > 130000): # проверям что площадь не слишком маленькая
            return 0
        x, y, w, h = cv2.boundingRect(approx) # вычисляем координаты, высоту и ширину прямоугольника, в котором лежит контур
        #cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 1) # можно нарисовать прямоугольник на исходной картике. НО при этом надо учитывать, что мы будем рисовать на подданной нам картике, не копируя её, а значит и вне функции она будет изрисована, плсле выполнения функции
        #cv2.imshow("drowing contur", img)
        roImg = gray[max(y - 10, 0):min(y + h + 10, height - 1), max(x - 10, 0):min(x + w + 10, weight - 1)]   # вырезаем из картики этот прямоугольник по найденным кооринатам, слега увилиивая область на 10 пикселей, чтобы случайно не обрезать часть знака
        # проверям что картинка вырезалась нормально
        if roImg is None or len(roImg) == 1 or len(roImg) == 0 or len(roImg[0]) == 0:
            return 0
        cv2.imshow("Box", roImg) # вывод на экран получившегося прямоугольника
        return classificate_by_cascade(roImg) # вызывем функцию для узнавания знака на вырезанной области
    return 0


def preprocess_img(imgBGR, erode_dilate=True):
    """preprocess the image for contour detection.
    Args:
        imgBGR: source image.
        erode_dilate: erode and dilate or not.
    Return:
        img_bin: a binary image (blue and red).

    """
    imgHSV = cv2.cvtColor(imgBGR, cv2.COLOR_BGR2HSV) # перевродим картинку img в hsv формат ( вроде 16-ричные цвета, но это не точно =) )
    #cv2.imshow('HSV', imgHSV)

    Bmin = np.array([100, 43, 46])
    Bmax = np.array([124, 255, 255])
    img_Bbin = cv2.inRange(imgHSV, Bmin, Bmax) # выбраем писксили подходящие под фильтр синего цвета, в результате получится картинка, где подходяшиие пиксили белые(255), а те что не вошли в заданный диапаозон - чёрные(0)
    #cv2.imshow('Bin Blue', img_Bbin)

    Rmin1 = np.array([0, 43, 46])
    Rmax1 = np.array([10, 255, 255])
    img_Rbin1 = cv2.inRange(imgHSV, Rmin1, Rmax1) # выбраем писксили подходящие под фильтр красного цвета, в результате получится картинка, где подходяшиие пиксили белые(255), а те что не вошли в заданный диапаозон - чёрные(0)
    #cv2.imshow('Bin Red', img_Rbin1)

    Rmin2 = np.array([156, 43, 46])
    Rmax2 = np.array([180, 255, 255])
    img_Rbin2 = cv2.inRange(imgHSV, Rmin2, Rmax2) # # выбраем писксили подходящие под фильтр розового (почему бы и нет) цвета, в результате получится картинка, где подходяшиие пиксили белые(255), а те что не вошли в заданный диапаозон - чёрные(0)
    #cv2.imshow('Bin Red2 Pink', img_Rbin2)

    img_Rbin = np.maximum(img_Rbin1, img_Rbin2) # совмещаем отфильтрованные картники, путём выбрания максимума для каждого пикселя
    img_bin = np.maximum(img_Bbin, img_Rbin) # совмещаем отфильтрованные картники, путём выбрания максимума для каждого пикселя

    #cv2.imshow('Maximum bin result', img_bin)
    if erode_dilate is True:
        kernelErosion = np.ones((3, 3), np.uint8)
        kernelDilation = np.ones((3, 3), np.uint8)
        img_bin = cv2.erode(img_bin, kernelErosion, iterations=2) # убираем шумы, удаляя слишком маленькие области
        #cv2.imshow('Image after erode', img_bin)

        img_bin = cv2.dilate(img_bin, kernelDilation, iterations=4) # нарщиваем отсавшиеся областти, чтобы случайно не сломать контур полсе убирания шумов
        #cv2.imshow('Image after dilate', img_bin)
    return img_bin



cap = cv2.VideoCapture(0) # иницируем камеру с индексом 0
while True:
    ret, img = cap.read()  # читаем кадр
    cv2.imshow("CAMERA", img) # выводим кадр

    #result = preprocess_img(img) # функция для предобработки изображения
    #cv2.imshow("Processed image",result)

    #last = FindSingBox(img) # найти знак
    #cv2.imshow("After Finding Box", img)

    last = FindSvetofor(img) # найти светофор
    cv2.imshow("After Finding Svetofor", img)

    k = cv2.waitKey(30) & 0xff # проверяем какая клавиша нажата
    if k == 27:  # если была нажата 'ESC' (у неё код 27) то выйти из бесконечного цикла
        break

cap.release() # отключиться от камеры
cv2.destroyAllWindows() # закрыть все окна
