# -*- coding: utf-8 -*-  
import sys  
reload(sys)  
sys.setdefaultencoding('utf8') 
import requests
import re
from bs4 import BeautifulSoup
import time
import json
import datetime
import random
import string
import pymysql.cursors

s = requests.session()


def getIntro(bookid):
    global csrf,s
    info_url="http://book.zongheng.com/book/{0}.html"
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:65.0) Gecko/20100101 Firefox/65.0'
    header ={
        'User-Agent':user_agent,
        'Host':'book.zongheng.com',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Referer': 'http://book.zongheng.com',
       }

    info_tmp_url = info_url.format(bookid)
    req = s.get(info_tmp_url,headers=header)

    soup = BeautifulSoup(req.content,'html5lib')

    # print soup
    intro = soup.find('div',class_='book-dec').p.get_text()
    return re.sub(r'\s','',intro).replace(u'　','').replace("'",'"').replace("\\",'/')

def detailInfo(bookid):
    global csrf
    category_url = 'http://book.zongheng.com/showchapter/{0}.html'
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:65.0) Gecko/20100101 Firefox/65.0'
    header ={
        'User-Agent':user_agent,
        'Host':'book.zongheng.com',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Referer': 'https://book.zongheng.com',
        }

    category_tmp_url = category_url.format(bookid)
    req = requests.get(category_tmp_url,headers=header)

    fontsum=0
    chapterTotalCnt=0
    lastTime= time.mktime(time.strptime("1971-1-1 0:0", "%Y-%m-%d %H:%M"))
    firstTime=time.time()
    for each in re.findall(u'字数：(\\d+) 更新时间：(\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}) ',req.content.decode('utf8')):
        chapterTotalCnt+=1
        fontsum+=int(each[0])

        tmptime =  time.mktime(time.strptime(each[1], "%Y-%m-%d %H:%M"))
        if tmptime-lastTime>0:
            lastTime=tmptime
        if firstTime-tmptime>0:
            firstTime=tmptime
    lastTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(lastTime))
    firstTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(firstTime))
    return (fontsum,chapterTotalCnt,lastTime,firstTime)

connect = pymysql.Connect(
    host='localhost',
    port=3306,
    user='账户',
    passwd='密码',
    db='数据库',
    charset='utf8'
)
cursor = connect.cursor()




while True:
    
    try:
        time.sleep(random.randint(10,20))
        if random.randint(1,100)%10==0:
            s = requests.session()
        cursor.execute("select bookid,bookname from book where bookfrom = 'zongheng' and create_time is null order by rand() limit 1;")
        connect.commit()
        result = cursor.fetchone()

        bookid = result[0]
        bookname = result[1]
        print u'正在爬取小说%d,%s'%(bookid,bookname)

        intro = getIntro(bookid)
        fontsum,chapterTotalCnt,lastTime,firstTime = detailInfo(bookid)

        sql = "UPDATE book SET intro='%s',fontsum='%d',chapterTotalCnt='%d',update_time='%s',create_time='%s' WHERE bookid = '%d' and bookfrom='zongheng';"
        data = (intro, fontsum,chapterTotalCnt,lastTime,firstTime,bookid)
        cursor.execute(sql % data)
        connect.commit()    
         
    except Exception,e:
       print e


cursor.close()
connect.close()
print 'finish'


