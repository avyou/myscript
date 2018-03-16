#!/usr/bin/python
#coding=utf-8
# random generate log
# by zhaozf(avyou)
# 20170905
"""

"""

import linecache
import random
import time
import datetime
import os,shutil,sys
import platform

#t  = time.strftime("%d/%m/%Y:%H:%M:%S", time.localtime())

##时间转时间戳
def StrToTimestamp(dt):
    timeArray = time.strptime(dt, "%Y-%m-%d %H:%M:%S")
    timestamp = int(time.mktime(timeArray))
    return timestamp
##时间转时间戳
def TimestampToTime(timestamp):
    timeArray = time.localtime(timestamp)
    timestyle = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    timestyle_list = timestyle.split("/")
    month_num = timestyle_list[1]
    month_letter = month_num_to_letter[month_num]
    timestyle_list[1] = month_letter
    timestyle_log = "/".join(timestyle_list)
    return timestyle_log

def TimestramToTime2(timestamp):
    timeArray = time.localtime(timestamp)
    timestyle = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return  timestyle


def recordLog(msg):
    with open(output_log,'a') as f:
        f.write(msg+"\n")

class RandomGenLog(object):

    ##初始化参数
    def __init__(self,init_log_filename):

        self.file_ist = fileList
        ##统计对应文件的行数，用于随机取行
        self.mydict = self.fileLineCount()
        self.ip_file = "ip.txt"
        self.domain_file = "domain.txt"
        self.agent_file = "agent.txt"
        ##初始文件名
        self.log_filename = init_log_filename
        ##循环写入日志总条数
        self.write_num = writelog_by_min
        self.initfun()
        self.timeDefine()
        self.random_define()


    def initfun(self):
        self.domain_dict = {}
        self.domain_list = []
        with open(self.domain_file) as f:
            for i in f.readlines():
                domain =  i.strip()
                self.domain_dict[domain] = {'bw':0,'bw_5min':0,'hits':0,'hits_err':0,'hits_5min':0,'hits_err_5min':0,'hits_5min_last':0,'hits_err_5min_last':0}

        self.count_line = 0
        self.count_line_second = 0
        self.hits = 0
        self.hits_error = 0
        self.hist_5min_last = 0
        self.hist_error_5min_last = 0
        self.bandwidth = 0



    def timeDefine(self):
        self.max_seconds = max_seconds
        self.start_time_stamp_record = int(time.time())
        self.time_second_record = self.start_time_stamp_record
        start_time_record = TimestramToTime2(self.start_time_stamp_record)
        start_time_record_list = start_time_record.split(':')
        get_min = start_time_record_list[-2]
        if 0 <= int(get_min)<5:
            start_time_record_list[-2] = "00"
        elif 5<=int(get_min)<10:
            start_time_record_list[-2] = "05"
        elif 10<=int(get_min)<15:
            start_time_record_list[-2] = "10"
        elif 15<=int(get_min)<20:
            start_time_record_list[-2] = "15"
        elif 20<=int(get_min)<25:
            start_time_record_list[-2] = "20"
        elif 25<=int(get_min)<30:
            start_time_record_list[-2] = "25"
        elif 30<=int(get_min)<35:
            start_time_record_list[-2] = "30"
        elif 35<=int(get_min)<40:
            start_time_record_list[-2] = "35"
        elif 40<=int(get_min)<45:
            start_time_record_list[-2] = "40"
        elif 45<=int(get_min)<50:
            start_time_record_list[-2] = "45"
        elif 50<=int(get_min)<55:
            start_time_record_list[-2] = "50"
        elif int(get_min)>=55:
            start_time_record_list[-2] = "55"

        start_time_record_list[-1] = "00"
        start_time_record_int = ":".join(start_time_record_list)
        print "起始时间：",start_time_record_int
        recordLog("起始时间：%s" % start_time_record_int)
        self.start_time_stamp_record_int = StrToTimestamp(start_time_record_int)
        print "起始时间戳",self.start_time_stamp_record_int
        recordLog("起始时间戳：%s" % self.start_time_stamp_record_int)
        self.start_time_stamp_record_5_min = self.start_time_stamp_record
        self.date_hour = time.strftime('%Y%m%d%H',time.localtime(time.time()))

    ##预定义随机的字符
    def random_define(self):
        #self.fileBodySizeRange = fileBodySizeRange
        ##状态码
        self.status_list = ['200','206','502','503','404','403','304','499']
        self.status_error_list = ['404','403','499','502','503']
        ##状态码出现的权重比列
        self.weight_status = [85,11.5,0.5,0.2,0.8,0.3,1.5,0.2]
        ##随机字母
        self.alph_str = "abcdefghhijklmnopqrsvwz"
        self.sleep_time = [0.1]*5 + [0.01]*5 + [1]*2 + [2]
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
        # reqfname_alph = self.random_fun(self.alph_str)
        # print "随机字母:",reqfname_alph
        # reqfname_num = self.random_fun(self.num_str)
        # print "随机数字:",reqfname_num
        # reqfname_mix_alph_num = self.random_fun(self.mix_alph_num)
        # print "混合字母或数字:",reqfname_mix_alph_num
        ## 同时m3u8 的文件名
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
        if status in self.status_error_list:
            body = random.randint(100,512)
        else:
            body = random.randint(ext_name_body[0],ext_name_body[1])

        if len(slice_reqpath) == 0:
            request_url = "/" + reqfname_html + ".html"

        elif ext_name == 'm3u8':
            request_url = "/" + self.random_fun(self.alph_str) + "/" + reqfname_m3u8 + "." + ext_name

        elif ext_name == "ts":
            request_url = "/" + "/".join(slice_reqpath)  + "/" + self.random_fun(self.num_str) + "." + ext_name

        elif ext_name in ['jpg','gif','png']:
            request_url = "/" + random.choice(["upload","uploadfile","image","img"]) + "/" + "/".join(slice_reqpath) \
                          + random.choice([self.random_fun(self.alph_str),self.random_fun(self.num_str)]) + "." + ext_name

        elif ext_name in ['js','css','ico']:
            request_url = "/" + "static" + "/" \
                          + random.choice([self.random_fun(self.alph_str),self.random_fun(self.num_str)]) + "." + ext_name
        else:
            request_url = "/" + "/".join(slice_reqpath)  + "." + ext_name

        self.this_time_stamp = int(time.time())
        self.this_time = TimestampToTime(self.this_time_stamp)
        #print request_url

        return ip,domain,agent,body,status,request_url,self.this_time

    def logFormat(self):
        genFild = self.RandomGenFild()
        ip = genFild[0]
        domain = genFild[1]
        agent = genFild[2]
        self.body = genFild[3]
        status = genFild[4]
        request_url = genFild[5]
        log_time = genFild[6]
        log_time_str_list = log_time.split("/")
        log_year = log_time_str_list[2].split(':')[0]
        log_month = month_letter_to_num[log_time_str_list[1]]
        log_day = log_time_str_list[0]
        log_hour = log_time_str_list[2].split(':')[1]
        #log_min = log_time_str_list[2].split(':')[2]
        self.nowdate_by_hour = log_year + log_month + log_day + log_hour
        self.logMsgFormat = '''{0} - - [{1} +0800] "{2}" "GET {3} HTTP/1.1" {4} {5} "-" "{6}" "-" "-"'''.format(ip,log_time,domain,request_url,status,self.body,agent)
        #status_line = 1
        if status in self.status_error_list:
            self.domain_dict[domain]["hits_err"] = self.domain_dict[domain]["hits_err"] + 1
            self.hits_error = self.hits_error + 1

        else:
            self.hits = self.hits + 1
            self.bandwidth = self.bandwidth + self.body
            self.domain_dict[domain]['bw'] =  self.domain_dict[domain]['bw'] + self.body
            self.domain_dict[domain]['hits'] =  self.domain_dict[domain]['hits'] + 1
        return self.logMsgFormat

    def WriteLog(self):

        ## 这里未通过外部调用类来循环写入日志，是为了防止不断的重复多次打开和关闭文件，浪费系统资源影响效率
        with open(self.log_filename,"a") as f:
            ## 循环的写入条数
            for i in xrange(1,self.write_num):
                #print "写第几条日志: %s" %i
                msg = self.logFormat()
                f.write(msg +"\n")

                if(self.this_time_stamp - self.start_time_stamp_record_int) == 299:
                    start_t = TimestramToTime2(self.start_time_stamp_record_int)
                    end_t = TimestramToTime2(self.this_time_stamp)
                    self.start_time_stamp_record_int = self.start_time_stamp_record_int + 300
                    hits_5min = self.hits - self.hist_5min_last
                    hits_error_5min = self.hits_error - self.hist_error_5min_last
                    bw_5min = float((self.bandwidth/1024/1024/300) * 8)
                    time_msg = "{0:15}~{1:15}".format(start_t,end_t)
                    print time_msg
                    #recordLog(time_msg)
                    recordLog("\n #############################  %s #################################\n" %time_msg)
                    msg_normal = "5分钟正常请求日志（包含所有域名）写入行数： {0:12} ".format(hits_5min)
                    msg_error = "5分钟错误请求日志（包含所有域名）写入行数：{0:12} 行".format(hits_error_5min)
                    msg_bw = "5分钟请求平均带宽是（包含所有域名）：{0:12.2f} Mbps".format(bw_5min)
                    msg_hits = "到目前为止正常请求日志（包含所有域名）写入行数： {0:12}".format(self.hits)
                    msg_hits_error = "到目前为止错误请求日志（包含所有域名）写入行数： {0:12} ".format(self.hits_error)
                    print msg_normal
                    recordLog(msg_normal)
                    print msg_error
                    recordLog(msg_error)
                    print msg_bw
                    recordLog(msg_bw)
                    print msg_hits
                    recordLog(msg_hits)
                    print msg_hits_error
                    recordLog(msg_hits_error)

                    for domain in self.domain_dict.keys():

                        d_hits_5min  = self.domain_dict[domain]['hits_5min'] = self.domain_dict[domain]['hits'] - self.domain_dict[domain]['hits_5min_last']
                        d_hits_err_5min = self.domain_dict[domain]['hits_err_5min'] = self.domain_dict[domain]['hits_err'] - self.domain_dict[domain]['hits_err_5min_last']
                        d_bw = self.domain_dict[domain]['bw_5min'] = float((self.domain_dict[domain]['bw']/1024/1024/300) * 8)

                        domain_msg = "域名:{0:20}, 带宽:{1:12.2f} Mbps, 点击数:{2:8}, 错误点击数:{3:8}".format(domain,d_bw,d_hits_5min,d_hits_err_5min)
                        print domain_msg
                        recordLog(domain_msg)
                        self.domain_dict[domain]['hits_5min_last'] = self.domain_dict[domain]['hits']
                        self.domain_dict[domain]['hits_err_5min_last'] = self.domain_dict[domain]['hits_err']
                        self.domain_dict[domain]['bw'] = 0
                        #self.domain_dict[domain]['hits'] = 0
                        #self.domain_dict[domain]['hits_err'] = 0

                    self.hist_5min_last = self.hits
                    self.hist_error_5min_last = self.hits_error
                    self.bandwidth = 0
                    #self.hits_error = 0
                    #self.hits = 0
                ##控制写入速度
                #print self.this_time_stamp
                #print self.time_second_record
                if (self.this_time_stamp - self.time_second_record) == 1:
                    self.time_second_record = self.this_time_stamp
                    j = i - self.count_line_second
                    if j > self.max_seconds:
                        sleep_t = random.choice(self.sleep_time)
                        #print "1秒内大于 %s 行，sleep %s 秒" % (self.max_seconds,sleep_t)
                        time.sleep(sleep_t)
                        self.count_line_second = i

                ##按小时循切换日志文件
                if self.date_hour != self.nowdate_by_hour :
                    print "切换日志文件"
                    if 'linux' in (platform.platform()).lower():
                        old_log_filename = log_file_path + str(self.date_hour) + '.log'
                    else:
                        old_log_filename = str(self.date_hour) + '.log'

                    self.date_hour = self.nowdate_by_hour
                    f.flush()
                    f.close()
                    shutil.move(self.log_filename,old_log_filename)
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
    if 'linux' in (platform.platform()).lower():
        if not os.path.exists(log_file_path):
            os.makedirs(log_file_path)
        log_full_filename = os.sep.join([log_file_path,filename_log])
    else:
        log_full_filename = filename_log

    if os.path.exists(log_full_filename):
        try:
            os.remove(log_full_filename)
        except:
            print "无法移除文件"
            sys.exit(1)
    F = RandomGenLog(log_full_filename)
    F.WriteLog()

if __name__ == '__main__':
    fileList = ["ip.txt","domain.txt","agent.txt"]
    log_file_path = "/opt/cdn/nginx/logs/"
    filename_log = "access.log"
    output_log = "output.log"
    ##要写入多少行的日志
    writelog_by_min = 50000000
    ##每秒最大写入多少行,超过就sleep
    max_seconds = 100
    ##日志格式的月份有是字母，这里是为了映射： 数字 -》字母
    month_num_to_letter = {'01':'Jan','02':'Feb','03':'Mar','04':'Apr','05':'May','06':'Jun','07':'Jul','08':'Aug','09':'Sep','10':'Oct','11':'Nov','12':'Dec'}
    ## 月份 字母--》数字
    month_letter_to_num = dict([(v,k) for k,v in month_num_to_letter.iteritems()])

    main()

