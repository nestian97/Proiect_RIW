import socket
import gc
target_host = "http://riweb.tibeica.com/crawl/"
target_host2 = "riweb.tibeica.com"
client = "CLIENT RIW"
target_port = 80  # create a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect the client
client.connect((target_host2, target_port))

# send some data
request = "GET {}/ HTTP/1.1\r\nHost: {}\r\nUser-Agent: {}\r\n\r\n".format(target_host,target_host2,client)

client.send(request.encode())


#=========================Function for receiving data===========================
def recvall(sock):
    BUFF_SIZE = 4096 # 4 KiB
    data = b''
    while True:
        part = sock.recv(BUFF_SIZE)
        print(len(part))
        data += part
        if  b'</html>' in part.lower() or len(part) == 0:
            break
    return data


#=========================Read step by step===============================
CHUNK_SIZE = 32  # you can set it larger or smaller
lines = []
buffer = bytearray()
buffer.extend(client.recv(CHUNK_SIZE))
firstline = buffer[:buffer.find(b'\n')]
firstline = buffer.decode()
data = b''
if '200 OK' in firstline:
    data = recvall(client)
    data=data.decode()
    data_lower = data.lower()
    #print(data_lower.find('<!doctype'))
    if data_lower.find('<!doctype') > -1:
        data_to_store = data[data_lower.find('<!doctype'):data_lower.find('</html>') + 8]
    else:
        data_to_store = data[data_lower.find('<html'):data_lower.find('</html>') + 8]
    with open('my_page.html','w') as file:
        print(data_to_store)
        file.write(data_to_store)
else:
    data = data + buffer
    data +=recvall(client)
    with open('error_page.txt','w') as file:
        file.write(data.decode())
    pass