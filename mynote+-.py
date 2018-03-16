#coding:utf-8
# by avyou
# at 2011-9
import wx
from wx import AboutDialogInfo
import sys,os,time
import codecs
import chardet
from wx.lib.wordwrap import wordwrap
import wx.lib
import wx.lib.dialogs
import wx.richtext as rt
reload(sys)


sys.setdefaultencoding("utf-8")
#print sys.getdefaultencoding()

### 装饰退出程序的函数
def CheckStep(funcEvent):
    def _CheckStep(self,*args,**kargs):
        NeedSave = self.CheckFileSaveStatus()
        if NeedSave is True:
            UserChooseSave = self.SaveFilePrompt()
            if UserChooseSave is True:
                self.OnSaveFile(*args,**kargs)
            elif UserChooseSave is None:
                return
        funcEvent(self,*args,**kargs)
    return _CheckStep

#### 检测文件的编码，传一个文件的完全路径，返回一个检测后的编码
def CheckFileCode(checkFile,charNum):
    FileName = os.path.basename(checkFile)
    FileObj = open(checkFile,'r')
    FileReadHead = FileObj.read(charNum)
    FileObj.close()
    FileChar = chardet.detect(FileReadHead)["encoding"]
            #print FileChar
    if str(FileChar).lower() == "gb2312":
        FileChar = "GBK"
    return FileChar

class CustomStatusBar(wx.StatusBar):
    def __init__(self,parent):
        wx.StatusBar.__init__(self, parent, -1)
        self.SetFieldsCount(3)
        self.SetStatusWidths([-2,-1,-1])
        self.sizeChanged=True
        self.Bind(wx.EVT_SIZE,self.OnSize)

        #self.SetStatusText(u"状态栏测试",0)
        self.SetStatusText(u"文件保存状态: ",1)
        self.timer=wx.PyTimer(self.Notify)
        self.timer.Start(1000)
        self.Notify()

    def Notify(self):
        t=time.localtime(time.time())
        st=time.strftime("%Y-%m-%d %H:%M:%S",t)
        self.SetStatusText(st,2)

    def OnSize(self,evt):
        self.sizeChanged=True
class FileDrop(wx.FileDropTarget):
    def __init__(self,textctrl,frame):
        wx.FileDropTarget.__init__(self)
        self.MainText = textctrl
        self.frame = frame
        self.MainTitle = u"我的记事本-"

    def OnDropFiles(self, x, y, filenames):

        for filepath in filenames:
            try:
                fchar = CheckFileCode(filepath,100)
                self.__OpenAndSetup(filepath,fchar)
                return
            except IOError, error:
                dlg = wx.MessageDialog(self.MainText, u'打开文件错误\n' + str(error))
                dlg.ShowModal()
                return
            except UnicodeDecodeError, error:
                try:
                    fchar = CheckFileCode(filepath,-1)
                    self.__OpenAndSetup(filepath,fchar)
                    return
                except UnicodeDecodeError, error:
                    dlg = wx.MessageDialog(None, 'u"不支持的文件类型或文件编码载入出错"\n' + str(error))
                    dlg.ShowModal()
                    return
    def __OpenAndSetup(self,fpath,fchar):
        flist = []
        with codecs.open(fpath, 'r',fchar) as f:
            for line in f.readlines():
                flist.append(line)
            FileContent = "".join(flist)
            self.MainText.SetValue(FileContent)
            filename = os.path.basename(fpath)
            self.frame.SetTitle(self.MainTitle+filename)
            self.frame.FilePath = fpath
            self.frame.TextContentChanaged = False
            self.frame.SetStatusBarText()

class MyNoteBookFrame(wx.Frame):
    def __init__(self):
        self.MainTitle = u"我的记事本-"
        self.DefaultFileName = u"无标题"

        #self.ID_Main = wx.NewId()
        wx.Frame.__init__(self,None,-1,title=self.MainTitle+self.DefaultFileName,size=(800,600))
        self.panel = panel = wx.Panel(self,-1)
        self.TextContentChanaged = False
        self.stext1 = u"文件的保存状态： "
        #self.kc_list = "324 325 326 327 328 329 330 331 332 333 370 387 388 390 391 392".split()

        logo_icon = wx.EmptyIcon()
        img = wx.Bitmap("ico\small1.ico",wx.BITMAP_TYPE_ANY)
        logo_icon.CopyFromBitmap(img)
        self.SetIcon(logo_icon)
        self.BookMenuBar()
        self.BookToolBar()
        self.BookText()
        self.BookMenuBar()
        self.statusOther = self.BookStatusBar()
        self.finddlg = None
        self.finddata = wx.FindReplaceData()
        self.Centre()


    def BookMenuBar(self):
        ######### 菜单栏与菜单 ####################################################################
        ##创建菜单
        menubar = wx.MenuBar()
        ##"文件"菜单
        menu_file = wx.Menu()
        menu_file.Append(wx.ID_NEW,u"新建\tCtrl+N",help=u"新建文件")
        menu_file.Append(wx.ID_OPEN,u"打开\tCtrl+O",help=u"打开文件")
        menu_file.Append(wx.ID_SAVE,u"保存\tCtrl+S",help=u"保存文件")
        menu_file.Append(wx.ID_SAVEAS,u"另存为",help=u"保存为另一个文件")
        menu_file.Append(wx.ID_PAGE_SETUP,u"页面设置",help=u"页面的相关设置")
        menu_file.AppendSeparator()
        menu_file.Append(wx.ID_EXIT,u"退出\tCtrl+Q",help=u"退出程序")
        ###"编辑"菜单
        menu_edit = wx.Menu()
        menu_edit.Append(wx.ID_UNDO,u"撤消\tCtrl+Z",help=u"撤消原先操作")
        menu_edit.AppendSeparator()
        menu_edit.Append(wx.ID_CUT,u"剪切\tCtrl+X",help=u"剪切内容")
        menu_edit.Append(wx.ID_COPY,u"复制\tCtrl+S",help=u"复制内容")
        menu_edit.Append(wx.ID_PASTE,u"粘贴\tCtrl+V",help=u"粘贴内容")
        menu_edit.Append(wx.ID_DELETE,u"删除\tDel",help=u"删除内容")
        menu_edit.AppendSeparator()
        menu_edit.Append(wx.ID_FIND,u"查找\tCtrl+F",help=u"查找内容")
        ID_FIND_NEXT = wx.NewId()
        menu_edit.Append(ID_FIND_NEXT,u"查找下一个\tF3",help=u"查找指定内容的下一个")
        menu_edit.Append(wx.ID_REPLACE,u"替换\tCtrl+H",help=u"替换内容")
        menu_edit.Append(wx.ID_FORWARD,u"转到\tCtrl+G",help=u"转到指定的内容")
        menu_edit.AppendSeparator()
        menu_edit.Append(wx.ID_SELECTALL,u"全选\tCtrl+A",help=u"选择全部的内容")
        self.ID_DATE_TIME = ID_DATE_TIME = wx.NewId()
        menu_edit.Append(ID_DATE_TIME,u"日期和时间\tF5",help=u"在本文件中插入时间日期")

        ########## "格式"菜单 ##############################
        menu_layout = wx.Menu()
        ID_LINE_FEED = wx.NewId()
        ##复选框菜单项
        self.AutoWordWarp = menu_layout.AppendCheckItem(ID_LINE_FEED,u"自动换行",help=u"自动换行")
        ##复选菜单项自动被选上
        #menu_layout.Check(ID_LINE_FEED,True)
        self.AutoWordWarp.Check(True)
        FontSetting = menu_layout.Append(-1,u"字体",help=u"字体设定")
        ID_BACKGROUND_COLOR = wx.NewId()
        menu_layout.Append(ID_BACKGROUND_COLOR,u"背景颜色",help=u"修改文本的背景颜色")
        ######### "查看"菜单 #################################
        menu_view = wx.Menu()
        ID_VIEW_TOOLSBAR = wx.NewId()
        ##复选框菜单项
        self.YesNoToolBar = menu_view.AppendCheckItem(ID_VIEW_TOOLSBAR,u"工具栏",help=u"显示工具栏")
        ##复选菜单项自动被选上
        menu_view.Check(ID_VIEW_TOOLSBAR,True)
        ID_VIEW_STATUSBAR = wx.NewId()
        self.YesNoStatusBar = menu_view.AppendCheckItem(ID_VIEW_STATUSBAR,u"状态栏",help=u"显示状态栏")
        menu_view.Check(ID_VIEW_STATUSBAR,True)

        ##"帮助"菜单
        menu_help = wx.Menu()
        menu_help.Append(wx.ID_HELP,u"查看帮助",help=u"查看帮助")

        AboutNoteBook = menu_help.Append(-1,u"关于笔记本",help=u"关于笔记本")
        ##将菜单附加在菜单栏上
        menubar.Append(menu_file,u"文件")
        menubar.Append(menu_edit,u"编辑")
        menubar.Append(menu_layout,u"格式")
        menubar.Append(menu_view,u"查看")
        menubar.Append(menu_help,u"帮助")
        ##将菜单栏与框架关联#
        self.SetMenuBar(menubar)

        self.Bind(wx.EVT_MENU, self.OnCreateNew,id=wx.ID_NEW)
        self.Bind(wx.EVT_MENU, self.OnOpenFile,id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.OnSaveFile,id=wx.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.OnSaveASFile,id=wx.ID_SAVEAS)
        self.Bind(wx.EVT_MENU, self.OnSetting,id=wx.ID_PAGE_SETUP)
        self.Bind(wx.EVT_MENU, self.OnCloseWindow,id=wx.ID_EXIT)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.Bind(wx.EVT_MENU,self.OnFontSet,FontSetting)
        self.Bind(wx.EVT_MENU,self.OnBackgroundColor,id=ID_BACKGROUND_COLOR)
        self.Bind(wx.EVT_MENU, self.OnAutoWordwarp,id=ID_LINE_FEED)
        self.Bind(wx.EVT_MENU, self.OnAboutNoteBook,AboutNoteBook)
        self.Bind(wx.EVT_MENU, self.OnHelper,id=wx.ID_HELP)
        self.Bind(wx.EVT_MENU, self.OnEditUndo, id=wx.ID_UNDO)
        self.Bind(wx.EVT_MENU, self.OnEditCopy, id=wx.ID_COPY)
        self.Bind(wx.EVT_MENU, self.OnEditCut, id=wx.ID_CUT)
        self.Bind(wx.EVT_MENU, self.OnEditPaste, id=wx.ID_PASTE)
        self.Bind(wx.EVT_MENU, self.OnEditDelete, id=wx.ID_DELETE)
        self.Bind(wx.EVT_MENU, self.OnEditSelectAll, id=wx.ID_SELECTALL)
        self.Bind(wx.EVT_MENU, self.OnFindMenu, id=wx.ID_FIND)
        self.Bind(wx.EVT_MENU, self.OnFindNext, id=ID_FIND_NEXT)
        self.Bind(wx.EVT_MENU, self.OnFindMenu, id=wx.ID_REPLACE)
        self.Bind(wx.EVT_MENU, self.OnForward, id=wx.ID_FORWARD)
        self.Bind(wx.EVT_MENU, self.OnInsertTime, id=ID_DATE_TIME)
        self.Bind(wx.EVT_MENU, self.OnHideToolBar, id=ID_VIEW_TOOLSBAR)
        self.Bind(wx.EVT_MENU, self.OnHideStatusBar, id=ID_VIEW_STATUSBAR)

        self.Bind(wx.EVT_FIND, self.OnFind)
        self.Bind(wx.EVT_FIND_NEXT, self.OnFind)
        self.Bind(wx.EVT_FIND_REPLACE, self.OnReplace)
        self.Bind(wx.EVT_FIND_REPLACE_ALL, self.OnReplaceAll)
        self.Bind(wx.EVT_FIND_CLOSE, self.OnFindClose)


    #### 工具栏 ###########################
    def BookToolBar(self):
        self.toolbar = toolbar = self.CreateToolBar()
        toolbar.AddLabelTool(wx.ID_NEW,"",wx.Bitmap("icons/new.png"),shortHelp=u"新建文件",longHelp=u"新建文件")
        toolbar.AddLabelTool(wx.ID_OPEN,"",wx.Bitmap("icons/open.png"),shortHelp=u"打开文件",longHelp=u"打开文件")
        toolbar.AddLabelTool(wx.ID_SAVE,"",wx.Bitmap("icons/save.png"),shortHelp=u"保存文件",longHelp=u"保存文件")
        toolbar.AddLabelTool(wx.ID_EXIT,"",wx.Bitmap("icons/exit.png"),shortHelp=u"退出",longHelp=u"退出程序")
        toolbar.AddLabelTool(wx.ID_HELP,"",wx.Bitmap("icons/help.png"),shortHelp=u"查看帮助",longHelp=u"查看帮助")
        toolbar.AddLabelTool(wx.ID_PAGE_SETUP,"",wx.Bitmap("icons/setting.png"),shortHelp=u"页面设置",longHelp=u"页面设置")
        toolbar.AddLabelTool(wx.ID_FIND,"",wx.Bitmap("icons/search.png"),shortHelp=u"搜索",longHelp=u"搜索内容")
        ID_DATE = wx.NewId()
        toolbar.AddLabelTool(self.ID_DATE_TIME,"",wx.Bitmap("icons/date.png"),shortHelp=u"插入时间日期",
                             longHelp=u"在本文件中插入时间日期")
        toolbar.AddLabelTool(wx.ID_PRINT,"",wx.Bitmap("icons/print.png"),shortHelp=u"打印",longHelp=u"打印")
        toolbar.Realize()


    ########## 文本框 ############################################
    def BookText(self):
        ##设定一个文本框的布局
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        ##新建多行文本框，父框为panel
        self.MainText = wx.TextCtrl(self.panel,-1, "", size=(-1,-1),style=wx.TE_MULTILINE|wx.TE_RICH2)
        ##设定背景颜色
        self.MainText.SetBackgroundColour("light blue")
        ##调用拖放类与方法
        dt = FileDrop(self.MainText,self)
        self.MainText.SetDropTarget(dt)

        ##设定字体
        self.UpdateFont = False
        self.UpdateFontUI()

        ##加入sizer 布局，布满显示，可以自动伸展
        sizer.Add(self.MainText,1,flag=wx.EXPAND)

        ##调整自动宽度
        self.panel.SetSizerAndFit(sizer)
        self.MainText.Bind(wx.EVT_KEY_UP, self.OnKeyUp)

        ##在文本框上邦定一个键盘的字符按键事件
        self.MainText.Bind(wx.EVT_CHAR, self.OnKeyUp)

    ########### 状态栏####################################################
    def BookStatusBar(self):
        self.statusbar = CustomStatusBar(self)
        self.SetStatusBar(self.statusbar)
        #self.panel.Show(False)
        #self.panel.Bind(wx.EVT_MOTION,  self.OnMove)
        #self.TextStatuBar()

    ########### 功能函数与事件 #####################################

    ##打开并获取文件的内容。需要传入文件名路径，和文件编码
    def FileContents(self,filePath,fileCode):
        ##新建文件内容的空列表
        FileContentList = []
        try:
            ##以指定编码的方式解码打开的文件，每读取一行就加入文件的内容列表。
            with codecs.open(filePath,'r',fileCode) as FileObj:
                for line in FileObj.readlines():
                    FileContentList.append(line)
        except UnicodeDecodeError,errorMsg:
            #wx.MessageBox(u"不支持的文件类型或文件编码载入出错",caption=u"错误消息",style=wx.OK|wx.ICON_ERROR)
            return "codeError"
        self.FileContent = "".join(FileContentList)
        return self.FileContent

    def CheckFileSaveStatus(self):
        ##获取文件名
        FileName = self.GetTitle().split("-")[1]
        #print "--->title Name:",FileName
        TextContent = self.MainText.GetValue()
        #print "--->Text Content:",TextContent
        #print "---> if TextContentChanged:",self.TextContentChanaged
        ##不需要保存条件：
        # 1.文件内容为空，没有存储为文件(无标题)
        if TextContent == "" and FileName == self.DefaultFileName:
            #print "==>not need save"
            self.NeedSave = False
        # 2.文件内容未发生改变
        elif self.TextContentChanaged is False and FileName != self.DefaultFileName:
            #print '==>not need save'
            self.NeedSave = False
        else:
            #print "==>need save"
            self.NeedSave = True
        #print self.NeedSave
        return self.NeedSave

    ## 保存文件提示框，一共有三个按钮："是"，"否","取消"
    def SaveFilePrompt(self):
        ##获取文件名
        FileName = self.GetTitle().split("-")[1]
        ##创建文件保存提示对话框
        SavePromptDlg = wx.MessageDialog(self.MainText, u"是否将更改保存到 %s?" % FileName,u'记事本',
                                         wx.YES_NO|wx.CANCEL|wx.YES_DEFAULT|wx.ICON_QUESTION)
        ##取得输入按钮的返回值
        retCode = SavePromptDlg.ShowModal()
        if (retCode == wx.ID_YES):
            #print "yes"
            self.UserChooseSave = True
        elif (retCode == wx.ID_NO):
            self.UserChooseSave = False
        else:
            self.UserChooseSave = None
        SavePromptDlg.Destroy()
        return self.UserChooseSave

    ##设定状态栏中间段的内容
    def SetStatusBarText(self):
        #print "=========> check: ",self.TextContentChanaged
        if self.TextContentChanaged == True:
            stext2 = u"未保存"
        else:
            stext2 = u"已保存"
        self.SetStatusText(self.stext1 + stext2,1)

    ########## 事件函数 ####################################
    ##响应鼠标滑动事件
    def OnMove(self, event):
        #pass
        pos = event.GetPosition()
        self.SetStatusText("%s, %s" % (pos.x, pos.y),0)

    ##响应键盘按键事件，每按一次字符类型的键，就说明文本内容已发生改变，然后调用 SetStatusBarText()函数设定状态栏内容
    ##event.Skip 是事件跳过继续，也就是让文本框可以输入内容
    def OnKeyUp(self, event):
        #按键时相应代码
        #kc = event.GetKeyCode()
        #kc = event.GetUniChar()
        #print kc
        #if 8 <= kc <=126 or  str(kc) in self.kc_list:
            #print kc
        self.TextContentChanaged = True
        self.SetStatusBarText()
        event.Skip()

    ## 新建文件的事件函数，新建前调用 CheckSetp 函数检测原先文件内容是否需要保存
    @CheckStep
    def OnCreateNew(self,event):
        self.MainText.SetValue("")
        self.SetTitle(self.MainTitle+self.DefaultFileName)
        self.TextContentChanaged = True
        self.SetStatusBarText()

    ##打开文件的事件函数，打开前调用 CheckSetp 函数检测原先文件内容是否需要保存
    @CheckStep
    def OnOpenFile(self,event):
        wildcard = u"文本文件 (*.txt)|*.txt|" \
                   u"所有文件 (*.*)|*.*"
        DialogFile = wx.FileDialog(None, "Choice a file","", "", wildcard, wx.OPEN)
        if DialogFile.ShowModal() == wx.ID_OK:
            self.FilePath = DialogFile.GetPath()
            ##返回字符编码
            fileChar = CheckFileCode(self.FilePath,50)
            ##返回文件内容
            fileContent = self.FileContents(self.FilePath,fileChar)
            if fileContent == "codeError":
                try:
                    print "try read all charactors for detection code"
                    fileChar = CheckFileCode(self.FilePath,-1)
                    fileContent = self.FileContents(self.FilePath,fileChar)
                    if fileContent == "codeError":
                        wx.MessageBox(u"不支持的文件类型或文件编码载入出错",caption=u"错误消息",style=wx.OK|wx.ICON_ERROR)
                except:
                    return
            ## 内容载入文本框
            self.MainText.SetValue(fileContent)
            ## 得到文件名
            self.FileName = os.path.basename(self.FilePath)
            ##设定 Frame 的标题
            self.SetTitle(self.MainTitle+self.FileName)
            self.TextContentChanaged = False
            self.SetStatusBarText()
        DialogFile.Destroy()

    ##直接保存文件的函数
    def FileSaveDirect(self):
        with codecs.open(self.FilePath,'w') as FileObj:
            self.FileContent = self.MainText.GetValue()
            FileObj.write(self.FileContent.encode("utf-8"))
            self.TextContentChanaged = False
            self.SetStatusBarText()

    ##保存文件的对话框(另存为)
    def FileSaveDialogFun(self):
        wildcard = u"文本文件 (*.txt)|*.txt|" \
                   u"所有文件 (*.*)|*.*"
        DialogFile = wx.FileDialog(None, "Choice a file", os.getcwd(), "", wildcard, wx.SAVE|wx.OVERWRITE_PROMPT)
        if DialogFile.ShowModal() == wx.ID_OK:
            self.FilePath = DialogFile.GetPath()
            self.FileName = os.path.basename(self.FilePath)
            self.FileSaveDirect()
            self.SetTitle(self.MainTitle+self.FileName)
        else:
            return
        DialogFile.Destroy()

    def OnSaveFile(self,event):
        #print self.GetTitle().split("-")[1]
        if self.GetTitle().split("-")[1] == self.DefaultFileName:
            self.FileSaveDialogFun()
        else:
            self.FileSaveDirect()

    def OnSaveASFile(self,event):
        self.FileSaveDialogFun()

    def OnSetting(self,event):
        pass

    def OnFontSet(self,event):
        DialogFont = wx.FontDialog(self,wx.FontData())
        if DialogFont.ShowModal() == wx.ID_OK:
            data = DialogFont.GetFontData()
            self.curFont = data.GetChosenFont()
            self.curColour = data.GetColour()
            self.UpdateFont = True
            self.UpdateFontUI()

        DialogFont.Destroy()

    def UpdateFontUI(self):
        if self.UpdateFont == True:
            # print self.curFont
            # print self.curColour
            # print self.curFont.GetPointSize()
            # print self.curFont.GetFamilyString()
            # print self.curFont.GetStyleString()
            #print self.curFont.GetWeightString()
            # print self.curFont.GetFaceName()
            # cPointSize = self.curFont.GetPointSize()
            # cfamily = self.curFont.GetFamilyString()
            # cstyle = self.curFont.GetStyleString()
            # cweight = self.curFont.GetWeightString()
            # cface = self.curFont.GetFaceName()
            # curFontAll = wx.Font(pointSize=cPointSize, family=wx.FONTFAMILY_DEFAULT,
            #                      style=wx.FONTSTYLE_NORMAL,weight=wx.FONTWEIGHT_NORMAL,underline=False,
            #                face=cface, encoding=wx.FONTENCODING_SYSTEM)
            self.MainText.SetFont(self.curFont)
            self.MainText.SetForegroundColour(self.curColour)
            self.MainText.Refresh()
        else:
            ##获取系统的默认字体
            #font = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
            ##创建自定义字体
            curFontAll = wx.Font(pointSize=10.5, family=wx.FONTFAMILY_DEFAULT, style=wx.FONTSTYLE_NORMAL,
                           weight=wx.FONTWEIGHT_NORMAL,underline=False, face="", encoding=wx.FONTENCODING_SYSTEM)
            self.MainText.SetFont(curFontAll)
            #print curFontAll.GetWeight()
    ##更新背景颜色
    def OnBackgroundColor(self,event):
        self.ColorDialog = ColorDialog = wx.ColourDialog(self.panel)

        ColorDialog.GetColourData().SetChooseFull(True)
        if ColorDialog.ShowModal() == wx.ID_OK:
            data = ColorDialog.GetColourData()
            SelectColor = data.GetColour()
            print "You selected: %s \n" %  SelectColor
            self.MainText.SetOwnBackgroundColour(SelectColor)
            self.MainText.Refresh()
        ColorDialog.Destroy()

    def ChangeStyle(self,oldMainText,style):
        TextContent = oldMainText.GetValue()
        #oldMainText.Destory()
        self.MainText = wx.TextCtrl(self.panel, -1,TextContent, size=(-1,-1),
                                    style=style)
        self.MainText.SetBackgroundColour(self.bcolor)
        self.UpdateFont = False
        self.UpdateFontUI()

        self.ChangeTextSizer(oldMainText,self.MainText)
         ##调用拖放类与方法
        dt = FileDrop(self.MainText,self)
        self.MainText.SetDropTarget(dt)
        self.MainText.Bind(wx.EVT_CHAR, self.OnKeyUp)

    def OnAutoWordwarp(self,event):
        self.bcolor = self.MainText.GetBackgroundColour()
        if self.AutoWordWarp.IsChecked() is False:
            print "111"
            style = wx.TE_MULTILINE|wx.TE_RICH2|wx.HSCROLL
            self.ChangeStyle(self.MainText,style)
        else:
            print "222"
            style=wx.TE_MULTILINE|wx.TE_RICH2|wx.TE_WORDWRAP
            self.ChangeStyle(self.MainText,style)


    def ChangeTextSizer(self,oldTextCtrl,NewTextCtrl):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(NewTextCtrl,1,flag=wx.EXPAND)
        self.panel.SetSizerAndFit(sizer)
        oldTextCtrl.Destroy()
        NewTextCtrl.Refresh()
        self.SendSizeEvent()

    def OnAboutNoteBook(self,event):
        info = wx.AboutDialogInfo()
        about_icon = wx.Icon('icons\Notepad.png', wx.BITMAP_TYPE_PNG)
        info.SetIcon(about_icon)
        info.Name = "My NotePad"
        info.Version = "1.0 Beta"
        info.Copyright = "(C) 2013 Python Geeks Everywhere"
        info.Description = wordwrap(u"MyNotepad 是一个免费的记事本软件，最常用于查看或编辑文本文件。"
                                    u"他使用 python 语言编写。 ",350, wx.ClientDC(self.panel))
        info.WebSite = ("http://www.avyou.net", u"我的主页")
        info.Developers = ["avyou"]
        info.License = wordwrap(u"免费软件!", 500,
                            wx.ClientDC(self.panel))
        info.SetCopyright('(C) 2013 avyou')
        wx.AboutBox(info)

    def OnHelper(self,event):
        with codecs.open("Help.txt",'r',"utf-8") as FileObj:
            HelpContent = FileObj.read()
        DialogHelp = wx.lib.dialogs.ScrolledMessageDialog(None,HelpContent, u"帮助文档",
                           pos=wx.DefaultPosition, size=(500,300),style=wx.RESIZE_BORDER|wx.DD_DEFAULT_STYLE)
        DialogHelp.ShowModal()
        DialogHelp.Destroy()


    def OnEditUndo(self, event):
        self.MainText.Undo()
        self.TextContentChanaged = True

    def OnEditCut(self, event):
        self.MainText.Cut()
        self.TextContentChanaged = True

    def OnEditCopy(self, event):
        self.MainText.Copy()
        self.TextContentChanaged = True

    def OnEditPaste(self, event):
        self.MainText.Paste()
        self.TextContentChanaged = True

    def OnEditDelete(self, event):
        start, end = self.MainText.GetSelection()
        self.MainText.Remove(start, end)
        self.TextContentChanaged = True

    def OnEditSelectAll(self, event):
        self.MainText.SelectAll()

    def readFindFlags(self):
        _Findflags = self.finddata.GetFlags()
        if _Findflags & wx.FR_MATCHCASE:
            self.matchCase = True
        else:
            self.matchCase = False
        # if _Findflags & wx.FR_WHOLEWORD:
        #     self.wholeWord = True
        # else:
        #     self.wholeWord = False
        if _Findflags & wx.FR_DOWN:
            self.goingDown = True
        else:
            self.goingDown = False

    def StrmatchCase(self,findString):
        self.readFindFlags()
        if self.matchCase is False:
            FileContents = self.MainText.GetValue().upper()
            findString = findString.upper()
        else:
            FileContents = self.MainText.GetValue()
        return findString,FileContents


    def OnFind(self,event):
        self.readFindFlags()
        print "down:",self.goingDown
        #print "whole:",self.wholeWord
        print "case:",self.matchCase
        findstr = self.finddata.GetFindString()
        if self.goingDown:
            if not self.FindString(findstr):
                wx.MessageBox(u'找不到 %s'%findstr, u'记事本', wx.OK | wx.ICON_INFORMATION,parent=self.finddlg)
                wx.Bell()
        else:
            if not self.FindStringPrev(findstr):
                wx.MessageBox(u'找不到 %s'%findstr, u'记事本', wx.OK | wx.ICON_INFORMATION,parent=self.finddlg)
                wx.Bell()

    def FindString(self,findString):
        self.readFindFlags()
        ##大小写敏感匹配检测
        findString,FileContents = self.StrmatchCase(findString)
        ##获取文本的选择范围，返回一个字节point位置的元组
        selectPoint = self.MainText.GetSelection()
        ##如果没有选取文本范围，默认 selectPoint 返回元组的两个数是相等的，也就是等下光标的插入点
        ##如果选取了范围，selectPoint返回元组的两人个数是不相等的
        if selectPoint[0] != selectPoint[1]:
            startFindAt = max(selectPoint)  ##设置查找点 startFindAt 为元组最大的数
        else:
            startFindAt = self.MainText.GetInsertionPoint()  ##设置开始查找点为光标插入点
        if startFindAt == self.MainText.GetLastPosition():  ##如果查找点为尽头，重置为0
            startFindAt = 0
        ##开始查找指定的字符
        foundStr = FileContents.find(findString,startFindAt)
        if foundStr != -1:
            ##如果找到，求出字符的最后位置
            EndStr = len(findString) + foundStr
            ##设置文本选取范围
            self.MainText.SetSelection(EndStr,foundStr)
            ##设置文本选取范围的focus
            self.MainText.SetFocus()
            return True
        else:
            return False

    def FindStringPrev(self,findString):
        self.readFindFlags()
        ##大小写敏感匹配检测
        findString,FileContents = self.StrmatchCase(findString)

        end = self.MainText.GetLastPosition()
        start =  self.MainText.GetSelection()[0]

        loc = FileContents.rfind(findString,0,start)
        print loc
        if loc == -1 and start !=0:
            start = end
            loc = FileContents.rfind(findString,0, start)
        if loc != -1:
            self.MainText.ShowPosition(loc)
            self.MainText.SetSelection(loc,loc + len(findString))
            self.MainText.SetFocus()
            return True
        return False

    def OnFindNext(self,event):
        self.readFindFlags()
        if self.finddata.GetFindString():
            try:
                self.OnFind(event)
            except:
                wx.Bell()
        return

    def OnReplace(self,event):
        self.readFindFlags()
        fstring = self.finddata.GetFindString()
        rstring = self.finddata.GetReplaceString()
        ##大小写敏感匹配检测
        fstring,FileContents = self.StrmatchCase(fstring)
        pos = self.MainText.GetInsertionPoint()
        start,end = pos,pos

        if self.FindString(fstring):
            start,end = self.MainText.GetSelection()
            self.MainText.Replace(start,end,rstring)

    def OnReplaceAll(self,event):
        self.readFindFlags()
        rstring = self.finddata.GetReplaceString()
        fstring = self.finddata.GetFindString()
        ##大小写敏感匹配检测
        fstring,FileContents = self.StrmatchCase(fstring)
        nFileContents = FileContents.replace(fstring, rstring)
        self.MainText.SetValue(nFileContents)

    def OnFindClose(self,event):
        self.finddlg.Destroy()

    def OnHideToolBar(self, event):
        if self.YesNoToolBar.IsChecked():
            self.toolbar.Show()
            self.SendSizeEvent()
        else:
            self.toolbar.Hide()
            self.SendSizeEvent()

    def OnHideStatusBar(self,event):
        if self.YesNoStatusBar.IsChecked():
            self.statusbar.Show()
            self.SendSizeEvent()
        else:
            self.statusbar.Hide()
            self.SendSizeEvent()

    @CheckStep
    def OnCloseWindow(self,event):
        self.Destroy()

    # def OnForward(self,event):
    #     print "goto"
    #     print self.MainText.GetLineText(50)
    #     self.MainText.ShowPosition(3950)
    #     self.MainText.Refresh()
    def OnForward(self,event):
        """ Display Goto Line Number dialog box """
        line = -1
        dialog = wx.TextEntryDialog(self.panel, (u"跳转到指定行:"), (u"跳转行"))
        dialog.CenterOnParent()
        if dialog.ShowModal() == wx.ID_OK:
            try:
                line = int(dialog.GetValue())
                if line > 65535:
                    line = 65535
            except:
                pass
        dialog.Destroy()
        print line
        print self.MainText.GetNumberOfLines()

        ##转换指定行为行首的point
        startpos = self.MainText.XYToPosition(0, line-1)
        ##转换指定行为行尾的point
        endpos = self.MainText.XYToPosition(0, line)
        print startpos
        ##选定行首和行尾之间范围的内容
        self.MainText.SetSelection(startpos, endpos)

        self.MainText.SetFocus()

    def OnFindMenu(self, event):
        evt_id = event.GetId()
        if evt_id in (wx.ID_FIND, wx.ID_REPLACE):
            self._InitFindDialog(evt_id)
            self.finddlg.Show()
        else:
            event.Skip()

    def _InitFindDialog(self, mode):
        if self.finddlg:
            self.finddlg.Destroy()
        if mode == wx.ID_FIND:
            title = u"查找"
            style = wx.FR_NOWHOLEWORD
        else:
            title = u"查找与替换"
            style = wx.FR_REPLACEDIALOG|wx.FR_NOWHOLEWORD
        self.finddlg = wx.FindReplaceDialog(self,self.finddata,title,style)

    def OnInsertTime(self,event):
        t = time.localtime(time.time())
        iNowTime = time.strftime("%Y-%m-%d %H:%M:%S",t)
        pos = self.MainText.GetInsertionPoint()
        self.MainText.SetInsertionPoint(pos)
        self.MainText.WriteText("  %s  " % iNowTime)
        self.TextContentChanaged = True
        self.SetStatusBarText()
        event.Skip()


if __name__ == "__main__":
    app = wx.App()
    frame = MyNoteBookFrame()
    frame.Show()
    app.MainLoop()