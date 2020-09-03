# python color_tracking.py

# import the necessary packages
from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time
import heapq
import socket
import struct
from pynput.keyboard import Key, Controller
import time

# Range de cores a menor e a maior
greenLower = (29, 86, 6)
greenUpper = (64, 255, 255)

pts = deque(maxlen=2)

vs = VideoStream(src=0).start()
keyboard = Controller()
# configura as coisas para enviar os dados via socket UDP
# se quiser testar sem utilizar unity pode usar este servidor aqui: https://github.com/ezefranca/socket-demo

UDP_IP = "127.0.0.1"
UDP_PORT = 5065
udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
destination = (UDP_IP, UDP_PORT)

# Um delay para camera começar
time.sleep(2.5)

# Loop
while True:

	frame = vs.read()

	if frame is None:
		break

	# Redimensiona e flipa o frame atual e aplica um filtro Gaussiano
	frame = imutils.resize(frame, width=600)
	frame = cv2.flip(frame, 1)
	blurred = cv2.GaussianBlur(frame, (11, 11), 0)
	hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

	# Aqui a mágica acontece, é feita uma máscara para a cor "verde" e, em seguida, executar dilatações e erosões para remover manchas

	mask = cv2.inRange(hsv, greenLower, greenUpper)
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)


	# Encontra os contornos na máscara e inicializa o ponto central
	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
	center1 = None
	center2 = None

	# Só continua se tiver ao menos 2 pq senão não tem como calcular o angulo
	if len(cnts) > 2:
		# Digamos que temos vários pontos, vamos pegar aqui os dois maiores e criar um circulo no centro

		sensors = cnts

		# Função super marota que retorna os n maiores de uma lista (n = 2 neste caso) o parametro key é o que é maior, num objeto podemos escolher uma propriedade
		sensors_selected = heapq.nlargest(2, sensors, key=cv2.contourArea)

		c1 = sensors_selected[0]
		c2 = sensors_selected[1]

		((x, y), radius1) = cv2.minEnclosingCircle(c1)
		M = cv2.moments(c1)
		center1 = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

		# Se for menor que n (neste caso 10) o raio do circulo nem considero pois pode ser mancha (esse valor 5 pode ser ajustado depois)
		if radius1 > 5:
			# Desenha o circulo do primeiro
			cv2.circle(frame, (int(x), int(y)), int(radius1),
				(0, 255, 255), 2)
			cv2.circle(frame, center1, 5, (0, 255, 255), -1)

		((x, y), radius2) = cv2.minEnclosingCircle(c2)
		M = cv2.moments(c2)
		center2 = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

		# Mesma coisa ali de cima
		if radius2 > 5:
			# Desenha o circulo do segundo
			cv2.circle(frame, (int(x), int(y)), int(radius2),
				(0, 255, 255), 2)
			cv2.circle(frame, center2, 5, (0, 255, 255), -1)

		# desenho uma linha do centro de um circulo no outro
		cv2.line(frame, center1, center2, (0, 0, 255), 5)

		# calculo do angulo entre o centro1 e o centro2

		unit_vector_1 = (abs(center1[0] - center2[0]), abs(center1[1] - center2[1]))
		# unit_vector_2 = (0 , 10)
		#
		# print(unit_vector_1)
		#
		# # unit_vector_1 = center1 / np.linalg.norm(center1)
		# # unit_vector_2 = center2 / np.linalg.norm(center2)
		# dot_product = np.dot(unit_vector_1, unit_vector_2)
		#
		# angleRad = np.arccos(dot_product)
		# angleDeg = np.degrees([angleRad])

		# send = str(unit_vector_1[0] + "")
		# Envia o Angulo via UDP
		x1 = center1[0] - center2[0]
		y1 = center1[1] - center2[1]

		v1 = (x1, y1)
		v2 = (1, 0)
		angle = np.dot (v1 , v2)

		if (angle > -10) and (angle < 10):
			print('stop')
			keyboard.release ( Key.left )
			keyboard.release ( Key.right )
		elif angle > 10:
			print('right')
			keyboard.press ( Key.right )
			time.sleep ( 0.01 )
		elif angle < -10:
			print('left')
			keyboard.press ( Key.left )
			time.sleep ( 0.01 )

		angle_struct = struct.pack('!ii', x1, y1)
		# Notice the ! sign for network endianness.

		udp.sendto(angle_struct , destination)
		# udp.sendto(str(unit_vector_1).encode(), destination)

		# Um debug do angulo na tela (não use sempre pq deixa as coisas lentas pra caramba)

		# font = cv2.FONT_HERSHEY_SIMPLEX
		# bottomLeftCornerOfText = (10, 300)
		# fontScale = 1
		# fontColor = (255, 255, 255)
		# lineType = 2
		#
		# cv2.putText(frame, 'Angulo: ' + str(angle),
		# 			bottomLeftCornerOfText,
		# 			font,
		# 			fontScale,
		# 			fontColor,
		# 			lineType)

	# Uma linha branca para debug
	cv2.line(frame, center1, center2, (255, 255, 255), 1)


	# Atualiza a lista dos pontos (pra se quiser enviar no UDP também)
	pts.appendleft(center1)
	pts.appendleft(center2)

	# Mostra na tela
	cv2.imshow("Frame", frame)

	# Se digitar q ele mata sai do loop While
	key = cv2.waitKey(1) & 0xFF
	if key == ord("q"):
		break

# libera a camera
vs.release()

# fecha a conexão UDP
udp.close()

# fecha todas janelas
cv2.destroyAllWindows()