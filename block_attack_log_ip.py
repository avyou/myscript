#!/usr/bin/python
#coding:utf-8
# monitor /var/log/nginx/hack/*.log and analysis attack ip then block it
# by avyou
# at 20140930

import time,datetime
import subprocess
import select
import re,os,sys
import smtplib
from email.mime.text import MIMEText

mail_to_list=['test@163.com']
mail_host="smtp.163.com"
mail_user="test@163.com"
mail_pass="123456"
mail_postfix="163.com"

##当前时间
nowtime = datetime.datetime.now()
##当前时间的上一分钟
lastmin = nowtime - datetime.timedelta(minutes=2)
## 转换成日志格式的时间，为了让awk 能使用，字符"/"会转成"\/"
log_nowtime_format = nowtime.strftime('%H:%M:%S')
log_lastmin_format = lastmin.strftime('%H:%M:%S')

log_day = nowtime.strftime('%Y-%m-%d')

#log_lastmin_format = "22/Sep/2014:06:24"
#log_nowtime_format = "22/Sep/2014:06:26"

hostname = os.popen('echo $HOSTNAME').read()

##要分析日志文件
nginx_log = "/var/log/nginx/hack/www.5usport.com_%s_sec.log" % log_day
#nginx_log = "0922.log"
nginx_p = "/usr/local/webserver/nginx/sbin/nginx"
watch_log = "/var/log/nginx/hack/block_nginx_ip.log"
f_suffix='.tmp'

##可疑用户访问错误达到的次数
errors_block = 10
##过期移除IP的间隔时间
expire_time = 7200

##生成ip文件的临时目录
ip_tmp_dir = "ip_tmp"
##nginx 封断IP的文件
block_ip_file = "/usr/local/webserver/tengine/conf/auto_block_ip.conf"
#block_ip_file = "auto_block_ip.conf"
##白名单规则
writelist = "1.1.1.1|2.2.2.2|192.168.111.\d{0,3}|192.168.3.\d{0,3}"

## awk命令，获取时间范围的日志
get_logs_cmd = r"""gawk -F '[ \[]' '$5>"%s" && $5<"%s"'  %s""" %(log_lastmin_format ,log_nowtime_format, nginx_log)
log_obj_output = os.popen(get_logs_cmd)
##f = subprocess.Popen(['tail','-n10000',log],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
##log_contents = f.stdout.readlines()
log_contents = log_obj_output.readlines()
#print log_contents

##编译正则
re_writelist_rules_match = re.compile(writelist)

##创建临时目录，如果不存在
if not os.path.exists(ip_tmp_dir):
    os.makedirs(ip_tmp_dir)

if not os.path.isfile(block_ip_file):
    with open(block_ip_file,'w') as f:
        f.write('')


def SendMail(sub,content):
    msg = MIMEText(content,_subtype='plain',_charset='gb2312')
    me="monitor"+"<"+mail_user+"@"+mail_postfix+">"
    msg['Subject'] = sub
    msg['From'] = me
    msg['To'] = ";".join(mail_to_list)
    try:
        print "send mail test ...."
        server = smtplib.SMTP()
        server.connect(mail_host)
        server.login(mail_user,mail_pass)
        server.sendmail(me, mail_to_list, msg.as_string())
        server.close()
        return True
    except Exception, e:
        print str(e)
        return False


def WriteLog(msg):
    with open(watch_log,"a") as f:
        f.write(msg)

def ReloadNginx(nginx_p):
    test_nginx_cmd = subprocess.Popen('%s -t' % nginx_p, shell=True, stdout=subprocess.PIPE, \
    	stderr=subprocess.STDOUT)
    nginx_status_list = test_nginx_cmd.stdout.readlines()
    re_ok = re.compile('ok')
    re_success = re.compile('successful')
    if (re_ok.search(nginx_status_list[0]) is not None) and (re_success.search(nginx_status_list)[1] is not None):
        subprocess.Popen('%s -s reload' % nginx_p, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

def suspiciousIPList():
    ## 可疑IP列表
    suspicious_iplist = []
    [ suspicious_iplist.append(log_line.split()[0]) for log_line in log_contents]
    print suspicious_iplist
    return suspicious_iplist

#print "suspicious_iplist: ",suspicious_iplist

def doBlockIP(iplist,errors_num):
    add_ip_status = 0
    if len(iplist) != 0:
        iplist.sort()
        ipdict = {}
        ##IP计数
        for ip in iplist :
            ipdict[ip] = ipdict.get(ip,0) + 1
        ##如果IP出错次数大于指定值，则进行相应操作
        log_ip = []
        for ip in ipdict.keys():
            if ipdict[ip] >= errors_num:
                #print ip, ipdict[ip]
                ##可疑IP生成文件名保存到指定目录
                genip = os.path.join(ip_tmp_dir,"".join([ip,'.tmp']))
                print genip
                with open(genip,'w') as f:
                    f.write("")
                ##可疑IP写入日志
                nowtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                msg = "At %s==>  suspicious IP %s access web.\n" % (nowtime,ip)
                WriteLog(msg)

                ##打开nginx 的阻止IP配置文件，写入IP
                try:
                    with open(block_ip_file,"a+") as f:
                        if ip not in [ each_ip.lstrip("deny ").rstrip(";\n") for each_ip in f ]:
                            f.write("".join(["deny ",ip,";\n"]))
                            log_ip.append(ip)
                            add_ip_status = 1

                except:
                    msg = "Write IP wrong,please check!\n"
                    WriteLog(msg)
                    break

        if add_ip_status == 1:
            ReloadNginx(nginx_p)
            nowtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            sub = u"monitor for analysis log file and add ip"
            msg = "(%s)At %s==> Add Some IP in block file: %s\n" %(hostname,nowtime,log_ip)
            SendMail(sub,msg)
            print 'nginx reload'
            add_ip_status = 0


def removeList():
    remove_iplist = []
    ## IP文件列表
    files_list = os.listdir(ip_tmp_dir)
    print "files_list: %s" % files_list
    ## 如果文件列表不为空就添加放到移除列表
    if len(files_list) != 0:
        for ip_file in files_list:
            if ip_file.endswith(f_suffix):
                ## 获取文件的时间
                mfile = time.localtime(os.stat(os.path.join(ip_tmp_dir,ip_file)).st_mtime)
                #print mtime
                mfile = time.strftime("%Y-%m-%d %H:%M:%S",mfile)
                file_time = datetime.datetime.strptime(mfile,'%Y-%m-%d %H:%M:%S')
                nowtime = datetime.datetime.now()
                ## IP文件到现在的时间,以秒为单位
                difftime_seconds = (nowtime - file_time).seconds
                print "ip file: %s" %ip_file
                ##print "difftime_time:  %s" %difftime_seconds
                ##print "expire_time: %s" %expire_time

                ## 如果IP文件时间超过指定的时间
                if difftime_seconds >= expire_time:
                    ip = ip_file.rstrip(f_suffix)
                    ## 放入到移除列表
                    remove_iplist.append(ip)
                    #print "delete file"
                    dfile = os.path.join(ip_tmp_dir,ip_file)
                    if os.path.isfile(dfile):
                        os.remove(dfile)
                        nowtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                        msg = "At %s==> Remove expire time IP: %s\n" %(nowtime,ip)
                        WriteLog(msg)

        print  "remove ip: ",remove_iplist
    return remove_iplist

############# 移除到期的IP ####################
def doRemoveIP(iplist):
    print "iplist: %s" %iplist
    del_ip_status = 0
    ##如果移除列表不为空，进行相应操作
    print "remove list: %s" % len(iplist)
    if len(iplist) != 0:
        with open(block_ip_file,'r') as in_f:
            ##获取原block_ipfile文件中的IP列表的集合
            set_block_ip_list = set([ip.lstrip("deny ").rstrip(";\n") for ip in in_f.readlines()])
            #print set_block_ip_list
            #print set(iplist)
            ## 获取保留的IP集合
            sip = set_block_ip_list - set(iplist)

        with open(block_ip_file,'w+')  as out_f:
            for ip in sip:
                out_f.write("".join(["deny ",ip,";\n"]))
                del_ip_status = 1

        if del_ip_status == 1:
            ReloadNginx(nginx_p)
            nowtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            sub = u"monitor for analysis log file and remove ip"
            msg = "(%s)At %s==> Remove some expire time IP: %s\n" %(hostname,nowtime,iplist)
            SendMail(sub,msg)
            print 'nginx reload'
            del_ip_status = 0


if __name__ == "__main__":
    ##可疑IP
    suspicious_iplist = suspiciousIPList()
    ##阻止IP
    print suspicious_iplist
    #print suspicious_iplist2
    doBlockIP(suspicious_iplist,errors_block)
    ##要移除的IP
    remove_ip_list = removeList()
    ##移除IP
    doRemoveIP(remove_ip_list)
