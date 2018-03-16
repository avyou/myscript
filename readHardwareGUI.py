#coding:utf-8
# by avyou at 20151015
  
import wx
import os,sys,subprocess
import wmi
import threading,time
import wmi,zlib
#import time,platform
#from M2Crypto import RSA, BIO
from wx.lib.wordwrap import wordwrap
from base64 import b64decode,b64encode
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
  
str_key = "xxxxxxxxxxxxxxx"
  
class TreadA(threading.Thread):
  
    def __init__(self, window):
        threading.Thread.__init__(self)
        self.vpn_ping = window.vpn_ping
        self.Btn_change_ip = window.Btn_change_ip
        self.getip_url = window.getip_url
        self.current_ip = window.current_ip
        self.start()
  
    def run(self):
        wx.CallAfter(self.postTime)
  
    def postTime(self):
        pass
  
class MyFrame(wx.Frame):
    def __init__(self, parent, id, title,size, pos=wx.DefaultPosition,
            style=wx.DEFAULT_FRAME_STYLE |wx.SUNKEN_BORDER |wx.CLIP_CHILDREN):
        wx.Frame.__init__(self, parent,id, title,size=size,pos=pos,style=style)
        self.encrypt_define_str = b64encode(str_key)
        logo_icon = wx.EmptyIcon()
        img = wx.Bitmap("D:\\PyInstaller-3.0\\favicon.ico",wx.BITMAP_TYPE_ANY)
        logo_icon.CopyFromBitmap(img)
        self.SetIcon(logo_icon)
        self.InitUI()
        self.MenuBarUI()
        self.StatusBarUI()
  
    def MenuBarUI(self):
    ## 菜单栏
        menuBar = wx.MenuBar()
        menu_file = wx.Menu()
        menu_help = wx.Menu()
        menuBar.Append(menu_file,u"文件")
        menu_file.Append(wx.ID_OPEN,u"查看文件\tCtrl+O",help=u"打开硬件配置信息文件")
        menuBar.Append(menu_help,u"帮助")

        menu_help.Append(wx.ID_HELP,u"查看帮助",help=u"查看帮助")
        menu_help.Append(wx.ID_ABOUT,u"关于",help=u"关于程序")
        self.SetMenuBar(menuBar)
  
    def InitUI(self):
        self.panel = panel = wx.Panel(self)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        gsizer = wx.GridBagSizer(vgap=10,hgap=5)
 
 
        self.font = wx.Font(12, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        hw_info_label = wx.StaticText(panel, label=u"当前硬件配置信息：")
        hw_info_label.SetFont(self.font)
        line = wx.StaticLine(panel)
 
        text_mcode = wx.StaticText(panel,label=u"机器码:")
        text_cpu = wx.StaticText(panel,label="CPU:")
        text_mem = wx.StaticText(panel,label=u"内存:")
        text_disk = wx.StaticText(panel,label=u"硬盘:")
        text_network = wx.StaticText(panel,label=u"网卡信息")
 
        self.tc_mcode = wx.TextCtrl(panel,style=wx.TE_READONLY)
        self.tc_cpu = wx.TextCtrl(panel,style=wx.TE_READONLY)
        self.tc_mem = wx.TextCtrl(panel,style=wx.TE_READONLY)
        self.tc_disk = wx.TextCtrl(panel,style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.tc_network = wx.TextCtrl(panel,style=wx.TE_MULTILINE|wx.TE_READONLY)
 
        button_read = wx.Button(panel,label=u"读取")
        button_save = wx.Button(panel,label=u"保存")
        button_cancel = wx.Button(panel,label=u"退出")
  
  
        gsizer.Add(hw_info_label,pos=(0,0),span=(1,3),flag=wx.TOP|wx.LEFT|wx.BOTTOM,border=10)
        gsizer.Add(line,pos=(1,0),span=(1,5),flag=wx.EXPAND,border=10)
 
        gsizer.Add(text_mcode,pos=(2,0),span=(1,1),flag=wx.ALIGN_RIGHT|wx.TOP|wx.LEFT,border=10)
        gsizer.Add(text_cpu,pos=(3,0),span=(1,1),flag=wx.ALIGN_RIGHT|wx.TOP|wx.LEFT,border=10)
        gsizer.Add(text_mem,pos=(4,0),span=(1,1),flag=wx.ALIGN_RIGHT|wx.TOP|wx.LEFT,border=10)
        gsizer.Add(text_disk,pos=(5,0),span=(1,1),flag=wx.ALIGN_RIGHT|wx.TOP|wx.LEFT,border=10)
        gsizer.Add(text_network,pos=(7,0),span=(1,1),flag=wx.ALIGN_RIGHT|wx.TOP|wx.LEFT,border=10)
 
 
        gsizer.Add(self.tc_mcode,pos=(2,1),span=(1,4),flag=wx.TOP|wx.RIGHT|wx.EXPAND,border=10)
        gsizer.Add(self.tc_cpu,pos=(3,1),span=(1,4),flag=wx.EXPAND|wx.RIGHT|wx.TOP,border=10)
        gsizer.Add(self.tc_mem,pos=(4,1),span=(1,4),flag=wx.EXPAND|wx.RIGHT|wx.TOP,border=10)
        gsizer.Add(self.tc_disk,pos=(5,1),span=(2,4),flag=wx.EXPAND|wx.RIGHT|wx.TOP,border=10)
        gsizer.Add(self.tc_network,pos=(7,1),span=(3,4),flag=wx.EXPAND|wx.RIGHT|wx.TOP,border=10)
 
        gsizer.Add(button_read,pos=(10,2),span=(1,1),flag=wx.RIGHT|wx.TOP|wx.BOTTOM,border=10)
        gsizer.Add(button_save,pos=(10,3),span=(1,1),flag=wx.RIGHT|wx.TOP|wx.BOTTOM,border=10)
        gsizer.Add(button_cancel,pos=(10,4),span=(1,1),flag=wx.RIGHT|wx.TOP|wx.BOTTOM,border=10)
 
        gsizer.AddGrowableRow(7,1)
        gsizer.AddGrowableRow(6,1)
        gsizer.AddGrowableCol(1,1)
 
 
        hbox.Add(gsizer, proportion=1, flag=wx.ALL|wx.EXPAND, border=15)
        panel.SetSizer(hbox)
 
        button_read.Bind(wx.EVT_BUTTON,self.OnReadHardInfo)
        button_save.Bind(wx.EVT_BUTTON,self.OnGenHardwareText)
        button_cancel.Bind(wx.EVT_BUTTON,self.OnExit)
        self.Bind(wx.EVT_MENU,self.OnMenuViewFile,id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU,self.OnMenuHelp,id=wx.ID_HELP)
        self.Bind(wx.EVT_MENU,self.OnAbout,id=wx.ID_ABOUT)

    def OnMenuViewFile(self,event):
        rfile = os.sep.join([self.cur_file_dir(),fsave])
        try:
            subprocess.Popen(["explorer.exe",rfile], shell=True)
        except:
            msg = u"文件不存在，或打开文件 %s 发生错误" % fsave
            wx.MessageBox(msg, u"错误",style=wx.OK|wx.ICON_ERROR)
    def cur_file_dir(self):
         path = sys.path[0]
         if os.path.isdir(path):
             return path
         elif os.path.isfile(path):
             return os.path.dirname(path)

    def OnExit(self, event):
        self.Destroy()
        self.Close()

    def OnMenuHelp(self,event):
        import wx.lib
        import wx.lib.dialogs
        dialog_texts = u'''
        1. 本工具用于读取的电脑硬件配置做为公司资产部分统计和管理。

        2. 机器码是根据电脑硬件配置信息计算出来的唯一值，如果硬件配件发变更，请重新读取.

        3. 读取电脑硬件配置信息前，请先移除U盘等移动设备

        4. 要保存硬件配置信息到文件，请先点击读取再保存按钮.'''

        dialog = wx.lib.dialogs.ScrolledMessageDialog(None,dialog_texts, u"使用帮助",
                                                  pos=wx.DefaultPosition, size=(450,280))
        dialog.ShowModal()
        dialog.Destroy()

    def OnAbout(self,event):
        info = wx.AboutDialogInfo()
        # about_icon = wx.Icon('icons\Notepad.png', wx.BITMAP_TYPE_PNG)
        # info.SetIcon(about_icon)
        info.Name = "rHardware"
        info.Version = "1.0 Beta"
        info.Copyright = "(C) 2015 Python Geeks Everywhere"
        info.Description = wordwrap(u"本工具用于读取电脑硬件基本配置信息。",350, wx.ClientDC(self.panel))
        info.WebSite = ("http://www.5usport.com", u"5U体育")
        info.Developers = ["avyou,Using the python"]
        info.License = wordwrap(u"GPL", 500,
                            wx.ClientDC(self.panel))
        info.SetCopyright('(C) 2015 avyou')
        wx.AboutBox(info)
    def StatusBarUI(self):
        self.statusbar = CustomStatusBar(self)
        self.SetStatusBar(self.statusbar)
 
    def OnReadHardInfo(self,event):
        self.SetStatusText(u"读取中，请稍后...",0)
        try:
            self.c = wmi.WMI()
            mcode = self.getMachineCode(self.c)
            cpu = self.get_cpu_info(self.c)
            memory = self.get_memory_info(self.c)
            disk = self.get_disk_info(self.c)
            network  = self.get_network_info(self.c)
        except:
            wx.MessageBox(u"读取数据失败！",caption=u"错误消息",style=wx.OK|wx.ICON_ERROR)
            return

        self.tc_mcode.SetValue(mcode)
        self.tc_cpu.SetValue(cpu)
        self.tc_mem.SetValue(memory)
        self.tc_disk.SetValue(disk)
        self.tc_network.SetValue(network)
        self.SetStatusText(u"",0)
        self.SetStatusText(u"读取完成.",0)

    def OnGenHardwareText(self,event):
        mcode = self.tc_mcode.GetValue()
        cpu = self.tc_cpu.GetValue()
        mem = self.tc_mem.GetValue()
        disk = self.tc_disk.GetValue()
        network = self.tc_network.GetValue()
        if mcode == "" or cpu == "":
            wx.MessageBox(u"请先读取数据再保存！",caption=u"错误消息",style=wx.OK|wx.ICON_ERROR)
            return
        try:
            wfile = os.sep.join([self.cur_file_dir(),fsave])
            with open(wfile,"w") as f:
                f.writelines(u"############## 机器码 ###############\n%s\n" % mcode)
                f.writelines(u"############# CPU ################\n%s\n" % cpu)
                f.writelines(u"############# 内存 ##############\n%s\n" % mem)
                f.writelines(u"############# 硬盘 ##############\n%s\n" % disk)
                f.writelines(u"############# 网卡 ##############\n%s\n" % network)
            wx.MessageBox(u'成功保存到 %s !\n' % wfile,caption=u"提示",style=wx.OK|wx.ICON_INFORMATION)

        except:
            wx.MessageBox(u"写入文件失败！",caption=u"错误消息",style=wx.OK|wx.ICON_ERROR)

    def getMachineCode(self,c):
        try:
            cpu_code = "".join([  cpu.ProcessorId.strip() for cpu in c.Win32_Processor() ])
        except:
            cpu_code = None
        try:
            disk_code = "".join([ physical_disk.SerialNumber.strip() for physical_disk in c.Win32_DiskDrive()])
        except:
            disk_code = None
        try:
            board_code = "".join([ board_id.SerialNumber.strip() for board_id in c.Win32_BaseBoard()])
        except:
            board_code = None
        MachineCodeValid = [ i for i in [cpu_code,disk_code,board_code] if i is not None ]
            #print MachineCodeValid
        MachineCode = self.encrypt_define_str + "".join(MachineCodeValid)
        GenMachineCode = str(zlib.adler32(MachineCode)).lstrip("-")
        print GenMachineCode
        return GenMachineCode
  
  
    def get_memory_info(self,c):
        ##获取物理内存
        print "memory_info:"
        cs = c.Win32_ComputerSystem()
 
        MemTotal = int(cs[0].TotalPhysicalMemory) / 1024 / 1024
        MemTotalInfo= str(MemTotal) + "M"
        print MemTotalInfo
        return MemTotalInfo
 
    def get_disk_info(self,c):
        ##获取物理磁盘信息。
        print "disk_info:"
        tmplist = []
  
        for physical_disk in c.Win32_DiskDrive():
            if physical_disk.Size:
                diskinfo = str(physical_disk.Caption) + ' :\t' + str(long(physical_disk.Size) / 1024 / 1024 / 1024) + "G"
                tmplist.append(diskinfo)
        DiskInfo = "\n".join(tmplist)
        print DiskInfo
        return DiskInfo
 
    def get_cpu_info(self,c):
        ##获取CPU信息。
        print "cpu_info:"
        tmpdict = {}
        tmpdict["CpuCores"] = 0
        c = wmi.WMI()
        for cpu in c.Win32_Processor():
            tmpdict["CpuType"] = cpu.Name
            try:
                tmpdict["CpuCores"] = cpu.NumberOfCores
            except:
                tmpdict["CpuCores"] += 1
                tmpdict["CpuClock"] = cpu.MaxClockSpeed
        CPUInfo = str(tmpdict["CpuType"]) + "  " +  str(tmpdict["CpuCores"]) + "cores"
        print CPUInfo
        return CPUInfo
  
  
    def get_network_info(self,c):
        ##获取网卡信息
        print
        print "network_info:"
 
        tmplist = []
 
        for interface in c.Win32_NetworkAdapterConfiguration(IPEnabled=1):
            tmpdict = {}
            tmpdict["Description"] = interface.Description
            tmpdict["IPAddress"] = interface.IPAddress[0]
            tmpdict["IPSubnet"] = interface.IPSubnet[0]
            tmpdict["MAC"] = interface.MACAddress
            tmplist.append(tmpdict)
        t2 = []
        for i in tmplist:
            NetInfo =  i["Description"] + '\n' + \
                       '\t' + "MAC :" + '\t' + i["MAC"] + '\n' + \
                       '\t' + "IPAddress :" + '\t' + i["IPAddress"] + '\n' + \
                       '\t' + "IPSubnet :" + '\t' + i["IPSubnet"]
            t2.append(NetInfo)
        NetInfo = "\n".join(t2)
        print NetInfo
        return NetInfo
  
class CustomStatusBar(wx.StatusBar):
    def __init__(self,parent):
        wx.StatusBar.__init__(self, parent, -1)
        self.SetFieldsCount(2)
        self.SetStatusWidths([-6,-4])
        self.sizeChanged=True
        self.SetStatusText(u"提示，读取配置信息时，请勿插入U盘等移动设备。",1)

  
if __name__ == "__main__":
    fsave = "HardWareInfo.txt"
    app = wx.App()
    frame = MyFrame(None,-1,u"xxxxx - 电脑硬件配置信息",(700,500))
    app.SetTopWindow(frame)
    frame.Center()
    frame.Show()
    app.MainLoop()