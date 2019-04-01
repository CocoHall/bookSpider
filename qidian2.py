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

csrf='aaa'

def getIntro(bookid):
    global csrf
    info_url="https://book.qidian.com/info/{0}"
    category_url = 'https://book.qidian.com/ajax/book/category?_csrfToken='+csrf+'&bookId={0}'
    user_agent='Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'
    header ={
        'User-Agent':user_agent,
        'Host':'book.qidian.com',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Referer': 'https://book.qidian.com',
        'Cookie': '_csrfToken='+csrf+'; newstatisticUUID=1534469328_127772446; e1=%7B%22pid%22%3A%22qd_P_Searchresult%22%2C%22eid%22%3A%22qd_S05%22%2C%22l1%22%3A3%7D; e2=%7B%22pid%22%3A%22qd_P_Searchresult%22%2C%22eid%22%3A%22qd_S01%22%2C%22l1%22%3A2%7D; qdrs=0%7C3%7C0%7C0%7C1; qdgd=1; lrbc=1004073922%7C342760907%7C1; rcr=1004073922'
    }

    info_tmp_url = info_url.format(bookid)

    req = requests.get(info_tmp_url,headers=header)

    soup = BeautifulSoup(req.content,'html5lib')

    # print soup
    intro = soup.find('div',class_='book-intro').p.get_text()
    return re.sub(r'\s','',intro).replace(u'　','').replace("'",'"').replace("\\",'/')

def detailInfo(bookid):
    global csrf
    category_url = 'https://book.qidian.com/ajax/book/category?_csrfToken='+csrf+'&bookId={0}'
    user_agent='Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'
    header ={
        'User-Agent':user_agent,
        'Host':'book.qidian.com',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Referer': 'https://book.qidian.com',
        'Cookie': '_csrfToken='+csrf+'; e1=%7B%22pid%22%3A%22qd_P_xiangqing%22%2C%22eid%22%3A%22%22%7D; e2=%7B%22pid%22%3A%22qd_P_fin%22%2C%22eid%22%3A%22qd_B58%22%2C%22l1%22%3A5%7D; newstatisticUUID=1540003010_529420568; pgv_pvi=3065774080; e1=%7B%22pid%22%3A%22qd_P_all%22%2C%22eid%22%3A%22qd_B58%22%2C%22l1%22%3A5%7D; e2=%7B%22pid%22%3A%22qd_P_all%22%2C%22eid%22%3A%22%22%2C%22l1%22%3A5%7D'
    }


    category_tmp_url = category_url.format(bookid)
    req = requests.get(category_tmp_url,headers=header)
    bookcategory = json.loads(req.content,strict=False)
    fontsum=0
    #print(bookcategory)
    for each in bookcategory['data']['vs']:
        fontsum+=each['wC']
    chapterTotalCnt = bookcategory['data']['chapterTotalCnt']
    lastTime= time.mktime(time.strptime("1971-1-1 0:0:0", "%Y-%m-%d %H:%M:%S"))
    firstTime=time.time()

    for eachVs in bookcategory['data']['vs']:
        for eachCs in eachVs['cs']:
            tmptime =  time.mktime(time.strptime(eachCs['uT'], "%Y-%m-%d %H:%M:%S"))
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
    user='账号',
    passwd='密码',
    db='数据库',
    charset='utf8'
)
cursor = connect.cursor()

#print(detailInfo(1004608738))

while True:
    
    try:
        time.sleep(random.randint(10,20))
        cursor.execute("select bookid,bookname from book where bookfrom = 'qidian' and create_time is null order by rand() limit 1;")
        connect.commit()
        result = cursor.fetchone()

        bookid = result[0]
        bookname = result[1]
        print u'正在爬取小说%d,%s'%(bookid,bookname)
        csrf=''.join(random.sample(string.ascii_letters + string.digits, 40))
        intro = getIntro(bookid)
        fontsum,chapterTotalCnt,lastTime,firstTime = detailInfo(bookid)

        sql = "UPDATE book SET intro='%s',fontsum='%d',chapterTotalCnt='%d',update_time='%s',create_time='%s' WHERE bookid = '%d';"
        data = (intro, fontsum,chapterTotalCnt,lastTime,firstTime,bookid)
        cursor.execute(sql % data)
        connect.commit()    
         
    except Exception,e:
       print e


cursor.close()
connect.close()
print 'finish'


