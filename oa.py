# -*- coding: utf-8 -*-

# pip install requests

import sys
import hashlib
import requests
import json
import os
import re
import uuid
from datetime import *

reload(sys)
sys.setdefaultencoding("utf-8")

class OA:
    __host = "http://oa.junnp.com:8080/"

    __headers = {
        "Connection": "keep-private",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36",
    }

    __cookies_path = "cookie.txt"
    __cookies = {}
    __weekdays = [
        "星期一",
        "星期二",
        "星期三",
        "星期四",
        "星期五",
        "星期六",
        "星期天"
    ]
    __staffname = ""
    __logfile = ""
    __shares = ""
    __loginid = ""
    __username = ""
    __password = ""

    def __init__(self , config):
        self.__logfile = config['logfile']
        self.__shares = config['shares']
        self.__loginid = config['loginid']
        self.__username = config['username']
        self.__password = config['password']
        self.__read_cookies()
        self.main()
        if self.__staffname == "":
            self.__login(self.__username , self.__password)

    def __save_cookies(self):
        if len(self.__cookies.keys()) > 0:
            f = open(self.__cookies_path, "wb")
            f.write(json.dumps(self.__cookies))

    def __read_cookies(self):
        if os.path.exists(self.__cookies_path):
            cookies_mtime = datetime.fromtimestamp(os.path.getmtime(self.__cookies_path));
            if (datetime.now() - cookies_mtime).seconds <= 1200:
                f = open(self.__cookies_path, "rb")
                str = f.read()
                if str != "":
                    self.__cookies = json.loads(str)

    def __login(self, username, password):
        payload = {
            "j_username": username,
            "j_password": hashlib.md5(password).hexdigest(),
            "j_org": ""
        }
        r = requests.post(url=self.__host + "j_spring_security_check", data=payload, headers=self.__headers);
        hl = len(r.history)
        jar = {}
        if hl > 0:
            jar = r.history[hl - 1].cookies
        else:
            jar = r.cookies

        self.__cookies = requests.utils.dict_from_cookiejar(jar)
        if len(self.__cookies.keys()) > 0 and "$=success" in r.url:
            self.__save_cookies()
            print u'用户：' + username + ' 登录成功'
        else:
            print r.text

    def main(self):
        r = requests.get(url=self.__host + "main.jsp", cookies=self.__cookies, headers=self.__headers);
        if len(r.history) > 0 and r.history[0].status_code == 302:
            self.__login(self.__username, self.__password)
            self.main()
        else:
            re_word = re.compile(u"staffName = '([\u4e00 -\u9fa5]+)'", re.U)
            m = re_word.search(r.text , 0)
            if m != None:
                self.__staffname = m.group(1);
                print u'当前用户：' + self.__staffname

    def __newlog(self):
        d = datetime.now()
        createdate = str(d.date())
        title = self.__staffname + createdate + " " + self.__weekdays[d.weekday()] + " 日志"
        logfile = open(self.__logfile.decode("utf-8") , "rb")
        loghtml = logfile.read().strip("\r\n").replace("\r\n" ,"<p></p>")

        return {
            "entityName": "calendar.Log",
            "id": str(uuid.uuid4()).replace("-", ""),
            "title": title,
            "createdate": createdate,
            "startDate":  d.strftime("%H-%M"),
            "endDate": (d + timedelta(hours=+1)).strftime("%H-%M"),
            "type": "1",
            "contentvalid": loghtml,
            "shares": self.__shares,
            "loginId": self.__loginid,
            "notetypeid": "1",
            "notetypeidOption": "1",
            "content": loghtml,
        }

    def createlog(self):
        log = self.__newlog();
        print log
        url = self.__host + "service/rest/calendar.Log/collection/create"
        r = requests.post(url, json=log, cookies=self.__cookies, headers=self.__headers);
        if len(r.history) > 0 and r.history[0].status_code == 302:
            self.__login(self.__username, self.__password)
            self.createlog()
        else:
            data = r.json()
            if data["code"] == 1:
                print u'日志创建成功'
            else:
                print data

    def getloglist(self, pageno, pagesize):
        url = self.__host + "service/rest/calendar.Log/collection/queryQuiPage"
        payload = {
            "pager.pageNo": pageno,
            "pager.pageSize": pagesize
        }
        r = requests.post(url, data=payload, cookies=self.__cookies, headers=self.__headers);
        if len(r.history) > 0 and r.history[0].status_code == 302:
            self.__login(self.__username, self.__password)
            self.getloglist(pageno, pagesize)
        else:
            data = r.json()
            print u'获取日志列表成功'
            if data["rows"] != None:
                for row in data["rows"]:
                    print "id=" + row['id'] + "\r\n" + "title=" + row['title'] + "\r\ncreatedate=" \
                          + row['createdate']+ "\r\nshares=" + row["shares"] + "\r\ncontent=" + row["content"] + "\r\n"

    def deletelog(self, id):
        url = self.__host + "service/rest/calendar.Log/" + id + "/delete"
        r = requests.post(url, cookies=self.__cookies, headers=self.__headers);
        if len(r.history) > 0 and r.history[0].status_code == 302:
            self.__login(self.__username, self.__password)
            self.deletelod(id)
        else:
            data = r.json()
            if data["code"] == 1:
                print u'删除日志成功'
            else:
                print data

