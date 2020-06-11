import urllib.robotparser
from urllib.parse import urlparse
import os
from header import robo_dict

def getrobo(baselink):
    #print(baselink)
    rp = urllib.robotparser.RobotFileParser()
    domain = urlparse(baselink).netloc
    rp.set_url(baselink + '/robots.txt')
    try:
        rp.read()
        with open(os.path.join('work_directory',domain,'robots.txt'), 'w') as file:
            file.write(str(rp))
            robo_dict[domain] = rp
    except:
        with open(os.path.join('work_directory',domain,'robots.txt'), 'w') as file:
            file.write('')
            robo_dict[domain] = None
            rp = None
    return rp

def canfetch(robo,localpath,nume_robot):
    if robo.can_fetch(nume_robot,localpath):
        return True
    else:
        return False
if __name__ == '__main__':
    rb = getrobo('http://CGI-Spec.Golux.Com')
    print(canfetch(rb,'RIWEB_CRAWLER','/crawl'))
