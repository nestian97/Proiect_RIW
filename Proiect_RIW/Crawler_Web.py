from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import datetime
import sys
import os
from DNS_From_Internet import DNSCache
from HTTPParser import extract_html_page
from header import coada_de_explorare, Q, robo_dict
import robots as rb
import shutil

##########################################################################
########################### VARIABLES ####################################
##########################################################################

adresses_for_domains = {}
total = 0
nefacute1 = 0
nefacute2 = 0
facute = 0
nefacute3 = 0
old_time = None
current_time = None
old_domain = None
##########################################################################
########################### FUNCTIONS ####################################
##########################################################################
def isabsolute(url):
    return bool(urlparse(url).netloc)


# =========================Function for receiving data===========================
def crawler():
    counter = 0
    global total, nefacute1, nefacute2, nefacute3, facute,old_time,current_time,old_domain
    for L in Q:
        P = None
        total += 1

        if coada_de_explorare[L]['explorat'] == True:
            continue
            nefacute3 += 1
        domain = urlparse(L).netloc

        url = urlparse(L).path
        baselink = urlparse(L).scheme + '://' + domain
        if not (os.path.isdir(os.path.join('work_directory', domain))):
            os.mkdir(os.path.join('work_directory', domain))

        #mai verific odata daca am permisiune de la robots
        if domain not in robo_dict:
            robo = rb.getrobo(baselink)
        else:
            robo = robo_dict[domain]
        if robo is not None:
            if not rb.canfetch(robo, url, 'RIWEB_CRAWLER'):
                continue

        path = domain + url

        #verific daca nu am descarcat deja pagina
        if path.split('/')[-1] == '':
            if os.path.isfile(os.path.join('work_directory',path,'index.html')):
                #print('Exista1')
                continue
        else:
            #print(path)
            if os.path.isfile(os.path.join('work_directory',path)):
                #print('Exista2')
                continue

        # verific daca am o adresa ip pentru link
        if domain not in adresses_for_domains:
            adresses_for_domains[domain] = {}
        # print(adresses_for_domains)
        if adresses_for_domains[domain] == {}:
            adresses_for_domains[domain] = DNSCache(domain, adresses_for_domains[domain])
        if adresses_for_domains[domain] is None:
            continue
        ip_adr = adresses_for_domains[domain]['ip_address']

        if ip_adr is not None or ip_adr != '':
            current_time = datetime.datetime.now()
            if old_time is None:
                P = extract_html_page(url, domain, ip_adr, L)
                old_domain = domain
            elif (current_time - old_time).total_seconds() < 1 and old_domain == domain:
                time.sleep(1)
                P = extract_html_page(url, domain, ip_adr, L)
                old_time = current_time
            else:
                P = extract_html_page(url, domain, ip_adr, L)
                old_time = current_time
                old_domain = domain
        if P is not None:
            try:


                getpage_soup = BeautifulSoup(P, 'html.parser')

            except Exception as e:
                nefacute3 += 1
                print(e)
                pass
            metas = getpage_soup.find_all('meta')
            permission1 = False
            permission2 = False
            break_activated = False
            for meta in metas:
                if meta.get('name') == 'robots':
                    if 'all' in meta.get('content') or 'index' in meta.get('content'):
                        permission1 = True

                    if 'all' in meta.get('content') or 'follow' in meta.get('content'):
                        permission2 = True

            if not any(meta.get('name') == 'robots' for meta in metas):
                permission1, permission2 = True, True
            if permission1 == True:
                path = domain + url
                path = path.split('/')
                current_path = os.path.join(os.getcwd(), 'work_directory')
                for var in path[:-1]:
                    if (os.path.isdir(os.path.join(current_path, var))):
                        current_path = os.path.join(current_path, var)
                    else:
                        current_path = os.path.join(current_path, var)
                        os.mkdir(current_path)
                if path[-1] == '':
                    nume_fisier = 'index.html'
                else:
                    nume_fisier = path[-1]
                with open('{}\{}.html'.format(current_path, nume_fisier.split('.')[0]), 'wb') as file:
                    file.write(P.encode('utf8'))
                    facute += 1
            else:
                nefacute1 += 1
            if permission2 == True:
                a_tags = getpage_soup.find_all('a', href=True)
                for a_tag in a_tags:
                    link = a_tag['href']
                    link2 = a_tag['href']
                    if isabsolute(link):
                        if link[:link.find(':')] == 'http':  # or link[:link.find(':')] == 'https':
                            link = link.split('#')[0]
                            if link not in coada_de_explorare.keys():
                                #verifica robots pentru domeniu
                                if urlparse(link).netloc not in robo_dict:
                                    robo = rb.getrobo(urlparse(link).scheme + '://' + urlparse(link).netloc)
                                else:
                                    robo = robo_dict[urlparse(link).netloc]
                                if robo is not None:
                                    if not rb.canfetch(robo, urlparse(link).path, 'RIWEB_CRAWLER'):
                                        continue

                                path = urlparse(link).netloc + urlparse(link).path
                                if path.split('/')[-1] == '':
                                    if os.path.isfile(os.path.join('work_directory', path, 'index.html')):
                                        #print('Exista1')
                                        continue
                                else:
                                    # print(path)
                                    if os.path.isfile(os.path.join('work_directory', path)):
                                        #print('Exista2')
                                        continue
                                coada_de_explorare[link] = {'retry': 0, 'explorat': False}
                                Q.append(link)
                    else:
                        link = urljoin(L, link)
                        link = link.split('#')[0]
                        port = urlparse(link).port
                        if port is not None:
                            link.replace(':{}'.format(port), '')
                            print(link)
                        if link not in coada_de_explorare.keys() and os:
                            if urlparse(link).netloc not in robo_dict:
                                robo = rb.getrobo(urlparse(link).scheme + '://' + urlparse(link).netloc)
                            else:
                                robo = robo_dict[urlparse(link).netloc]
                            if robo is not None:
                                if not rb.canfetch(robo, urlparse(link).path, 'RIWEB_CRAWLER'):
                                    continue
                            #verifica daca exista deja un fisier cu acest nume
                            path = urlparse(link).netloc + urlparse(link).path
                            if path.split('/')[-1] == '':
                                if os.path.isfile(os.path.join('work_directory', path, 'index.html')):
                                    continue
                            else:
                                # print(path)
                                if os.path.isfile(os.path.join('work_directory', path)):
                                    continue
                            coada_de_explorare[link] = {'retry': 0, 'explorat': False}
                            Q.append(link)
                            # print(link)
        else:
            nefacute2 += 1
        if counter % 30 == 0:
            # print("Procent nefacute perm:", nefacute1, '/', total)
            # print("Procent nefacute null:", nefacute2, '/', total)
            # print("Procent nefacute3/ facute:", nefacute3, '/', facute)

            counter += 1
        else:
            counter += 1
        if facute == 100:
            break
    print(len(Q))
    print(Q)


if __name__ == "__main__":
    folder = 'work_directory'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except:
            pass
    start_time = datetime.datetime.now()
    print('A inceput la: ', start_time)
    crawler()
    print('A durat:', str(datetime.datetime.now() - start_time))
