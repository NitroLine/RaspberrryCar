import socket
import cv2
import pickle
import struct

client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_sock.connect(('localhost', 8888))
connection = client_sock.makefile('wb')

cap = cv2.VideoCapture(0)

cap.set(3, 320)
cap.set(4, 240)

img_counter = 0

encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

while True:
	ret, frame = cap.read()
	result, frame = cv2.imencode('.jpg', frame, encode_param)

	data = pickle.dumps(frame, 0)
	size = len(data)

	print("{}: {}".format(img_counter, size))
	client_sock.sendall(struct.pack(">L", size) + data)
	img_counter += 1

cap.release()



# 	img_str = cv2.imencode('.jpg', frame)[1].tostring()
	# for i in range(0, len(img_str), 4096):
	# 	send_data = img_str[i:min(i+4096, len(img_str))]
	# 	s.sendall(send_data)
	# s.sendall(b'ENDENDEND')
	# command = s.recv(1024)