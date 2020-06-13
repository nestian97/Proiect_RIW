import socket
import random
import time
import dns.query

to_send = ("{}".format("8.8.8.8"),53)
def DNS (domain):
    ip_adr = socket.gethostbyname("8.8.8.8")
    print(ip_adr)
    #ip_adr = socket.gethostbyname_ex(domain)
    print(ip_adr)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    mesaj = bytearray()
    mesaj.extend()
    mesaj[1] = (0xFF) & (random.randint(0, 254) + 1)
    mesaj[5] = 1
    #domeniu = "www.tuiasi.ro"
    labels = domain.split('.')
    idx = 12
    for i in range(len(labels)):
        tmp = len(labels[i])
        mesaj[idx] = tmp & 0xFF
        idx += 1
        for j in range(tmp):
            mesaj[idx] = ord(labels[i][j])
            idx += 1
    mesaj[idx] = 0
    mesaj[30] = mesaj[28] = 1
    mesaj_hex = []
    for elem in mesaj:
        mesaj_hex.append(hex(elem))
    print(s.sendto(mesaj, (to_send)))
    #time.sleep(3)
    print('Aici')
    response = s.recv(512)
    hex_array = []
    for elem in response:
        hex_array.append(hex(elem))
    print(hex_array)
    return ip_adr
DNS('www.tuiasi.ro')