import http.client
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import socket
import datetime
import sys
import os
import requests
# noinspection PyUnresolvedReferences
from DNS_From_Internet import DNSCache,DNSServer
# noinspection PyUnresolvedReferences
from HTTPParser import extract_html_page
# noinspection PyUnresolvedReferences
from header import coada_de_explorare,Q
##########################################################################
########################### VARIABLES ####################################
##########################################################################

my_var = 0
adresses_for_domains = {}

##########################################################################
########################### FUNCTIONS ####################################
##########################################################################
def isabsolute(url):
    return bool(urlparse(url).netloc)

# =========================Function for receiving data===========================
def crawler():
    counter = 0
    for L in Q:
        if counter > 1000:
            break
        else:
            counter += 1

        P = None
        domain = urlparse(L).netloc
        url = urlparse(L).path
        baselink = urlparse(L).scheme+ '://' + domain
        if not os.path.isfile(os.path.join('work_directory',domain,'robots.txt')):
            robo = getrobots(baselink)
            with open (os.path.join('work_directory',domain,'robots.txt'),'w') as file:
                file.write(robo)
        else:
            with open(os.path.join('work_directory',domain, 'robots.txt'),'r') as file:
                robo = file.read()
                #print(robo)
        #for line in robo.split('\n'):
        conditii = robo.split('User-agent: *')[1]
        print(conditii)
        sys.exit()
        path = domain+url
        # if path.split('/')[-1] == '':
        #     if os.path.isfile(os.path.join('work_directory',path,'index.html')):
        #         print('Exista1')
        #         continue
        # else:
        #     #print(path)
        #     if os.path.isfile(os.path.join('work_directory',path)):
        #         print('Exista2')
        #         continue
        #print(url)
        if domain not in adresses_for_domains:
            adresses_for_domains[domain] = []
        adresses_for_domains[domain] = DNSCache(domain,adresses_for_domains[domain])
        ip_adr = adresses_for_domains[domain]['ip_address']
        #ip_adr = DNSServer(domain)['ip_address']
        #print(adresses_for_domains)
        if ip_adr is not  None:
            P = extract_html_page(url,domain,ip_adr,L)

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
                    if meta.get('content') == 'noindex' or meta.get('content') == 'nofollow':
                        print('de Asta')
            if not any(meta.get('name') == 'robots' for meta in metas):
                permission1, permission2 = True, True
            if permission1 == True:
                path = domain + url
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
                            if link not in coada_de_explorare.keys():
                                coada_de_explorare[link] = {'retry': 0, 'explorat': False}
                                Q.append(link)
                    else:
                        link = link.split('#')[0]
                        if '.' in L.split('/')[-1]:
                            L = L.replace(L.split('/')[-1],'')
                        if L[-1] != '/':
                            L += '/'
                        #print(L)
                        link = L + link
                        if link not in coada_de_explorare.keys():
                            coada_de_explorare[link] = {'retry': 0, 'explorat': False}
                            Q.append(link)
    print(len(Q))
    print(Q)

def getrobots(link):
    response = requests.get("{}/robots.txt".format(link))
    test = response.text
    return test

if __name__ == "__main__":
    start_time = datetime.datetime.now()
    crawler()
    print('A durat:', str(datetime.datetime.now() - start_time))