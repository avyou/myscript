#!/usr/bin/python
#coding=utf-8
# random generate log
# by zhaozf
# 20170905
"""
    log_format access '$remote_addr - $remote_user [$time_local] "$http_host" "$request" '
                  '$status $body_bytes_sent "$http_referer" '
                  '"$http_user_agent" "$http_x_forwarded_for"'
                  '$connection $upstream_addr '
                  '$upstream_response_time  $request_time ';
36.149.167.9 - - [06/Sep/2017:00:20:37 +0800] "app.dameistore.com" "POST /app/getItemPrices HTTP/1.1" 200 1177 "-" "AMengInstalments/2.6.1 (iPhone; iOS 10.3.3; Scale/3.00)" "-"5356254 127.0.0.1:8080 0.027  0.027

36.149.167.9 - - [06/Sep/2017:00:20:43 +0800] "app.dameistore.com" "POST /web/getItemDetailInfoFTL?id=369 HTTP/1.1" 200 568 "-" "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_3 like Mac OS X) AppleWebKit/603.3.8 (KHTML, like Gecko) Mobile/14G6
0" "-"5356268 127.0.0.1:8080 0.004  0.004
36.149.167.9 - - [06/Sep/2017:00:20:43 +0800] "app.dameistore.com" "GET /res/web/css/style.css?v=2.0 HTTP/1.1" 200 9719 "https://app.dameistore.com/web/getItemDetailInfoFTL?id=369" "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_3 like Mac OS X
) AppleWebKit/603.3.8 (KHTML, like Gecko) Mobile/14G60" "-"5356268 - -  0.000
36.149.167.9 - - [06/Sep/2017:00:20:44 +0800] "app.dameistore.com" "GET /ueditor/jsp/upload/image/20170329/1490778207319073801.png HTTP/1.1" 200 37682 "https://app.dameistore.com/web/getItemDetailInfoFTL?id=369" "Mozilla/5.0 (iPhone; CPU
 iPhone OS 10_3_3 like Mac OS X) AppleWebKit/603.3.8 (KHTML, like Gecko) Mobile/14G60" "-"5356270 - -  0.093

117.136.41.91 - - [06/Sep/2017:00:20:49 +0800] "app.dameistore.com" "POST /app/myIdentify HTTP/1.1" 200 650 "-" "-" "-"5356273 127.0.0.1:8080 0.005  0.005
117.136.41.91 - - [06/Sep/2017:00:20:49 +0800] "app.dameistore.com" "POST /app/getPlatformListForApp HTTP/1.1" 200 3905 "-" "-" "-"5356275 127.0.0.1:8080 0.005  0.018
117.136.41.91 - - [06/Sep/2017:00:20:51 +0800] "app.dameistore.com" "POST /app/creditPacketInfo HTTP/1.1" 200 791 "-" "-" "-"5356277 127.0.0.1:8080 0.013  0.013

"""

import linecache
import random
import time
import datetime
import os

#t  = time.strftime("%d/%m/%Y:%H:%M:%S", time.localtime())

##时间戳转时间
def StrToTimestamp(dt):
    timeArray = time.strptime(dt, "%Y-%m-%d %H:%M:%S")
    timestamp = int(time.mktime(timeArray))
    return timestamp
##时间转时间戳
def TimestampToTime(timestamp):
    timeArray = time.localtime(timestamp)
    timestyle = time.strftime("%d/%m/%Y:%H:%M:%S", timeArray)
    timestyle_list = timestyle.split("/")
    month_num = timestyle_list[1]
    month_letter = month_num_to_letter[month_num]
    timestyle_list[1] = month_letter
    timestyle_log = "/".join(timestyle_list)
    return timestyle_log

##取过去多少天的时间
def day_get(day_ago):
    day_now = datetime.datetime.now()
    day_ago = datetime.timedelta(days=day_ago)
    day = day_now - day_ago
    date_ago = datetime.datetime(day.year, day.month, day.day, 0, 0, 0)
    return date_ago


class RandomGenLog(object):

    ##初始化参数
    def __init__(self,start_time_stamp,init_log_filename):
        self.file_ist = fileList
        ##统计对应文件的行数，用于随机取行
        self.mydict = self.fileLineCount()
        self.ip_file = "ip.txt"
        self.domain_file = "domain.txt"
        self.agent_file = "agent.txt"
        ##最开始写入日志的时间戳
        self.start_time_stamp = start_time_stamp
        ##以这个时间为标准做最开始的时间比较，用于写入到不同日期的日志文件
        self.start_time_stamp_record = start_time_stamp
        ##初始文件名
        self.log_filename = init_log_filename
        ##循环写入日志总条数
        self.write_num = write_num
        self.random_define()

    ##预定义随机的字符
    def random_define(self):
        #self.fileBodySizeRange = fileBodySizeRange
        ##状态码
        self.status_list = ['200','206','502','503','404','403','304','499']
        ##状态码出现的权重比列
        self.weight_status = [85,11.5,0.5,0.2,0.8,0.3,1.5,0.2]
        ##随机字母
        self.alph_str = "abcdefghhijklmnopqrsvwz"
        ##阿随机数字
        self.num_str = "0123456789"
        ##混合或字母或数字
        self.mix_alph_num = self.alph_str + self.num_str
        ##请求URL文件的扩展名文件类型及对应的size 大小范围
        self.fileBodySizeRange = {
            'mp4':(1024000,204800000),
            'flv':(1024000,204800000),
            'rar':(1024000,81920000),
            'zip':(1024000,81920000),
            'm3u8':(1000,1500),
            'ts':(1024000,5120000),
            'jpg':(10240,3072000),
            'ico':(500,5120),
            'png':(10240,2048000),
            'gif':(102400,10240000),
            'css':(500,20480),
            'js':(500,20480),
            'json':(30000,80263),
            'xml':(10263,60000),
            'apk':(5120000,51200000),
            'exe':(2120000,31200000),
        }
    ##返回随机的字符串
    def random_fun(self,chars):
        str = ''
        #chars = "abcdefghijklmnopqrstuvwyz0123456789"
        length = len(chars) - 1
        for i in range(random.randint(2,7)):
            random_str = chars[random.randint(0, length)]
            str += random_str
        return str

    ##统计对应文件的行数，用于随机取行
    def fileLineCount(self):
        mydict = {}
        for i in self.file_ist:
            count = len(linecache.getlines(i))
            mydict[i] = count
        return mydict
    ##从文件中随机取行
    def choiceRomLine(self,filename):
        count = self.mydict[filename]
        lineno = random.randrange(0,count)
        line = linecache.getline(filename,lineno).rstrip("\n")
        return line

    def RandomGenFild(self):

        reqfname_m3u8 = random.choice(["index","360p","540p","720p","1024p"])
        ##html 的文件名
        reqfname_html = random.choice(["index","home",self.random_fun(self.alph_str),self.random_fun(self.num_str),
                                       self.random_fun(self.mix_alph_num)])

        reqpath_list = [self.random_fun(self.alph_str),self.random_fun(self.num_str),self.random_fun(self.mix_alph_num),
                        self.random_fun(self.alph_str),self.random_fun(self.num_str),self.random_fun(self.mix_alph_num),
                        self.random_fun(self.alph_str),self.random_fun(self.num_str)]
        ##路径长度范围随机组合成的列表
        slice_reqpath = random.sample(reqpath_list,random.randint(0,5))

        ext_list = self.fileBodySizeRange.keys()
        ext_name = random.choice(ext_list)
        ext_name_body = self.fileBodySizeRange[ext_name]
        ### 日期时间随机自加，0的出现的机率高些
        self.start_time_stamp += random.choice([0,0,0,0,1])
        ## 取IP
        ipd =self.choiceRomLine(self.ip_file).split('.')
        ##print ipd
        ##防止取IP程序出错
        if len(ipd) != 0:
            try:
                ip = ".".join([ipd[0],ipd[1],ipd[2],str(random.randint(1,254))])
            except:
                ip = '1.1.1.1'
        else:
            ip = "1.1.1.1"
        ## 取域名
        domain = self.choiceRomLine(self.domain_file)
        if len(domain) == 0:
            domain = 'www.fang.com'
        ## 取 user agent
        agent = self.choiceRomLine(self.agent_file)
        if len(agent)  == 0:
            agent = '-'
        ##随机状态码
        status = self.status_list[self.weightChoice()]
        ##非正常状态码的 body大小
        if status in ['404','403','499','502','503']:
            body = random.randint(100,512)
        else:
            body = random.randint(ext_name_body[0],ext_name_body[1])

        if len(slice_reqpath) == 0:
            request_url = "/" + reqfname_html + ".html"

        elif ext_name == 'm3u8':
            request_url = "/" + self.random_fun(self.alph_str) + "/" + reqfname_m3u8 + "." + ext_name

        elif ext_name == "ts":
            request_url = "/" + "/".join(slice_reqpath)  + "/" + self.random_fun(self.num_str) + "." + ext_name
        else:
            request_url = "/" + "/".join(slice_reqpath)  + "." + ext_name

        self.next_time = TimestampToTime(self.start_time_stamp)
        print request_url

        return ip,domain,agent,body,status,request_url,self.next_time

    def logFormat(self):
        genFild = self.RandomGenFild()
        ip = genFild[0]
        domain = genFild[1]
        agent = genFild[2]
        body = genFild[3]
        status = genFild[4]
        request_url = genFild[5]
        log_time = genFild[6]
        log_time_str_list = log_time.split("/")
        #print log_time_str_list
        log_year = log_time_str_list[2].split(':')[0]
        log_month = month_letter_to_num[log_time_str_list[1]]
        log_day = log_time_str_list[0]
        print "写入文件: %s" %self.log_filename
        #log_hour = log_time_str_list[2].split(':')[1]
        self.log_filename = "".join(["access_nginx_",log_year,'-',log_month,'-',log_day,'.log'])
        self.logMsgFormat = '''{0} - - [{1} +0800] "{2}" "GET {3} HTTP/1.1" {4} {5} {6} "-" "-"'''.format(ip,log_time,domain,request_url,status,body,agent)

        return self.logMsgFormat

    def WriteLog(self):
        # if locals().has_key('log_file_path'):
        if not os.path.exists(log_file_path):
            os.makedirs(log_file_path)
            self.log_filename = os.sep.join([log_file_path,self.log_filename])
        ## 这里未通过外部调用类来循环写入日志，是为了防止不断的重复多次打开和关闭文件，浪费系统资源影响效率
        with open(self.log_filename,"a") as f:
            ## 循环的写入条数
            for i in xrange(1,self.write_num):
                msg = self.logFormat()
                f.write(msg+"\n")
                ##如果超过一天，更换日志文件再写入
                if (self.start_time_stamp - 86400) > self.start_time_stamp_record:
                    self.start_time_stamp_record = self.start_time_stamp
                    f.flush()
                    f.close()
                    self.WriteLog()

    ##状态码的概率函数
    def weightChoice(self):
        randnum = random.uniform(0.0,float(sum(self.weight_status)))
        start = 0.0
        for schoice, item in enumerate(self.weight_status):
            #print index,item
            start += item
            if randnum <= start:
                break
        return schoice


def main():
    start_time = str(day_get(write_before_day))
    print "初始时间:",start_time
    start_time_stamp = StrToTimestamp(start_time)
    print "初始时间戳:",start_time_stamp
    log_year = start_time[0:4]
    log_month = start_time[5:7]
    log_day = start_time[8:10]
    init_log_filename = "".join(["access_nginx_",log_year,'-',log_month,'-',log_day,'.log'])
    print "初始日志文件名:",init_log_filename
    if os.path.exists(init_log_filename):
        os.remove(init_log_filename)

    F = RandomGenLog(start_time_stamp,init_log_filename)
    F.WriteLog()

    ##测试状态码的随机比率
    # a = {'200':0,'206':0,'502':0,'503':0,'404':0,'403':0,'304':0}
    # for i in xrange(1000):
    #     j = status_list[F.weightChoice()]
    #     a[str(j)] += 1
    # print a

if __name__ == '__main__':
    fileList = ["ip.txt","domain.txt","agent.txt"]
    log_file_path = "/Users/liuheng/dev/nginx/ins/logs/"
    ##要写入多少天的日志
    write_before_day = 7
    ## 根据天数转成条数，但要乘倍
    write_num = 7 * 3600 * 24 * 4
    ##日志格式的月份有是字母，这里是为了映射： 数字 -》字母
    month_num_to_letter = {'01':'Jan','02':'Feb','03':'Mar','04':'Apr','05':'May','06':'Jun','07':'Jul','08':'Aug','09':'Sep','10':'Oct','11':'Nov','12':'Dec'}
    ## 月份 字母--》数字
    month_letter_to_num = dict([(v,k) for k,v in month_num_to_letter.iteritems()])

    main()