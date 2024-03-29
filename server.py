import socket
import pickle
import cv2
import numpy as np
import struct

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Socket created")

s.bind(('192.168.43.121', 8888))
print("Socket bind complete")

s.listen(10)
print("Socket now listening")

conn, addr = s.accept()

data = b""
payload_size = struct.calcsize(">L")
print("payload_size: {}".format(payload_size))

while True:
	while len(data) < payload_size:
		print("Recv: {}".format(len(data)))
		data += conn.recv(4096)

	print("Done recv: {}".format(len(data)))
	packed_msg_size = data[:payload_size]
	data = data[payload_size:]

	msg_size = struct.unpack(">L", packed_msg_size)[0]
	print("msg_size: {}".format(msg_size))
	while len(data) < msg_size:
		data += conn.recv(4096)

	frame_data = data[:msg_size]
	data = data[msg_size:]

	frame = pickle.loads(frame_data, fix_imports=True, encoding="bytes")
	frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

	conn.sendall(b"Line*450#")

	cv2.imshow("Image", frame)
	cv2.waitKey(1)

# nparr = np.fromstring(img_str, np.uint8)
# img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
# cv2.imwrite("result.jpeg", img)		

