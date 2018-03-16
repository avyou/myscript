#!/usr/bin/python
# --* coding:utf-8 *--
# Check PHP files in the directory
# by avyou
# write at 2015-03-07
# last update 2015-04-03

import hashlib
import tempfile
import os,sys
import os.path
import shelve
import shutil
import smtplib
from email.mime.text import MIMEText
import urllib
import urllib2
import fnmatch
import re
import socket

reload(sys)
sys.setdefaultencoding('utf-8')

class VerifyPHPFile(object):
    def __init__(self,site_name,check_dir,include_files,exclude_dir,tfile,dbfile,db_plaintext):
        self.site_name = site_name
        self.check_dir = check_dir
        self.include_files = include_files
        self.exclude_dir = exclude_dir
        self.dbfile = dbfile
        self.tfile = tfile
        self.db_plaintext = db_plaintext
        self.alist = []
        self.mlist = []
        self.dlist = []
        self.hostname = socket.gethostbyname_ex(socket.gethostname()) [0]
        self.IP = socket.gethostbyname_ex(socket.gethostname()) [2][0]


    ##遍历目录树下的文件
    # def visitFunc(self,tfile,exclude_dir,dirname,names):
    #     for nfile in names:
    #         subname = os.path.join(dirname,nfile)
    #         if os.path.isfile(subname):
    #             if subname.endswith(".php"):
    #             ##将指定类型的所有文件写入临时文件
    #                 with open(tfile,'a') as f:
    #                     f.write(subname+'\n')


    ##遍历目录树下的文件,添加文件过滤和目录排除
    def checkPHPFile(self,tfile,check_dir,include_files,exclude_dir):
        #print "include", include_files
        #print "exclude_dir", exclude_dir
        includes = r'|'.join([fnmatch.translate(x) for x in include_files])
        excludes = r'|'.join([fnmatch.translate(x) for x in exclude_dir]) or r'$.'

        for root, dirs, files in os.walk(check_dir):
            dirs[:] = [os.path.join(root, d) for d in dirs]
            dirs[:] = [d for d in dirs if not re.match(excludes, d)]

            files = [os.path.join(root, f) for f in files]
            files = [f for f in files if not re.match(excludes, f)]
            files = [f for f in files if re.match(includes, f)]

            with open(tmpfile,'a') as tf:
                for fname in files:
                    #print fname
                    tf.write(fname+'\n')

    ##比较字典文件
    def diff_db(self,dbfile,db_plaintext,tfile):
        ##如果临时文件不存在，返回
        if not os.path.exists(tfile):
            return
        ##如果字典数据文件不存在，初始化已校验后的数据到字典文件
        if not os.path.exists(dbfile):
            dbfile_dict  = shelve.open(dbfile)
            if os.path.exists(db_plaintext):
                os.remove(db_plaintext)
            with open(db_plaintext,'a') as f:
                for line in open(tfile):
                    line = line.split('\n')[0]
                    #dbfile_dict[line] = check_file(line,hasher)
                    dbfile_dict[line] = hashlib.md5(open(line, 'rb').read()).hexdigest()
                    #print dbfile_dict[line]
                    f.write('%s\t%s%s' %(line,dbfile_dict[line],'\n'))

        ## 打开已存在的字典数据文件进行比较
        else:
            dbfile_dict  = shelve.open(dbfile)
            db_plaintext_tmp = tempfile.mktemp()
            dbfile_tmp = tempfile.mktemp()
            ##打开当前的正检查的生临时字典文件
            current_check_dict = shelve.open(dbfile_tmp)
            with open(db_plaintext_tmp,'a') as f:
                ##循环到扫描生成的文件列表
                for efile in open(tfile):
                    efile = efile.split('\n')[0]
                    #current_check_dict[efile] = check_file(efile,hasher)
                    ##文件对应校验码，并写入临时数据字典
                    current_check_dict[efile] = hashlib.md5(open(efile, 'rb').read()).hexdigest()
                    #print current_check_dict[efile]
                    ##文件对应关系写入文明文件
                    f.write('%s\t%s%s' %(efile,current_check_dict[efile],'\n'))
                    ## 如果原字典数据中存在扫描到的文件，并且校验码不一致，这判断为修改内容，存入修改列表中。
                    if dbfile_dict.has_key(efile):
                        if dbfile_dict[efile] != current_check_dict[efile]:
                            #print "X different file: %s" % efile
                            self.mlist.append(efile)
                    else:
                        ##如果原字典数据中没有扫描到的文件，判断为新加文件，存入添加列表中
                        #print "+ new add file: %s" % efile
                        self.alist.append(efile)
            ##扫描原字典，如果原字典中的文件不在当前扫描后的字典中，判断为文件被删除，存入删除列表中
            for oefile in dbfile_dict:
                if not current_check_dict.has_key(oefile):
                    if not os.path.isfile(oefile):
                        #print "- del file: %s" % oefile
                        self.dlist.append(oefile)
            ##更新数据字典
            if os.path.exists(dbfile):
                os.remove(dbfile)
                shutil.move(dbfile_tmp,dbfile)
            ##更新文明文件
            if os.path.exists(db_plaintext):
                os.remove(db_plaintext)
                shutil.move(db_plaintext_tmp,db_plaintext)

            current_check_dict.sync()
            current_check_dict.close()

    ##打印的报告内容
    def reportContent(self,send_media):
        # self.changed_file_dict = {
        #     'add':self.alist,
        #     'modify': self.mlist,
        #     'delete': self.dlist,
        # }
        #print self.alist
        #print self.mlist
        #print self.dlist

        ##返回要输出的列表内容
        add_info = self.get_files_print(u"增加",self.alist)
        modify_info = self.get_files_print(u"修改",self.mlist)
        delete_info = self.get_files_print(u"删除",self.dlist)
        msg = ""
        header = ""
        file_changed = False
        for seq,i in enumerate([add_info,modify_info,delete_info]):
            if i is not None:
                header = u"提示，网站文件有变动(%s)。\n主机名: %s\nIP: %s\n检查目录：%s\n" % (self.site_name,self.hostname,self.IP,self.check_dir)
                if send_media == "mail":
                    msg = msg + i[0] + "\n"
                if send_media == "sms":
                    msg = msg + i[1] + "\n"
                ##判断文件是否有变动，要发送邮件或短信
                file_changed = True
        return header+msg,file_changed

    ## 返回打印增加、修改、删除的内容
    def get_files_print(self,addstr,flist):
        num = len(flist)
        if num != 0:
            separate = u"################# %s了%s个文件 #######################" % (addstr,num)
            body = ""
            for num_seq,afile in  enumerate(flist):
                if flist is not self.dlist:
                    body =  "".join([body,str(num_seq+1),'、 ',os.popen("ls -l %s" %afile).read()])
                else:
                    body =  "".join([body,str(num_seq+1),'、 ',afile,"\n"])
            mail_content = "\n".join([separate,body])
            sms_content = u"%s了%s个文件" % (addstr,num)
            return "\n"+mail_content,sms_content
    ##邮件发送
    def sendMail(self,content,sub):
        msg = MIMEText(content,_subtype='plain',_charset='gb2312')
        me="monitor"+"<"+mail_user+">"
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

    ##短信发送
    def sendSMS(self,message):
        for each_phone in to_phone_list:
            values = {'pw':password,
              'from':from_phone,
              'to':each_phone,
              'message':message}
            data = urllib.urlencode(values)
            try:
                conn = urllib2.urlopen(fetionAPI,data)
                print conn.read()
            except Exception , e:
                print e

    def run(self):
        print u"---------------------- 检测%s目录中------------------------" % self.check_dir
        print u"检测的文件类型：%s" % ",".join([ i  for i in self.include_files])
        print u"排除的目录：%s"  % ",".join([ i  for i in self.exclude_dir if len(self.exclude_dir) != 0])
        try:
            #os.path.walk(self.check_dir,self.visitFunc,(self.tfile,self.exclude_dir))
            #self.visitPHPFile(self.tfile,self.check_dir,self.include_files,self.exclude_dir)
            self.checkPHPFile(self.tfile,self.check_dir,self.include_files,self.exclude_dir)
        except:
            print "walk dir has error"
            return
        else:
            ##调用比较文件
            self.diff_db(self.dbfile,self.db_plaintext,self.tfile)
            ##邮件报告
            msg_mail,file_changed_mail = self.reportContent("mail")
            #print msg_mail
            sub = u"提示，(%s)网站(%s)文件有变动！" % (self.hostname,self.site_name)
            if file_changed_mail  is True:
                self.sendMail(msg_mail,sub)

            ##短信报告
            msg_sms,file_changed_sms = self.reportContent("sms")
            if file_changed_sms  is True:
                self.sendSMS(msg_sms)
        print u"完成\n"

if __name__ == "__main__":

    ##需要检查目录、排除目录和网站名称，字典格式
    check_dir_dict = {
        "xxx":{
                  "scan":'/data/www/xxx',
                  "include":['*.php'],"exclude":["/data/www/xxx/xxx/logs",
                                                 "/data/www/xxxx/upload"]
        },
        "xxxx":{
                  "scan":'/data/www/xxxx',
                  "include":['*.php'],"exclude":["/data/www/xxx/data/template",
                                                 "/data/www/xxx/data/log",
                                                 "/data/www/xxx/data/attachment",
                                                 "/data/www/xxx/uc_server/data/logs",
                                                 "/data/www/xxx/source/plugin/dc_mall/data/cron.php",]
        },
    }

    ##生成的数据目录
    datadir = "check_data"
    mail_host="smtp.mytest.com"
    mail_user="alarm@mytest.com"
    mail_pass="xxxxxx"
    mail_postfix="mytest.com"
    mail_to_list=["zzf@mytest.com","test@mytest.com"]
    from_phone = '136xxxxxxx'
    to_phone_list = [ '139xxxxxxxx']
    #to_phone_list = [ '139xxxxxxx']
    password = '123456'
    ##短信发送的API url
    fetionAPI = "http://1.1.1.1:5500/api"

    ##循环进入扫描目录
    for site_name,site_dir in check_dir_dict.items():
        ##如果存在目录，扫描
        if os.path.exists(site_dir['scan']):
            if not os.path.exists(datadir):
                os.mkdir(datadir)
            ##扫描生成文件列表，临时文件
            if not os.path.exists('/tmp/cfp'):
                os.mkdir('/tmp/cfp')
            tmpfile = tempfile.mktemp(suffix='.txt',prefix='tmp',dir='/tmp/cfp')
            os.popen("find /tmp/cfp -name '*.txt' -type f -ctime +2 -exec /bin/rm -rf {} \;")
            #print tmpfile
            ##字典数据
            dbfile = '%s/%s_dict.db' %(datadir,site_name)
            ##文明数据
            db_plaintext = "%s/%s_dict.txt" %(datadir,site_name)
            ##生成检测实例
            checkFile = VerifyPHPFile(site_name,site_dir["scan"],site_dir["include"],site_dir["exclude"],tmpfile,dbfile,db_plaintext)
            ##调用run方法
            checkFile.run()
