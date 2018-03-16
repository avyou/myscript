#!/usr/bin/env python
# coding:utf-8
# rewrite for watch_web.py
# function:  protect the web site directory from illegal upload the PHP file
# by avyou at 2016-01-05

import pyinotify
import logging
from logging.handlers import RotatingFileHandler
import os,time,io,subprocess
from shutil import move
import redis
import hashlib

## 主要监控类，定义了监控的触发事件（添加|修改|移动),并启动监控。 
class FileWatcher:
    def start_watch(self, watch_dir, callback):
        wm = pyinotify.WatchManager()
        handler = EventHandler(callback)
        ##self.notifier = pyinotify.Notifier(wm, handler)
        ## 排除文件或目录
        excl = pyinotify.ExcludeFilter(excl_file)
        notifier = pyinotify.ThreadedNotifier(wm,handler)
        ## 触发的事件类型
        mask = (pyinotify.IN_CREATE | pyinotify.IN_MODIFY | pyinotify.IN_DELETE
                | pyinotify.IN_DELETE_SELF | pyinotify.IN_MOVED_FROM
                | pyinotify.IN_MOVED_TO)

        ## auto_add 为自动添加创建的目录或文件到监控
        wm.add_watch(watch_dir, mask,auto_add=True,rec=True,exclude_filter=excl)
        notifier.loop()

class EventHandler(pyinotify.ProcessEvent):

    def __init__(self,callback):
        self.event_callback = callback

        self.initFile(cdir=backup_dir)
        self.initFile(cdir=monitor_dir)
        self.initFile(cdir=log_dir)
        self.initFile(status_file=global_status_file,status='0')
        self.initFile(status_file=del_status_file,status='1')
        self.modify_list = []
        self.create_list = []

        self.diffLogFile()

    ##初始化目录和文件
    def initFile(self,status_file=None,cdir=None,status=1):
        if cdir is not None and not os.path.isdir(cdir):
            os.makedirs(cdir)
        if status_file is not None and not os.path.exists(status_file):
            with open(status_file,'w') as f:
                f.write(status)

    ### 日志定义
    def handlerLogger(self,logger_name,log_file,level=logging.DEBUG):

        #log_format = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s'
        #log_fmt = '%a, %d %b %Y %H:%M:%S'

        #logging.basicConfig(level=logging.DEBUG,format=log_format,
        #        datefmt=log_fmt,
                #filename=logFile,
        #        filemode='a')

        log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(filename)s(%(lineno)d) %(message)s')
        handler = RotatingFileHandler(log_file,mode='a', maxBytes=5*1024*1024, 
                                 backupCount=10, encoding=None, delay=0)
        handler.setLevel(level)
        handler.setFormatter(log_formatter)
        logger = logging.getLogger(logger_name)
        logger.addHandler(handler)

    ##多日志文件调用
    def diffLogFile(self):
        self.handlerLogger('log1',logFile_warn)
        self.handlerLogger('log2',logFile_info)
        self.log1 = logging.getLogger('log1')
        self.log2 = logging.getLogger('log2')
        self.log1.warning('start monitor {0} directory...\n'.format(watch_dir))
        self.log2.warning('start monitor {0} directory...\n'.format(watch_dir))

 
    ##获取文件的md5值 
    def checkMd5(self,afile):
        m = hashlib.md5()
        file = io.FileIO(afile,'r')
        bytes = file.read(1024)
        while(bytes != b''):
            m.update(bytes)
            bytes = file.read(1024)
        file.close()
        md5value = m.hexdigest()
        return  md5value

    ##比较md5
    def compareMd5(self,afile):
        if robj.get(afile) != self.checkMd5(afile):
            return False
        return True

    ##禁止上传
    def disableUpload(self,status_file):
        with open(status_file,'w') as f:
            f.write('1') 
    ##开启上传
    def allowUpload(self,status_file):
        with open(status_file,'w') as f:
            f.write('0') 
        
    ###只监控指定后缀的文件类型或目录(排除其他所有文件)
    def __call__(self, event):
        if os.path.splitext(event.name)[1]  in file_suffixes or os.path.isdir(event.pathname):
            super(EventHandler, self).__call__(event)

    ######## 监控事件处理 ##############
    def process_IN_MODIFY(self, event):
        #self.monitorHandler(event)
        if os.path.exists(event.pathname):
            msg = '有文件或目录被修改'
            self.HandlerAction(event,msg)

    def process_IN_CREATE(self, event):
        #self.monitorHandler(event)
        if os.path.exists(event.pathname):
            msg = '有文件或目录被创建'
            self.HandlerAction(event,msg)

    def process_IN_MOVED_TO(self, event):
        #self.monitorHandler(event)
        msg = '有文件或目录被移动'
        self.HandlerAction(event,msg)

    def process_IN_DELETE(self, event):
        #self.monitorHandler(event)
        self.log1.warning('{0}({1}):{2}'.format('有文件或目录被删除',event.maskname,event.pathname))

    def HandlerAction(self,event,msg):
        fattrib = os.popen("ls -dl --time-style='+%Y-%m-%d %H:%M:%S' {0}".format(event.pathname)).readline()
        self.log2.warning('{0}({1}){2}:\n{3}'.format(msg,event.maskname,'文件属性',fattrib))
        ##项目名称
        projectName = [i for i in watch_dir if i in event.path ][0].split(os.sep)[-1]
        ##上传开关文件
        status_file = "{0}/{1}{2}".format(monitor_dir,projectName,status_file_suffix)
        #print  status_file

        ##如果开关文件不存在，则创建
        if not os.path.exists(status_file):
            with open(status_file,'w') as f:
                f.write('1') 

        ##读取开关文件
        with open(status_file) as f1:
            upload_status = int(f1.read())

        with open(global_status_file) as f2:
            global_status = int(f2.read())

        with open(del_status_file) as f3:
            del_status = int(f3.read())

        ##如果全局时间状态开启,且对应项目的防上传状态开启,则校验文件，重新拉取，或上传的文件会被移动到对应的备份目录
        if global_status == 1:
            if upload_status == 1: ##and global_status == 1:
                ##print "in",event.maskname, event.pathname
                ## 校验文件md5值比较，如果不为true,则进行备份、重新拉取或删除操作
                if not  os.path.isdir(event.pathname) and not self.compareMd5(event.pathname):
                    ## 定义备份文件全路径名
                    bakfile = ''.join([backup_dir,event.pathname,'_',time.strftime("%Y-%m-%d-%H%M%S", time.localtime())])
                    ## 备份目录
                    bakfile_dir = os.path.dirname(bakfile)
                    if not os.path.isdir(bakfile_dir):
                        os.makedirs(bakfile_dir)
                    msg = msg + '(可能非法)'
                    self.log1.warning('{0}({1}){2}:\n{3}'.format(msg,event.maskname,'文件属性',fattrib).rstrip())

                    ##如果从redis 获取不到对应文件的md5值(None), 直接移除
                    if robj.get(event.pathname) is None:
                        try:
                            ##移动文件到备份目录
                            if del_status == 1:
                                ##print 'del: %s,%s' % (event.maskname,event.pathname)
                                #os.popen("mv %s %s" %(event.pathname,bakfile))
                                move(event.pathname, bakfile)
                                self.log1.warning('{0}:{1}\n'.format('校验失败，已移至',bakfile))
                            else:
                                self.log1.warning('校验失败.\n')
                        except:
                            pass
                    else:
                        try:
                            ##上传文件的尾部路径
                            src_file_suff = event.pathname.replace(rsync_www,'')
                            self.allowUpload(status_file)
                            ##print "rsync file ...%s" %event.pathname
                            ##同步拉取文件, 达到防篡改的目的
                            ## eg: rsync -avrtuz backuper@192.168.111.111::www/depoytest/abc/a1.txt
                            ##              --password-file=/etc/rsync_111.111.pass  /data/www/depoytest/abc/a1.txt
                            #print src_file_suff
                            #print rsync_user,src_host,pass_file,event.pathname
                            subprocess.Popen('rsync -avz  {0}@{1}::www{2} --password-file={3} {4}'.format(rsync_user,src_host,
                                                                                                          src_file_suff,pass_file,event.pathname), shell=True)
                            ##关闭上传
                            self.disableUpload(status_file)
                        except:
                            ##print "rsync file failure...%s" %event.pathname
                            ##拉取失败，则移除
                            if del_status == 1:
                                move(event.pathname, bakfile)
                                self.log1.warning('{0}:{1}\n'.format('拉取失败，已移至',bakfile))
                            else:
                                self.log1.warning('拉取失败.\n')
                            self.disableUpload(status_file)
                            #print event.maskname,'==>',event.pathname

if __name__ == '__main__':

    ##监控目录列表
    watch_dir = ['/data/www/depoytest','/data/www/mytest'
                ]

    ## 备份主目录
    backup_dir = '/backup/watch_web/www'
    ##日志目录
    log_dir = '/backup/watch_web/log'
    ## 监控状态目录
    monitor_dir = '/data/www/monitor'
    ## 监控的文件类型
    file_suffixes = ['.php']
    ## 警告的日志文件
    logFile_warn = os.path.join(log_dir,'watch_web_warn.log')
    ## 一般信息日志文件
    logFile_info = os.path.join(log_dir,'watch_web_info.log')
    ## 全局上传开关文件
    global_status_file = os.path.join(monitor_dir,'global_uploadBlock.conf')
    ## 是否删除校验失败或者拉取失败的文件
    del_status_file = os.path.join(monitor_dir,'del_status_file.conf')
    ## 排除列表文件
    excl_file = os.path.join(monitor_dir, 'exclude.lst')
    ## 上传开关文件的后缀
    status_file_suffix = '_uploadBlock.conf'
    rsync_user = 'backuper'
    pass_file = '/etc/rsync_X.pass'
    src_host = '192.168.X.X'
    rsync_www = '/data/www'
    ##连接 redis
    redis_pool = redis.ConnectionPool(host='192.168.X.X',port=6379,db=10,password='123456')
    robj = redis.Redis(connection_pool=redis_pool)
    f = FileWatcher()
    f.start_watch(watch_dir,None)
