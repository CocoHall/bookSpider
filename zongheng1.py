# -*- coding: utf-8 -*-  
import sys  
reload(sys)  
sys.setdefaultencoding('utf8') 
import requests
import re
from bs4 import BeautifulSoup
import time
import pymysql.cursors
import random

s = requests.session()
chan_url="http://book.zongheng.com/store/c0/c0/b0/u0/p{0}/v4/s1/t0/u0/i1/ALL.html"
info_url="http://book.zongheng.com/book/{0}.html"
category_url = 'http://book.zongheng.com/showchapter/{0}.html'
user_agent='Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'
header ={
    'User-Agent':user_agent,
    'Host':'book.zongheng.com',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Referer': 'http://book.zongheng.com/book'
}


connect = pymysql.Connect(
    host='localhost',
    port=3306,
    user='账号',
    passwd='密码',
    db='数据库',
    charset='utf8'
)
cursor = connect.cursor()

def spider(chan_tmp_url,currentPage):
    global s
    chan_tmp_url=chan_tmp_url.format(currentPage)
    req = s.get(chan_tmp_url,headers=header)
    t=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    print( t+u'\t访问第'+str(currentPage)+'页')
    soup = BeautifulSoup(req.content,'html5lib')


    if random.randint(1,100)%10==0:
        s = requests.session()
    
    p=r'(\d+)页'
    m = re.search(p,req.content)
    if m!=None:
        this_pageMax=m.group(1)
    else:
        print u'未匹配'
        return 0



    for eachInfo in soup.find_all('div',class_='bookinfo'):
        tmp = eachInfo.find('div',class_='bookname').a
        bookid = tmp.attrs['href']
        bookid = re.search(r'(\d+)\.html',bookid).group(1)
        bookname = tmp.string
        author = eachInfo.find('div',class_='bookilnk').a.string
        booktype = eachInfo.find('div',class_='bookilnk').a.next_sibling.next_sibling.string
        status = re.sub(r"\s",'',eachInfo.find('div',class_='bookilnk').span.string)
        intro = eachInfo.find('div',class_='bookintro').string.replace("'",'"').replace("\\",'/')

        # fontsum = eachInfo.find('span',class_='count').children[0].string
        # fontsum = fontsum.replace(u'万','*10000').replace(u'千','1000')
        # if re.match(r'^(\d|\.|\*)+$',fontsum):
        #     fontsum = eval(fontsum)
        # else:
        #     fontsum=0
        
        cursor.execute("select 1 from book where bookid='%s' and bookfrom='zongheng';"%bookid)
        connect.commit()
        result = cursor.fetchone()
        if result!=None:
            continue



        sql = "INSERT INTO book (bookid, bookname, author,intro,booktype,status,is_vip,is_signing,bookfrom)\
         VALUES ( '%s', '%s', '%s', '%s','%s', '%s',1,1,'zongheng' )"
        data = (bookid, bookname, author,intro,booktype,status)
        try:
            cursor.execute(sql % data)
            connect.commit()
            t=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            print t+u'\t增加小说：'+bookname
        except:
            print u'mysql报错:'+sql%data

    return this_pageMax

while True:
    currentPage=1

    time.sleep(random.randint(10,20))
    pageMax = spider(chan_url,currentPage)
    while currentPage< int(pageMax):
        currentPage+=1
        try:
            time.sleep(random.randint(5,15))
            spider(chan_url,currentPage)

        except Exception,e:
            print e

cursor.close()
connect.close()
print 'finish'

