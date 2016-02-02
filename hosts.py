# -*- coding: utf-8 -*-
#run as root

import shutil
import subprocess
import platform
import os
from datetime import datetime
from httplib import HTTPSConnection

def fetchHostsData():
    '''
    get hosts data
    :return:
    '''
    conn = HTTPSConnection("raw.githubusercontent.com", timeout = 30)
    conn.request("GET", "/racaljk/hosts/master/hosts")
    resp = conn.getresponse()
    if resp.status == 200:
        return resp.read()
    else:
        print datetime.now().strftime('%Y-%m-%d %H-%M-%S') + '->' , 'fail fetch hosts data from https://raw.githubusercontent.com/racaljk/hosts/master/hosts'\
            , resp.status , resp.reason
    return ''

def getLastupdated(content):
    '''
    get hosts data last updated time
    :param content:
    :return:
    '''
    start = content.index('Last updated:')
    end = content.index('\n' , start)
    if end > start:
        return content[start:end]
    return ''

def replace_hosts_windows(content):
    '''
    [windows] write hosts data to file and replace system hosts file
    :param content:
    :return:
    '''
    dstdir = 'C:\Windows\System32\drivers\etc'
    with open(dstdir + '\hosts.new' , 'w') as f:
        f.write(content)
    f.close()
    shutil.copyfile(dstdir + '\hosts' , dstdir + '\hosts.bak')
    shutil.copyfile(dstdir + '\hosts.new' , dstdir + '\hosts')
    print datetime.now().strftime('%Y-%m-%d %H-%M-%S') , '->' ,'replace system hosts file success'
    subprocess.check_call(['ipconfig' , '/flushdns'])

def replace_hosts_linux(content):
    '''
    [linux] write hosts data to file and replace system hosts file
    :param content:
    :return:
    '''
    dst = 'hosts.new'
    if os.path.exists('/sdcard'):
        dst = '/sdcard/' + dst
    else:
        dst = '/tmp/' + dst
    with open(dst , 'w') as f:
        f.write(content)
    f.close()
    os.system('su -c "cp /etc/hosts /etc/hosts.bak"')
    os.system('su -c "cp {} /etc/hosts"'.format(dst))
    print datetime.now().strftime('%Y-%m-%d %H-%M-%S') , '->' ,'replace system hosts file success'

def fetch_replace_hosts():
    print datetime.now().strftime('%Y-%m-%d %H-%M-%S') + '->' , 'begin fetching hosts data'
    data = fetchHostsData()
    if data != '' :
        print datetime.now().strftime('%Y-%m-%d %H-%M-%S') + '->' , 'success fetched hosts data'
        lastupdated = getLastupdated(data)
        if lastupdated != '':
            print datetime.now().strftime('%Y-%m-%d %H-%M-%S') + '->' ,lastupdated
        tip = 'do you need to replace system hosts file? \n [y]-yes \n [n]-no \n'
        confirm = raw_input(tip)
        while True:
            if confirm == 'y':
                sys = platform.system()
                if sys == 'Windows':
                    replace_hosts_windows(data)
                elif sys == 'Linux':
                    replace_hosts_linux(data)
                else:
                    print 'unsupport platform' , sys
                break
            elif confirm == 'n':
                break
            else:
                confirm = raw_input(tip)

if __name__ == '__main__':
    fetch_replace_hosts()


