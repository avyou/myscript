#Region ;**** 参数创建于 ACNWrapper_GUI ****
#AutoIt3Wrapper_outfile=某业务监控脚本v20120427.exe
#EndRegion ;**** 参数创建于 ACNWrapper_GUI ****
;AutoIT script
;Monitor for xxxx 某业务
;by avyou
;2011-03-20
;update 2011-10-28
;last update 2012-04-27

#Include <File.au3>
#include <Thread.au3>
;释放内存	
_RTEmptyWorkingSet()

;定义错误信息
Dim $error
$error='ERROR (): CXMPPClient::onDisconnect(),'

Dim $pm
$pm=MsgBox(4+32,"在线客服进程监控",'在线客服程序将启动并被监控，退出请安"否"',5)

Func _ReduceMemory($i_PID = -1)
    If $i_PID <> -1 Then
        Local $ai_Handle = DllCall("kernel32.dll", 'int', 'OpenProcess', 'int', 0x1f0fff, 'int', False, 'int', $i_PID)
        Local $ai_Return = DllCall("psapi.dll", 'int', 'EmptyWorkingSet', 'long', $ai_Handle[0])
        DllCall('kernel32.dll', 'int', 'CloseHandle', 'int', $ai_Handle[0])
    Else
        Local $ai_Return = DllCall("psapi.dll", 'int', 'EmptyWorkingSet', 'long', -1)
    EndIf
 
    Return $ai_Return[0]
EndFunc   

Func nowtime()
    return (@YEAR& "-" & @MON & "-" & @MDAY & " " &  @HOUR & ":" & @MIN & ":" & @SEC)
EndFunc

;;############### myserver1 组启动函数 ####################
Func Stop_myserver()
	ShellExecute("taskkill", "/F /IM myserver.exe", @ScriptDir)
	Sleep(3000)
EndFunc
	
Func Start_myserver()
	ShellExecute("D:\myserver1\myserver.bat")
EndFunc	

;;###############008_team_3s 组启动函数########################
Func Stop_myserver008()
	ShellExecute("taskkill", "/F /IM myserver008.exe", @ScriptDir)
	Sleep(3000)
EndFunc
	
Func Start_myserver008()
	ShellExecute("D:\008_team_3s\myserver008.bat")
EndFunc	

;;############### 004_team_fixed 组启动函数 ##################################
Func Stop_myserver004()
	ShellExecute("taskkill", "/F /IM myserver004.exe", @ScriptDir)
	Sleep(3000)
EndFunc
	
Func Start_myserver004()
	ShellExecute("D:\004_team_fixed\myserver004.bat")
EndFunc	

;;##################  SHMonitor 进程函数 ######################################
Func Stop_SHMonitor()
	ShellExecute("taskkill", "/F /IM SHMonitor.exe", @ScriptDir)
	Sleep(3000)
EndFunc
	
Func Start_SHMonitor()
	ShellExecute("D:\myserver1\SHMonitor.bat")
EndFunc	


Select
	Case $pm = 6 Or $pm = -1
		While 1				   
			Sleep(3000)
			;监控openfire进程，需要注意的是openfire有两个进程，一个是openfire.exe,一个是openfired.exe，openfire.exe开启的话，openfired.exe不一定开启。
			$list1 = ProcessList("openfire.exe")
            $pnum1 = $list1[0][0]			
			If ProcessExists("openfire.exe")=0  Then
				$check_file_log = FileOpen("D:\myserver1\check-某业务.log", 1)
                FileWriteLine($check_file_log,"[" & nowtime() & "]" & "------发现openfire进程已经关闭!")
			    ShellExecute("C:\Program Files\Openfire\bin\openfire.exe")
				FileWriteLine($check_file_log,"[" & nowtime() & "]" & "------启动openfire进程和服务!")
				FileClose($check_file_log)
			    Sleep(10000)
				
		    ElseIf $pnum1 >1 Then
				$check_file_log = FileOpen("D:\myserver1\check-某业务.log", 1)
				FileWriteLine($check_file_log,"[" & nowtime() & "]" & "------发现多个openfire进程!")
			    ProcessClose("openfire.exe")
				FileWriteLine($check_file_log,"[" & nowtime() & "]" & "------结束openfire进程!")
				FileClose($check_file_log)
		    EndIf
			
			;监控openfired进程
			$list2 = ProcessList("openfired.exe")
            $pnum2 = $list2[0][0]			
			If ProcessExists("openfired.exe")=0  Then
				$check_file_log = FileOpen("D:\myserver1\check-某业务.log", 1)
                FileWriteLine($check_file_log,"[" & nowtime() & "]" & "------发现openfired服务已经关闭!")
				ProcessClose("openfire.exe")
				FileWriteLine($check_file_log,"[" & nowtime() & "]" & "------结束openfire进程!")
			    ShellExecute("C:\Program Files\Openfire\bin\openfire.exe")
				FileWriteLine($check_file_log,"[" & nowtime() & "]" & "------启动openfire进程和服务!")
				FileClose($check_file_log)
			    Sleep(10000)
				
		    ElseIf $pnum2 >1 Then
				$check_file_log = FileOpen("D:\myserver1\check-某业务.log", 1)
				FileWriteLine($check_file_log,"[" & nowtime() & "]" & "------发现多个openfired服务!")
			    ProcessClose("openfired.exe")
				FileWriteLine($check_file_log,"[" & nowtime() & "]" & "------结束openfired进程!")
				FileClose($check_file_log)
		    EndIf			
			
#CS 		;监控myserver程序错误，发现有20次连接不上openfire，自动重启myserver
   			$lastline=FileReadLine("D:\myserver1\myserver1.log",-1)
   			;如果最后一行存在错误后，再去判断后20行是否存在错误，不然循环检测会变得很慢。
            If StringInStr($lastline,$error) Then	
               $has_error= True
   			   $num_lines = _FileCountLines("D:\myserver1\myserver1.log")
               For $error_lines= $num_lines To $num_lines-20 Step -1
   		       $var_line=FileReadLine("D:\myserver1\myserver1.log",$error_lines)
   			      If Not StringInStr($var_line,$error) Then		
   	                 $has_error= False
   			      EndIf
               Next
               If $has_error= True Then
   	              $check_file_log = FileOpen("D:\myserver1\check-某业务.log", 1)				
   	              FileWriteLine($check_file_log,"[" & nowtime() & "]" & "------发现myserver.log日志中有CXMPPClient::onDisconnect(), error:错误!,一直连接不上openfire.")
   				  Stop_myserver()
   				  FileWriteLine($check_file_log,"[" & nowtime() & "]" & "------结束myserver.exe进程!")
   				  Start_myserver()
   				  FileWriteLine($check_file_log,"[" & nowtime() & "]" & "------启动myserver.exe进程!")
   	              FileClose($check_file_log)
   			   EndIf
   			 EndIf
#CE
			
		    ;########################## 监控myserver进程 ################################################
	        $list3 = ProcessList("myserver.exe")
            $pnum3 = $list3[0][0]
			If $pnum3 = 0 Then
			   $check_file_log = FileOpen("D:\myserver1\check-某业务.log", 1)
			   FileWriteLine($check_file_log,"[" & nowtime() & "]" & "------发现myserver.exe进程已经被关闭!")
			   Stop_myserver()			   
		       Start_myserver()
			   FileWriteLine($check_file_log,"[" & nowtime() & "]" & "------启动myserver.exe进程!")
			   FileClose($check_file_log)				   
		    ElseIf $pnum3 >1 Then
			   $check_file_log = FileOpen("D:\myserver1\check-某业务.log", 1)
			   FileWriteLine($check_file_log,"[" & nowtime() & "]" & "------发现有多个myserver.exe进程!")
			   Stop_myserver()	
			   FileWriteLine($check_file_log,"[" & nowtime() & "]" & "------结束myserver.exe进程!")
		       Start_myserver()
               FileWriteLine($check_file_log,"[" & nowtime() & "]" & "------启动myserver.exe进程!")	
			   FileClose($check_file_log)
		   EndIf
		    ;##########################  监控SHmonitor进程 ###########################################
		    $list4 = ProcessList("SHMonitor.exe")
		    $pnum4 = $list4[0][0]
			If $pnum4 = 0 Then
			   $check_file_log = FileOpen("D:\myserver1\check-某业务.log", 1)
			   FileWriteLine($check_file_log,"[" & nowtime() & "]" & "------发现SHMonitor.exe进程已经被关闭!")		  
		       Start_SHMonitor()
			   FileWriteLine($check_file_log,"[" & nowtime() & "]" & "------启动SHMonitor.exe进程!")
			   FileClose($check_file_log)				   
		    ElseIf $pnum4 >1 Then
			   $check_file_log = FileOpen("D:\myserver1\check-某业务.log", 1)
			   FileWriteLine($check_file_log,"[" & nowtime() & "]" & "------发现有多个SHMonitor.exe进程!")
			   Stop_SHMonitor()
			   FileWriteLine($check_file_log,"[" & nowtime() & "]" & "------结束SHMonitor.exe进程!")
		       Start_SHMonitor()
               FileWriteLine($check_file_log,"[" & nowtime() & "]" & "------启动SHMonitor.exe进程!")	
			   FileClose($check_file_log)
		   EndIf
		   
			;###################### 监控myserver004进程 ###############################################
		   	$list5 = ProcessList("myserver004.exe")
            $pnum5 = $list5[0][0]
			If $pnum5 = 0 Then
			   $check_file_log = FileOpen("D:\004_team_fixed\check-某业务.log", 1)
			   FileWriteLine($check_file_log,"[" & nowtime() & "]" & "------发现myserver004.exe进程已经被关闭!")
			   Stop_myserver004()			   
		       Start_myserver004()
			   FileWriteLine($check_file_log,"[" & nowtime() & "]" & "------启动myserver004.exe进程!")
			   FileClose($check_file_log)				   
		    ElseIf $pnum5 >1 Then
			   $check_file_log = FileOpen("D:\004_team_fixed\check-某业务.log", 1)
			   FileWriteLine($check_file_log,"[" & nowtime() & "]" & "------发现有多个myserver004.exe进程!")
			   Stop_myserver004()	
			   FileWriteLine($check_file_log,"[" & nowtime() & "]" & "------结束myserver004.exe进程!")
		       Start_myserver004()
               FileWriteLine($check_file_log,"[" & nowtime() & "]" & "------启动myserver004.exe进程!")	
			   FileClose($check_file_log)
		   EndIf	   
		   
		   ;###################### 监控myserver008 进程 ###############################################
		   	$list6 = ProcessList("myserver008.exe")
            $pnum6 = $list6[0][0]
			If $pnum6 = 0 Then
			   $check_file_log = FileOpen("D:\008_team_3s\check-某业务.log", 1)
			   FileWriteLine($check_file_log,"[" & nowtime() & "]" & "------发现myserver008.exe进程已经被关闭!")
			   Stop_myserver008()			   
		       Start_myserver008()
			   FileWriteLine($check_file_log,"[" & nowtime() & "]" & "------启动myserver008.exe进程!")
			   FileClose($check_file_log)				   
		    ElseIf $pnum6 >1 Then
			   $check_file_log = FileOpen("D:\008_team_3s\check-某业务.log", 1)
			   FileWriteLine($check_file_log,"[" & nowtime() & "]" & "------发现有多个myserver008.exe进程!")
			   Stop_myserver008()	
			   FileWriteLine($check_file_log,"[" & nowtime() & "]" & "------结束myserver008.exe进程!")
		       Start_myserver008()
               FileWriteLine($check_file_log,"[" & nowtime() & "]" & "------启动myserver008.exe进程!")	
			   FileClose($check_file_log)
		   EndIf
        WEnd
		
	Case $pm=7
		Exit
EndSelect