import cv2
import os
import xml.etree.ElementTree as pars
dir = "C:\\Users\\miner\\\OneDrive\\Desktop\\CarSee\\image_svetofor"
ImageDir = os.listdir(dir+"\\image")  # получаем лист названий картинок с расширением
AnotDir = os.listdir(dir+"\\annotation")  # получаем лист названий анотация с разрешениями
AllDirList = []
kostil=0
for i in range(170):  # объединяем названия картинок и анатация для удобства
    AllDirList.append([ImageDir[i], AnotDir[i-kostil]])
AllDirList=sorted(AllDirList,key=lambda x:x[0])
AllDirList=AllDirList[len(AllDirList)-3:]
for nameFl in AllDirList:
    img=cv2.imread(dir+"\\image\\"+nameFl[0],cv2.IMREAD_COLOR)
    Tree = pars.parse(dir + "\\annotation\\" + nameFl[1])  # загружаем анатацию(она в виде дерева типо)
    root = Tree.getroot()  # получаем корень данного дерева
    i=1
    for objects in root.findall("object"):
        bnx = objects.find("bndbox")  # получаем координаты
        x = int(bnx.find("xmin").text)
        y = int(bnx.find("ymin").text)
        x2 = int(bnx.find("xmax").text)
        y2 = int(bnx.find("ymax").text)
        print(nameFl)
        roImg=img[y:y2,x:x2]
        cv2.imwrite("res\\"+str(i)+"_"+nameFl[0],roImg)
        i+=1
print("READY!")