#coding=utf-8
# by avyou at 20130806
import urllib2,urllib
import re,string
from pyquery import PyQuery as pq
import StringIO
import datetime
 
mydate = raw_input("请输入你要查询的日期，如,2013-08-06 : ")
##如果没有输入日期，默认为当天日期
if len(mydate) == 0:
    mydate = datetime.datetime.now().strftime("%Y-%m-%d")
 
##返回请求的URL
def search_url(mydate):
   URL = "http://baidu.lecai.com/lottery/draw/list/557?d=%s" % mydate
   return URL
##网页请求文件头
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:22.0) Gecko/20130328 Firefox/22.0',
       'Referer': 'http://baidu.lecai.com/'}
##取得请求的URL
URL = search_url(mydate)
##请求页面的对象
reqobj = urllib2.Request(url=URL,data=None,headers=headers)
##获取源码
html = urllib2.urlopen(reqobj).read()
## 使用 pyquery 分析
d = pq(html)
## 过滤期号，如：<td class="td2"> 376245 </td>
a = d('td').filter('.td2')
 
##定义一个StringIO 缓存文件对象
f = StringIO.StringIO()
##将a 的内容写入对象f
f.write(a)
##指针移回开头
f.seek(0)
##从f对象中读取行数，开求取当前的期号数，如，376245 这些期号的数目
lineNum = int((len(f.readlines()) - 1 ) / 3 )
##过滤取得全部开彩号码
hao = d('span').filter('.ball_1').text()
#print hao
##以空格为间隔存入列表
hao_list =  hao.split(' ')
 
##求长度
allNum = len(hao_list)
 
'''
for i in xrange(0, allNum):
    if i % 10 == 0:
        print
    print hao_list[i],
 
'''
 
h = 0
p = []
for i in xrange(1,lineNum+1):
    c = []
    ## 求取每个期号
    qh = a.eq(i).text()
    ## 打印序号和期号，不分行
    print '%d\t%s' % (i,qh),
    ## 以10个为一行打印彩码
    for j in xrange(0,10):
        qhm = hao_list[h:h+10][j]
        print qhm,
    ## 求取当前彩码的前2位，存入c 列表
    for n in range(0,2):
       c.append(hao_list[h:h+10][n])
    ## 如果当前彩码的前2位数与前一期的最后2位有交集，就为错，否则为对
    if len(list(set(c) & set(p))) == 0:
       print ' 对'
    else:
       print " 错"
    p = []
    ## 求取当前彩码的最后两位，存入p 列表
    for n in range(8,10):
       p.append(hao_list[h:h+10][n])
 
    h = h + 10