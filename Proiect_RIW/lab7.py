import http.client
from bs4 import BeautifulSoup

import socket
Q = ["http://riweb.tibeica.com/crawl/"]
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
def extract_html_page(target_host):
    target_host2 = "riweb.tibeica.com"
    client = "CLIENT RIW"
    target_port = 80  # create a socket object
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect the client
    client.connect((target_host2, target_port))

    # send some data
    request = "GET {}/ HTTP/1.1\r\nHost: {}\r\nUser-Agent: {}\r\n\r\n".format(target_host, target_host2, client)

    client.send(request.encode())



    # =========================Read step by step===============================
    CHUNK_SIZE = 32  # you can set it larger or smaller
    lines = []
    buffer = bytearray()
    buffer.extend(client.recv(CHUNK_SIZE))
    firstline = buffer[:buffer.find(b'\n')]
    firstline = buffer.decode()
    data = b''
    if '200 OK' in firstline:
        data = recvall(client)
        data = data.decode()
        data_lower = data.lower()
        # print(data_lower.find('<!doctype'))
        if data_lower.find('<!doctype') > -1:
            data_to_store = data[data_lower.find('<!doctype'):data_lower.find('</html>') + 8]
        else:
            data_to_store = data[data_lower.find('<html'):data_lower.find('</html>') + 8]
        with open('my_page.html', 'w') as file:
            #print(data_to_store)
            #file.write(data_to_store)
            pass
        return data_to_store
    else:
        data = data + buffer
        data += recvall(client)
        with open('error_page.txt', 'w') as file:
            file.write(data.decode())
        pass
def crawler():
    counter = 0
    for L in Q:
        if counter > 99:
            break
        else:
            counter += 1
        P = extract_html_page(L)
        if P is not None:
            getpage_soup = BeautifulSoup(P, 'html.parser')
            metas = getpage_soup.find_all('meta')
            permission1 = None
            permission2 = None
            break_activated = False
            for meta in metas:
                if meta.get('name') == 'robots':
                    if meta.get('content') == 'all' or meta.get('content') == 'index':
                        permission1 = True
                    else:
                        permission1 = False

                    if meta.get('content') == 'all' or meta.get('content') == 'follow':
                        permission2 = True

                    else:
                        permission2 = False

                if permission1 is not None or permission2 is not None:
                    break_activated = True
                    break
            if break_activated == False:
                permission2 = permission1 = True
            if permission1 == True:
                with open('work_directory\my_page.html', 'w') as file:
                    print(P)
                    file.write(P)
            if permission2 == True:
                pass

if __name__ == "__main__":
    crawler()