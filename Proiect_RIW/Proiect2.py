import http.client
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import socket
import datetime
import os
import dns
##########################################################################
########################### VARIABLES ####################################
##########################################################################
Q = ["http://riweb.tibeica.com/crawl/"]
my_var = 0
##########################################################################
########################### FUNCTIONS ####################################
##########################################################################
def isabsolute(url):
    return bool(urlparse(url).netloc)

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
def extract_html_page(url,domain):
    target_host2 = urlparse(url).netloc
    if not (os.path.isdir(os.path.join('work_directory',domain))):
        os.mkdir(os.path.join('work_directory',domain))
    client = "RIWEB_CRAWLER"
    target_port = 80  # create a socket object
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # connect the client
    client.connect((domain, target_port))
    # send some data
    request = "GET {} HTTP/1.1\r\nHost: {}\r\nUser-Agent: {}\r\n\r\n".format(url, domain, client)

    client.send(request.encode())
    # =========================Read step by step===============================
    CHUNK_SIZE = 36  # you can set it larger or smaller
    lines = []
    buffer = bytearray()
    buffer.extend(client.recv(CHUNK_SIZE))
    firstline = buffer[:buffer.find(b'\n')]
    firstline = buffer.decode()
    data = b''
    #print(target_host)
    #print(buffer)
    if '200 OK' in firstline:
        data = recvall(client)
        data = buffer + data
        data = data.decode()
        data_to_store = data[data.find('\r\n\r\n'):]
        #client.close()
        return data_to_store
    else:
        print(firstline)
        print(domain+url)
        data = data + buffer
        data += recvall(client)
        with open('error_page.txt', 'w') as file:
            file.write(data.decode())
        pass
        #client.close()
def crawler():
    counter = 0
    for L in Q:
        #print(L)
        domain = urlparse(L).netloc
        url = urlparse(L).path
        #print(url)
        P = extract_html_page(url,domain)
        if P is not None:
            getpage_soup = BeautifulSoup(P, 'html.parser')
            metas = getpage_soup.find_all('meta')
            permission1 = False
            permission2 = False
            break_activated = False
            for meta in metas:
                if meta.get('name') == 'robots':
                    if meta.get('content') == 'all' or meta.get('content') == 'index':
                        permission1 = True

                    if meta.get('content') == 'all' or meta.get('content') == 'follow':
                        permission2 = True
            if not any(meta.get('name') == 'robots' for meta in metas):
                permission1, permission2 = True, True
            if permission1 == True:
                path = L.split('http://')[1]
                path = path.split('/')
                current_path = os.path.join(os.getcwd(),'work_directory')
                for var in path[:-1]:
                    if (os.path.isdir(os.path.join(current_path,var))):
                        current_path = os.path.join(current_path,var)
                    else:
                        current_path = os.path.join(current_path,var)
                        os.mkdir(current_path)
                if path[-1] == '':
                    nume_fisier = 'index.html'
                else:
                    nume_fisier = path[-1]
                with open('{}\{}.html'.format(current_path,nume_fisier.split('.')[0]), 'wb') as file:
                    file.write(P.encode('utf8'))
            if permission2 == True:
                a_tags = getpage_soup.find_all('a',href = True)
                for a_tag in a_tags:
                    link = a_tag['href']
                    if isabsolute(link):
                        if link[:link.find(':')] == 'http' or link[:link.find(':')] == 'https':
                            link = link.split('#')[0]
                            if link not in Q:
                                Q.append(link)
                    else:
                        link = link.split('#')[0]
                        if '.' in L.split('/')[-1]:
                            #print('Da')
                            L = L.replace(L.split('/')[-1],'')
                        if L[-1] != '/':
                            L += '/'
                        #print(L)
                        link = L + link
                        if link not in Q:
                            Q.append(link)
    print(len(Q))
    print(Q)
if __name__ == "__main__":
    start_time = datetime.datetime.now()
    crawler()
    print('A durat:', str(datetime.datetime.now() - start_time))