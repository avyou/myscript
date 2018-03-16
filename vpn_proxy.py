# -*- coding:utf-8 -*-
# by avyou at 20150517

import wx
import os
import re
import wmi
import threading,time
import urllib2
import random
import subprocess


class MyFrame(wx.Frame):
    def __init__(self, parent, id, title,size, pos=wx.DefaultPosition,
                     style=wx.DEFAULT_FRAME_STYLE |wx.SUNKEN_BORDER |wx.CLIP_CHILDREN):
        wx.Frame.__init__(self, parent,id, title,size=size,pos=pos,style=style)
        self.InitUI()
        self.MenuBarUI()
        self.StatusBarUI()
        self.SetIP()
        #self.GetInternetIP()

    def MenuBarUI(self):
        ## 菜单栏
        menuBar = wx.MenuBar()
        menu_file = wx.Menu()
        menu_about = wx.Menu()
        menuBar.Append(menu_file,u"文件")
        menuBar.Append(menu_about,u"帮助")
        self.SetMenuBar(menuBar)

    def InitUI(self):
        self.ID_BTN_LOCAL = wx.NewId()
        self.ID_BTN_VPN = wx.NewId()
        self.ID_BTN_change = wx.NewId()
        self.ID_BTN_readip = wx.NewId()

        panel = wx.Panel(self)
        sizer = wx.GridBagSizer(6,7)
        self.font = wx.Font(15, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        current_ip_label = wx.StaticText(panel, label=u"当前外网IP：")
        self.current_ip = wx.StaticText(panel)
        current_ip_label.SetFont(self.font)
        self.current_ip.SetFont(self.font)
        self.current_ip.SetForegroundColour("red")
        line = wx.StaticLine(panel)
        sizer.Add(current_ip_label,pos=(0,0),span=(1,1),flag=wx.TOP|wx.LEFT|wx.BOTTOM, border=5)
        sizer.Add(self.current_ip,pos=(0,1),span=(1,5),flag=wx.TOP|wx.LEFT|wx.BOTTOM, border=5)
        sizer.Add(line, pos=(1,0), span=(1,5), flag=wx.EXPAND|wx.TOP, border=15)

      ##创建一个静态Box
        tbox = wx.StaticBox(panel, label=u"本地网络")
        ##在静态Box 上设置 StaticBoxSizer, 样式为垂直对齐
        boxsizer = wx.StaticBoxSizer(tbox, wx.HORIZONTAL)
        ##创建复选框，并加入静态的boxsizer，距左、顶5px
        local_ip_label = wx.StaticText(panel, label="IP:")
        local_mask_label = wx.StaticText(panel, label=u"子网掩码:")
        local_gw_label = wx.StaticText(panel, label=u"网关:")
        self.local_ip_text = wx.TextCtrl(panel)
        self.local_mask_text = wx.TextCtrl(panel)
        self.local_gw_text = wx.TextCtrl(panel)
        local_set_btn = self.local_set_btn =  wx.Button(panel,label=u"切换",id = self.ID_BTN_LOCAL)
        boxsizer.Add(local_ip_label,flag=wx.LEFT|wx.TOP, border=10)
        boxsizer.Add(self.local_ip_text,flag=wx.LEFT|wx.TOP, border=10)
        boxsizer.Add(local_mask_label,flag=wx.LEFT|wx.TOP, border=10)
        boxsizer.Add(self.local_mask_text,flag=wx.LEFT|wx.TOP, border=10)
        boxsizer.Add(local_gw_label,flag=wx.LEFT|wx.TOP, border=10)
        boxsizer.Add(self.local_gw_text,flag=wx.LEFT|wx.TOP, border=10)
        boxsizer.Add(local_set_btn,flag=wx.LEFT|wx.TOP, border=10)

        tbox2 = wx.StaticBox(panel, label=u"VPN网络")
        ##在静态Box 上设置 StaticBoxSizer, 样式为垂直对齐
        boxsizer2 = wx.StaticBoxSizer(tbox2, wx.HORIZONTAL)
        ##创建复选框，并加入静态的boxsizer，距左、顶5px
        vpn_ip_label = wx.StaticText(panel, label="IP:")
        vpn_mask_label = wx.StaticText(panel, label=u"子网掩码:")
        vpn_gw_label = wx.StaticText(panel, label=u"网关:")
        self.vpn_ip_text = wx.TextCtrl(panel)
        self.vpn_mask_text = wx.TextCtrl(panel)
        self.vpn_gw_text = wx.TextCtrl(panel)
        vpn_set_btn = self.vpn_set_btn = wx.Button(panel,label=u"切换",id=self.ID_BTN_VPN)
        boxsizer2.Add(vpn_ip_label,flag=wx.LEFT|wx.TOP, border=10)
        boxsizer2.Add(self.vpn_ip_text,flag=wx.LEFT|wx.TOP, border=10)
        boxsizer2.Add(vpn_mask_label,flag=wx.LEFT|wx.TOP, border=10)
        boxsizer2.Add(self.vpn_mask_text,flag=wx.LEFT|wx.TOP, border=10)
        boxsizer2.Add(vpn_gw_label,flag=wx.LEFT|wx.TOP, border=10)
        boxsizer2.Add(self.vpn_gw_text,flag=wx.LEFT|wx.TOP, border=10)
        boxsizer2.Add(vpn_set_btn,flag=wx.LEFT|wx.TOP, border=10)


        tbox3 = wx.StaticBox(panel, label=u"DNS地址")
        boxsizer3 = wx.StaticBoxSizer(tbox3, wx.HORIZONTAL)
        local_dns1_label3 = wx.StaticText(panel, label="DNS1:")
        local_dns2_label3 = wx.StaticText(panel, label="DNS2:")
        self.local_dns1_text3 = wx.TextCtrl(panel)
        self.local_dns2_text3 = wx.TextCtrl(panel)
        boxsizer3.Add(local_dns1_label3,flag=wx.LEFT|wx.TOP, border=10)
        boxsizer3.Add(self.local_dns1_text3,flag=wx.LEFT|wx.TOP, border=10)
        boxsizer3.Add(local_dns2_label3,flag=wx.LEFT|wx.TOP, border=10)
        boxsizer3.Add(self.local_dns2_text3,flag=wx.LEFT|wx.TOP, border=10)

        getip_url_label = wx.StaticText(panel, label=u"获取外网IP的URL：")
        self.getip_url = wx.TextCtrl(panel)

        self.vpn_ping_label = wx.StaticText(panel, label=u"Ping 值：")
        self.vpn_ping = wx.TextCtrl(panel)

        self.Btn_change_ip = wx.Button(panel,label=u"变更IP",id=self.ID_BTN_change)
        self.Btn_readip = wx.Button(panel,label=u"读取外网IP",id=self.ID_BTN_readip)
        Btn_local_save = wx.Button(panel,label=u"保存配置")
        Btn_exit = wx.Button(panel,label=u"退出")

        sizer.Add(boxsizer, pos=(2, 0), span=(1,5),flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT , border=10)
        sizer.Add(boxsizer2, pos=(3, 0), span=(1,5),flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT , border=10)
        sizer.Add(boxsizer3, pos=(4, 0), span=(1,5),flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT , border=10)
        sizer.Add(getip_url_label, pos=(5, 0), span=(1,1),flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT , border=10)
        sizer.Add(self.getip_url, pos=(5, 1), span=(1,2),flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT , border=10)
        sizer.Add(self.vpn_ping_label, pos=(5, 3), span=(1,1),flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT , border=10)
        sizer.Add(self.vpn_ping, pos=(5, 4), span=(1,1),flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT , border=10)
        sizer.Add(self.Btn_change_ip, pos=(7, 0), span=(1,1),flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT , border=5)
        sizer.Add(self.Btn_readip, pos=(7, 1), span=(1,1),flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT , border=5)
        sizer.Add(Btn_local_save, pos=(7, 2), span=(1,1),flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT , border=5)
        sizer.Add(Btn_exit, pos=(7, 3), span=(1,1),flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT , border=5)

        sizer.AddGrowableCol(1,1)
        panel.SetSizer(sizer)


        Btn_exit.Bind(wx.EVT_BUTTON,self.OnExit)
        Btn_local_save.Bind(wx.EVT_BUTTON,self.OnSave)
        self.Bind(wx.EVT_BUTTON,self.OnChangeIP,id=self.ID_BTN_change)
        self.Bind(wx.EVT_BUTTON,self.OnReadInternetIP,id=self.ID_BTN_readip)
        self.Bind(wx.EVT_BUTTON,self.OnSetNet,id=self.ID_BTN_LOCAL)
        self.Bind(wx.EVT_BUTTON,self.OnSetNet,id=self.ID_BTN_VPN)

    def OnExit(self, event):
        self.Destroy()
        self.Close()


    def OnSave(self,event):
        config_dict = {"local_net":{},"vpn_net":{},"dns":{}}
        local_ip = self.local_ip_text.GetValue()
        local_mask = self.local_mask_text.GetValue()
        local_gw = self.local_gw_text.GetValue()
        vpn_ip = self.vpn_ip_text.GetValue()
        vpn_mask = self.vpn_mask_text.GetValue()
        vpn_gw = self.vpn_gw_text.GetValue()
        dns1 = self.local_dns1_text3.GetValue()
        dns2 = self.local_dns2_text3.GetValue()
        getip_url = self.getip_url.GetValue()
        vpn_ping = self.vpn_ping.GetValue()

        local_net = config_dict["local_net"]
        local_net["ip"] = local_ip
        local_net["netmask"] = local_mask
        local_net["gateway"] = local_gw

        vpn_net = config_dict["vpn_net"]
        vpn_net["ip"] = vpn_ip
        vpn_net["netmask"] = vpn_mask
        vpn_net["gateway"] = vpn_gw

        dns = config_dict["dns"]
        dns["dns1"] = dns1
        dns["dns2"] = dns2

        config_dict["url"] = getip_url
        config_dict["vpn_ping"] = vpn_ping
        output = open(config_file,'wb')
        import pickle
        pickle.dump(config_dict,output)
        output.close()

    def ReadSystemIP(self):
        import netifaces
        uids = netifaces.interfaces()
        for uid in uids:
            gwuid = netifaces.gateways()["default"][netifaces.AF_INET][1]
            gw = netifaces.gateways()["default"][netifaces.AF_INET][0]
            if gwuid != uid:
                continue
            intface_info = netifaces.ifaddresses(uid)
            print intface_info
            #mac_addr =  intface_info[netifaces.AF_LINK][0]["addr"]
            netmask =  intface_info[netifaces.AF_INET][0]["netmask"]
            ip_addr =  intface_info[netifaces.AF_INET][0]["addr"]

            self.local_ip_text.SetValue(ip_addr)
            self.local_mask_text.SetValue(netmask)
            self.local_gw_text.SetValue(gw)

            self.vpn_mask_text.SetValue("255.255.0.0")
            self.vpn_gw_text.SetValue("192.168.3.10")
            self.getip_url.SetValue("http://1111.ip138.com/ic.asp")
            self.local_dns1_text3.SetValue("223.5.5.5")
            self.local_dns2_text3.SetValue("202.96.128.166")
            self.vpn_ping.SetValue("10.4.0.90")

    def SetIP(self):
        if os.path.exists(config_file):
            import pickle
            reader = pickle.load(open(config_file, 'rb'))
            if not reader.get("local_net"):
                self.ReadSystemIP()
            else:
                try:
                    self.local_ip_text.SetValue(reader.get("local_net")["ip"])
                    self.local_mask_text.SetValue(reader.get("local_net")["netmask"])
                    self.local_gw_text.SetValue(reader.get("local_net")["gateway"])

                    self.vpn_ip_text.SetValue(reader.get("vpn_net")["ip"])
                    self.vpn_mask_text.SetValue(reader.get("vpn_net")["netmask"])
                    self.vpn_gw_text.SetValue(reader.get("vpn_net")["gateway"])

                    self.local_dns1_text3.SetValue(reader.get("dns")["dns1"])
                    self.local_dns2_text3.SetValue(reader.get("dns")["dns2"])

                    self.getip_url.SetValue(reader.get("url"))
                    self.vpn_ping.SetValue(reader.get("vpn_ping"))
                except:
                    self.ReadSystemIP()
        else:
            self.ReadSystemIP()

    def GetInternetIP(self):
        getip_url = self.getip_url.GetValue()
        print getip_url
        # headers = random.choice(agents_list)
        # req = urllib2.Request(getip_url,headers=headers)
        # print req
        try:
            response = urllib2.urlopen(getip_url,timeout=10)
            souce = response.read()
            response.close()
            print souce
            ret = re.findall("<center>(.*)</center>", souce)[0]
            print ret
        except Exception, e:
            ret = u'获取外网IP失败'

        if "14.23.102.146" in ret:
            self.current_ip.SetLabel(ret)
            self.current_ip.SetForegroundColour("Black")
        else:
            self.current_ip.SetLabel(ret)
            self.current_ip.SetForegroundColour("red")

    def OnReadInternetIP(self,event):
        self.Btn_readip.Disable()
        self.GetInternetIP()
        self.Btn_readip.Enable()

    def OnSetNet(self,event):
        eid =  event.GetId()
        if eid == self.ID_BTN_LOCAL:
            ip = [self.local_ip_text.GetValue()]
            mask = [self.local_mask_text.GetValue()]
            gw = [self.local_gw_text.GetValue()]
            self.local_set_btn.Disable()
            self.vpn_set_btn.Enable()
            self.Btn_change_ip.Disable()
            self.SetStatusText(u"当前网络: 公司内网",0)
        else:
            ip = [self.vpn_ip_text.GetValue()]
            mask = [self.vpn_mask_text.GetValue()]
            gw = [self.vpn_gw_text.GetValue()]
            self.vpn_set_btn.Disable()
            self.local_set_btn.Enable()
            self.Btn_change_ip.Enable()
            self.SetStatusText(u"当前网络: VPN网络",0)

        dns1 = self.local_dns1_text3.GetValue()
        dns2 = self.local_dns2_text3.GetValue()
        arrDNSServers = [dns1,dns2]
        wmiService = wmi.WMI()
        colNicConfigs = wmiService.Win32_NetworkAdapterConfiguration(IPEnabled = True)
        print colNicConfigs
        if len(colNicConfigs) < 1:
            print u"没有可用的网卡"
        print colNicConfigs[0]
        objNicConfig = colNicConfigs[0]

        GatewayCostMetrics = [1]
        intReboot = 0
        returnValue = objNicConfig.EnableStatic(IPAddress = ip, SubnetMask = mask)
        if returnValue[0] == 0:
            print '成功设置IP'
        elif returnValue[0] == 1:
            print '  成功设置IP'
            intReboot += 1
        else:
            print u'修改IP失败(IP设置发生错误)'
            self.SetStatusText(u"修改IP失败(IP设置发生错误)",0)
            ##exit()

        returnValue = objNicConfig.SetGateways(DefaultIPGateway = gw, GatewayCostMetric = GatewayCostMetrics)
        if returnValue[0] == 0:
            print '  成功设置网关'
        elif returnValue[0] == 1:
            print '  成功设置网关'
            intReboot += 1
        else:
            print '修改IP失败(网关设置发生错误)'
            self.SetStatusText(u"修改IP失败(网关设置发生错误)",0)
            ##exit()

        returnValue = objNicConfig.SetDNSServerSearchOrder(DNSServerSearchOrder = arrDNSServers)
        if returnValue[0] == 0:
            print '  成功设置DNS'
        elif returnValue[0] == 1:
            print '  成功设置DNS'
            intReboot += 1
        else:
            print '修改IP失败(DNS设置发生错误)'
            self.SetStatusText(u"修改IP失败(DNS设置发生错误)",0)
            ##exit()

        if intReboot > 0:
            print '需要重新启动计算机'

    def OnChangeIP(self,event):
        self.Btn_change_ip.Disable()
        self.current_ip.SetLabelText(u"请稍等...")
        vpn_ping = self.vpn_ping.GetValue()
        #subprocess.Popen("ping -n 8  %s" % vpn_ping , shell=True)
        os.system('ping -t  %s' %vpn_ping)
        self.GetInternetIP()
        self.Btn_change_ip.Enable()

    def StatusBarUI(self):
        self.statusbar = CustomStatusBar(self)
        self.SetStatusBar(self.statusbar)


class CustomStatusBar(wx.StatusBar):
    def __init__(self,parent):
        wx.StatusBar.__init__(self, parent, -1)
        self.SetFieldsCount(2)
        self.SetStatusWidths([-5,-1])
        self.sizeChanged=True
        self.SetStatusText("by avyou",1)

if __name__ == "__main__":
    agents_list = [{'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:22.0) Gecko/20150328 Firefox/32.0'},
        {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36'},
        {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'}]

    config_file = "C:\\vpn_config.db"
    app = wx.App()
    frame = MyFrame(None,-1,u"外网IP切换工具",(650,500))
    app.SetTopWindow(frame)
    frame.Center()
    frame.Show()
    app.MainLoop()

