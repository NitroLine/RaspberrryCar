import cv2

cap = cv2.VideoCapture(0)
imgCount=0
while True:
	try:
		ret, frame = cap.read()
		cv2.imshow("Input()",frame)
		ch=cv2.waitKey(1)
		if ch == 27:
			break
		if ch == 114:  # press R to save img
			print("Save!")
			cv2.imwrite(str(imgCount) + "_save.jpg", frame)
			imgCount += 1	
	except KeyboardInterrupt:
		break
