import socket
from header import coada_de_explorare, Q
import codecs


# =========================Function for receiving data===========================
def recvall(sock):
    BUFF_SIZE = 4096  # 4 KiB
    data = b''
    while True:
        part = sock.recv(BUFF_SIZE)
        data += part
        if b'</html>' in part.lower() or len(part) == 0:
            break
    return data


def extract_html_page(url, domain, ip, adress):
    nume = "RIWEB_CRAWLER"
    target_port = 80  # create a socket object
    dec = codecs.getincrementaldecoder('utf8')()
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect the client
    try:
        client.connect((ip, target_port))
    except Exception as e:
        print(e, 'La connect')
        print(adress,'  ',ip)
        return
    client.settimeout(19)
    # send some data
    request = "GET {} HTTP/1.1\r\nHost: {}\r\nUser-Agent: {}\r\n\r\n".format(url, domain, nume)
    # print('Ajunge')
    client.send(request.encode())
    # =========================Read step by step===============================
    try:
        CHUNK_SIZE = 36  # you can set it larger or smaller
        lines = []
        buffer = bytearray()
        buffer.extend(client.recv(CHUNK_SIZE))
        if len(buffer) == 0:
            return
        buffer = bytes(buffer)
        firstline = buffer[:buffer.find(b'\n')]
        firstline = buffer.decode('utf-8', errors="ignore")
        data = b''
        # print(target_host)
        # print(buffer)
        if '200 OK' in firstline:
            data = recvall(client)
            # print(bytes(buffer))
            # print(data)
            # sys.exit(1)
            data = buffer + data
            data = data.decode('utf-8', errors="ignore")
            data_to_store = data[data.find('\r\n\r\n'):]
            coada_de_explorare[adress]['explorat'] = True
            client.close()
            return data_to_store
        else:
            data = data + buffer
            data += recvall(client)

            if '301' in firstline:
                check_301_status(data.decode('utf-8', errors="ignore"), adress)
            if '307' in firstline:
                check_307_status(data.decode('utf-8', errors="ignore"), adress)
            if '302' in firstline:
                check_302_status(data.decode('utf-8', errors="ignore"), adress)
            for nr in ['500','501','502','503','504','505','506','507','508','510','511']:
                if nr in firstline:
                    check_5xx_status(adress)
                    client.close()
                    return None

            client.close()
            return None
            # client.close()
    except Exception as e:
        client.close()
        print(e, domain, ':::::raspuns')
        print(domain+url)
        if 'timed out' in str(e):
            for link in Q:
                if domain in link:
                    Q.remove(link)

        pass


def check_301_status(data, adress):
    for header in data.split('\r\n'):
        if 'Location' in header:
            new_location = header.split(': ')[1]
            if coada_de_explorare[adress]['retry'] <= 5:
                coada_de_explorare[adress]['retry'] += 1
                coada_de_explorare[adress]['explorat'] = True
                coada_de_explorare[new_location] = {'explorat': False, 'retry': coada_de_explorare[adress]['retry']}
                Q.append(new_location)
                return
    return

def check_307_status(data, adress):
    for header in data.split('\r\n'):
        if 'Location' in header:
            new_location = header.split(': ')[1]
            if coada_de_explorare[adress]['retry'] < 5:
                coada_de_explorare[adress]['retry'] += 1
                coada_de_explorare[adress]['explorat'] = True
                coada_de_explorare[new_location] = {'explorat': False, 'retry': coada_de_explorare[adress]['retry']}
                Q.append(new_location)
            return
    return

def check_302_status(data, adress):
    for header in data.split('\r\n'):
        if 'Location' in header:
            new_location = header.split(': ')[1]
            if coada_de_explorare[adress]['retry'] < 5:
                coada_de_explorare[adress]['retry'] += 1
                coada_de_explorare[adress]['explorat'] = True
                coada_de_explorare[new_location] = {'explorat': False, 'retry': coada_de_explorare[adress]['retry']}
                Q.append(new_location)
            return
    return


def check_401_status():
    return
def check_404_status():
    return
def check_403_status():
    return
def check_405_status():
    return
def check_5xx_status(data, adress):
    if coada_de_explorare[adress]['retry'] < 5:
        Q.append(adress)
        coada_de_explorare[adress]['retry'] +=1
    else:
        coada_de_explorare[adress]['explorat'] = True

# sys.exit(1)
