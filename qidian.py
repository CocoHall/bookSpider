# -*- coding: utf-8 -*-  
import sys  
reload(sys)  
sys.setdefaultencoding('utf8') 
import requests
import re
from bs4 import BeautifulSoup
from fontTools.ttLib import TTFont
import time
import pymysql.cursors
import random

s = requests.session()
#xh_url="https://www.qidian.com/finish?chanId=21&action=hidden&orderId=&page={0}&vip=1&style=1&pageSize=20&siteid=1&pubflag=0&hiddenField=2"
# chan_url="https://www.qidian.com/finish?size=-1&sign=-1&tag=-1&chanId={0}&subCateId=-1&orderId=&update=-1&month=-1&style=1&vip=1"
chan_url="https://www.qidian.com/finish?chanId={0}&action=hidden&orderId=&vip=1&style=1&pageSize=20&siteid=1&pubflag=0&hiddenField=2"
chan=[]
chan.append({'id':6,'name':u'军事'})
chan.append({'id':21,'name':u'玄幻'})
chan.append({'id':5,'name':u'历史'})
chan.append({'id':9,'name':u'科幻'})
chan.append({'id':10,'name':u'灵异'})
chan.append({'id':22,'name':u'仙侠'})
chan.append({'id':2,'name':u'武侠'})
chan.append({'id':1,'name':u'奇幻'})
chan.append({'id':4,'name':u'都市'})
chan.append({'id':7,'name':u'游戏'})
chan.append({'id':10,'name':u'二次元'})
chan.append({'id':15,'name':u'现实'})

#chanId:21->玄幻 5->历史 9->科幻 10->灵异 22->仙侠 2->武侠 1->奇幻 4->都市 15->现实 6->军事 7->游戏 10->二次元
info_url="https://book.qidian.com/info/{0}"
category_url = 'https://book.qidian.com/ajax/book/category?_csrfToken=rCYlaunorM7XNYLPJzLGKLCyw5lLk1xz7sJG6KLp&bookId={0}'
user_agent='Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'
header ={
    'User-Agent':user_agent,
    'Host':'www.qidian.com',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Referer': 'https://www.qidian.com/finish?size=-1&sign=-1&tag=-1'
}

def resolveFont(fontName,enValue):
    header={
    'Host': 'qidian.gtimg.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0',
    'Accept': 'application/font-woff2;q=1.0,application/font-woff;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Referer': 'https://book.qidian.com/info/2643379',
    'Origin': 'https://book.qidian.com',
    'DNT': '1',
    'Connection': 'close'
    }
    font_url = "https://qidian.gtimg.com/qd_anti_spider/%s.woff" % fontName
    woff = requests.get(font_url,headers=header).content
    with open('fonts.woff', 'wb') as f:
        f.write(woff)
    online_fonts = TTFont('fonts.woff')
    # online_fonts.saveXML("text.xml")
    _dict = online_fonts.getBestCmap()

    origin_dic = {
            "six": "6",
            "three": "3",
            "period": ".",
            "eight": "8",
            "zero": "0",
            "five": "5",
            "nine": "9",
            "four": "4",
            "seven": '7',
            "one": "1",
            "two": "2"
        }
    t=''
    for each in enValue:
        tmp = origin_dic[_dict[int('0x'+each,16)]]
        t+=tmp
    return int(float(t)*10000)

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
    chan_tmp_url+='&page='+str(currentPage)
    req = s.get(chan_tmp_url,headers=header)
    t=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    print t+u'\t访问'+chan[chan_index]['name']+'完本vip频道'+str(currentPage)+'页'
    soup = BeautifulSoup(req.content,'html5lib')
    if random.randint(1,100)%10==0:
        s = requests.session()
    
    p='data-pageMax="(\d+)"'
    m = re.search(p,req.content,flags=re.IGNORECASE)
    if m!=None:
        this_pageMax=m.group(1)
    else:
        print u'未匹配'
        return 0



    for eachInfo in soup.find_all('div',class_='book-mid-info'):
        bookid = eachInfo.find('a',attrs={'data-eid':'qd_B58'}).attrs['data-bid']
        
        cursor.execute("select 1 from book where bookid='%s' and bookfrom='qidian';"%bookid)
        connect.commit()
        result = cursor.fetchone()
        if result!=None:
            continue
        bookname = eachInfo.find('a',attrs={'data-eid':'qd_B58'}).string.replace(",",'"').replace("\\",'/')
        author = eachInfo.find('a',attrs={'data-eid':'qd_B59'}).string.replace(",",'"').replace("\\",'/')
        booktype = eachInfo.find('a',attrs={'data-eid':'qd_B60'}).string
        subtype = eachInfo.find('a',attrs={'data-eid':'qd_B61'}).string
        intro = eachInfo.find('p',class_='intro').string.replace("'",'"').replace("\\",'/')
        status = eachInfo.find('a',attrs={'data-eid':'qd_B61'}).next_sibling.next_sibling.string
        fontsum = eachInfo.find('p',class_='update').span.span.string.encode('unicode_escape')
        font = eachInfo.find('p',class_='update').span.span.attrs['class'][0]
        fontsum = str((fontsum.split(" ")))[0:-2].split(r"\\U000")[1:]
        fontsum = resolveFont(font,fontsum)


        sql = "INSERT INTO book (bookid, bookname, author,intro,booktype,subtype,status,fontsum,is_vip,is_signing,bookfrom)\
         VALUES ( '%s', '%s', '%s', '%s','%s', '%s', '%s',%d,1,1,'qidian' )"
        data = (bookid, bookname, author,intro,booktype,subtype,status,fontsum)
        try:
            cursor.execute(sql % data)
            connect.commit()
            t=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            print t+u'\t增加小说：'+bookname
        except:
            print u'mysql报错:'+sql%data

    return this_pageMax

while True:

    
    chan_index = random.randint(0, len(chan)-1)
    currentPage=1
    chan_tmp_url = chan_url.format(chan[chan_index]['id'])
    time.sleep(random.randint(10,20))
    pageMax = spider(chan_tmp_url,currentPage)
    # print 'pageMax:'+str(pageMax)
    while currentPage< int(pageMax):
        currentPage+=1
        try:
            time.sleep(random.randint(5,15))
            spider(chan_tmp_url,currentPage)

        except Exception,e:
            print e

cursor.close()
connect.close()
print 'finish'

