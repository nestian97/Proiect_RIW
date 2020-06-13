import socket
import random
import time
import sys
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
to_send = ("81.180.223.1",53)
s.connect(to_send)
adress = s.getsockname()[0]
print(adress)
s.close()
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

adress = socket.getaddrinfo("81.180.223.1",53)
print(adress)
#sys.exit(1)
mesaj = bytearray(31)
mesaj[1] = (0xFF) & (random.randint(0,254)+1)
mesaj[5] = 1
domeniu = "www.tuiasi.ro"
labels = domeniu.split('.')
idx = 12
for i in range(len(labels)):
    tmp = len(labels[i])
    mesaj[idx] = tmp & 0xFF
    idx += 1
    for j in range(tmp):
        mesaj[idx] = ord(labels[i][j])
        idx += 1
mesaj[idx] = 0
mesaj[30]=mesaj[28] = 1
mesaj_hex = []
for elem in mesaj:
    mesaj_hex.append(hex(elem))
packet = (mesaj, adress)
print(s.sendto(mesaj, (to_send)))
#time.sleep(3)
response = s.recv(512)
hex_array = []
for elem in response:
    hex_array.append(hex(elem))
if int(hex_array[3],0) & 0x0F != 0:
    print('Eroare, codul erorii este: ',hex_array[3])
for x in range(len(hex_array)):
    pass
print(hex_array)
print(mesaj_hex)
#s.close()