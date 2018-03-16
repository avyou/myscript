#!/bin/bash
# monitoring network for XinShi of zxkf
# by avyou
# 2011-06-17
# last update 2011-06-18


export LANG=en_US.UTF-8
nowtime=$(date +%Y-%m-%d-%H:%M:%S)
month=$(date +%m)
day=$(date -I)
mark="245"
dir="/root/.script/monitoring-net"
tmp_file="/tmp/${day}-ping-${mark}.txt"
mon_file="$dir/${month}-monitoring-${mark}.txt"
status_file="$dir/status-${mark}.txt"
interval_file="$dir/interrval-time-${mark}.txt"
phone_sender="139xxxxxxxx"
phone_to_list="139xxxxxxxx,139xxxxxxxx"
pw="123456"
IP="1.1.1.1"
ping_packet="10"       #ping的次数
setting_loss="40"      #丢包百分比
setting_rtt_avg="500"  #延时值
interval_warn="120"    #间隔时间，单位为分钟
msg_from="从香港服务器检测"
msg_fail="xxx网络故障"
msg_success="xxx网络已恢复正常"
 
if [ ! -d $dir ];then
  mkdir -p $dir
fi
 
#初始化网络状态文件
if [ ! -f $status_file ];then
  echo "0" > $status_file
fi
 
#初始化所定义的”时间间隔”文件
if [ ! -f $interval_file ];then
    time_stamp=`date +%s`
    time=`date -d "1970-01-01 UTC $time_stamp seconds"`
    reduce_time=`expr ${interval_warn} \* 60`
    initial_stamp=`expr $time_stamp - $reduce_time`
    initial_time1=`date -d "1970-01-01 UTC $initial_stamp seconds"`
    initial_time2=`date -d "$initial_time1" +"%y%m%d%H%M"`
    touch -t $initial_time2 $interval_file
fi
 
#定义短信警告信息
function send_warning_message () {
LD_LIBRARY_PATH=/usr/local/fetion /usr/local/fetion/fetion \
    --mobile="$phone_sender"  \
    --pwd="$pw"  \
    --to="$phone_to_list" \
    --msg-utf8="Warning!! ${msg_from},${msg_fail},IP=$IP,packet loss=${loss}%,rtt avg=${avg}ms,$nowtime" >/dev/null;
echo "0">$status_file
}
#定义短信成功信息
function send_ok_message () {
LD_LIBRARY_PATH=/usr/local/fetion /usr/local/fetion/fetion \
    --mobile="$phone_sender" \
    --pwd="$pw"  \
    --to="$phone_to_list"  \
    --msg-utf8="OK! ${from},${msg_success},IP=$IP,packet loss=${loss}%,rtt avg=${avg}ms,$nowtime" >/dev/null;
echo "1">$status_file
}
 
#定义检测函数
function check_network(){
   echo "-------------------------$nowtime------------------------------------" >>$tmp_file
   echo "                                                                     " >>$tmp_file
   ping -c $ping_packet $IP >>$tmp_file
   find  /tmp -name *ping*.txt -ctime +31 -exec sudo rm -rf {} \;
   #获取RTT平均延时的值
   avg=`tail -1 $tmp_file |head -n 1 |awk -F =  '{print $2}'|awk -F / '{print $2}'`
   #获取丢包值
   loss=`tail -2 $tmp_file |head -n 1 |awk -F , '{print $3}' |sed -re 's/[^0-9]*([0-9]*).*$/\1/;'`
}
 
check_network
 
if (("$loss" > "$setting_loss")) || ((`echo ${avg%.*}` > "$setting_rtt_avg"));then
 
#判断，如果丢包大于指定值或者RTT延时大于指定值，执行下面语句:
   #获取“时间”文件到现在时间间隔
   file_time1=`ls -lt $interval_file |awk '{print $6,$7,$8}'`
   file_time2=`date -d  "$file_time1" +%s`
   nowtime1=`date +"%Y-%m-%d %H:%M:%S"`
   nowtime2=`date -d  "$nowtime1" +%s`
   interval=`expr $nowtime2 - $file_time2`
   interval_min=`expr $interval / 60`
 
   # 如果在120分钟前已经发送过警告短信，或者先前的检查状态正常的，就发送警告信息。
   if (("$interval_min" > "$interval_warn")) && ((`cat $status_file` == "1"));then
         send_warning_message
         echo "$nowtime"> $interval_file
   fi
# 如果状态正常，执行下面语句：
else
   #如果先前的网络状态是警告的，就发送网络状态恢复的信息。如果不是，则什么都不做。
   if ((`cat $status_file` == "0"));then
##      send_ok_message
      echo "1">$status_file
   fi
fi