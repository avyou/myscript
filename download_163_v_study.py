#!D:\python27\python.exe
#coding=GB2312

import urllib
import re
from bs4 import BeautifulSoup
import threading
from Queue import Queue
import os

url = "http://v.163.com/special/opencourse/bianchengdaolun.html"
htmlSource = urllib.urlopen(url).read()
#mp4re = re.compile(r'<a.*href="(http://.*\.mp4)".*/a>')
#mp4list = mp4re.findall(htmlSource)

soup = BeautifulSoup(htmlSource)
re_title = soup.findAll('td',{'class':'u-ctitle'})
re_mp4 = soup.findAll('td',{'class':'u-cdown'})

title_list = []
name_prefix = 1
for i in re_title:
    title_data = i.contents[1].contents[0]
    title_data =  '%d.%s.mp4' % (name_prefix,re.sub(u'，|,|\.|\:|：','__',title_data))
    title_list.append(title_data)
    name_prefix += 1
    #print title_data

mp4_list = []
#print re_mp4
for i in re_mp4:
    mp4_url = i.a.get('href')
    #print mp4_url
    mp4_list.append(mp4_url)

dicturl = {}
for title,mp4url in zip(title_list,mp4_list):
    try:
        dicturl[title] += mp4url
    except:
        dicturl[title] = mp4url

#print dicturl
#for title, mp4url in sorted(dicturl.items()):
#    print title
#    print mp4url

def download(filename, url):
    #print url
    #print filename
    if not os.path.exists(filename):
        urllib.urlretrieve(url,filename)

class MyThreadFunc(threading.Thread):
    def __init__(self,func,args):
        threading.Thread.__init__(self)
	self.func = func                                                                                                                                       
        self.args = args                                                                                                                                       
                                                                                                                                                               
    def run(self):                                                                                                                                             
        apply(self.func, self.args)                                                                                                                            
                                                                                                                                                               
def main():                                                                                                                                                    
    threads = []                                                                                                                                               
    urlnum = len(dicturl)                                                                                                                                      
    for title,mp4url in dicturl.items():                                                                                                                       
        t = MyThreadFunc(download,(title, mp4url))                                                                                                             
        threads.append(t)                                                                                                                                      
                                                                                                                                                               
    for i in range(urlnum):                                                                                                                                    
        threads[i].start()                                                                                                                                     
                                                                                                                                                               
    for i in range(urlnum):                                                                                                                                    
        threads[i].join()                                                                                                                                      
                                                                                                                                                               
    print 'all down'                                                                                                                                           
                                                                                                                                                               
if __name__ == '__main__':                                                                                                                                     
    main()                   