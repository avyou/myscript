#!/bin/bash
# monitor ADSL dial and VPN conntect
# by avyou at 2013-01-05
# uptime 2013-01-07
# last uptime 2013-06-26
 
while true
do
wan_iface=ppp0
R_HOST=1.1.1.1
R_PORT=2222
eval NOWTIME=$(date +%Y-%m-%d-%H:%M:%S)
temp_file=/tmp/tmp_ip.txt
log_file=/root/.script/vpn_ip_update.log
ssh_status=/root/.script/connect_ssh_status.log
test ! -f ${temp_file} && touch ${temp_file}
test ! -f $ssh_status && touch $ssh_status
ppp_status=$(/sbin/ifconfig |grep $wan_iface)
 
if [ -z "$ppp_status" ];then
 
    ps -ef |grep -v 'grep' |grep 'adsl-connect' >/dev/null 2>&1
    if [ $? -ne 0 ];then
       /usr/sbin/adsl-connect & >/dev/null 2>&1
       sleep 10s
       if [ -n "$ppp_status" ];then
           sh /root/.script/firewall_adsl_vpn.sh
       fi
    fi
else
    newip=`/sbin/ifconfig  $wan_iface |awk -F'[ :]+' '/inet addr/{print $4}'`
    oldip=`cat $temp_file`
    vpn_status=$(ipsec auto --status |grep "IPsec SA established")
 
Remote_Change_IP() {
ssh -p $R_PORT -tt $R_HOST -o ConnectTimeout=8 <<SSH_SCRIPT >/dev/null 2>&1
sed -ri "s/[0-9].*(mytest.3322.org$/${newip}  \1/" /etc/hosts
/etc/init.d/ipsec restart >/dev/null 2>&1
exit
SSH_SCRIPT
} 
    if [[ "$oldip" != "$newip" ]] || [[ `cat $ssh_status` -ne 0 ]];then
       echo "Update IP ..."
       ifconfig  $wan_iface |awk -F'[ :]+' '/inet addr/{print $4}' > /tmp/tmp_ip.txt
       lynx -mime_header -auth=svn144:shsvn144 "http://www.3322.org/dyndns/update?system=dyndns&hostname=mytest.3322.org" >/dev/null 2>&1
       echo "$NOWTIME, Update firewall..." >>$log_file
       sh /root/.script/firewall_adsl_vpn.sh
       echo "$NOWTIME, Update IP to remote hosts file ..." >>$log_file
       echo "$NOWTIME, Restart remote openswan ipsec server ..." >>$log_file
 
       Remote_Change_IP
 
       if [[ $? -eq 0 ]];then
           echo '0' > $ssh_status
           echo "$NOWTIME, Restart local openswan ipsec server ..." >>$log_file
           /etc/init.d/ipsec restart >/dev/null 2>&1
           echo "$NOWTIME, Now ADSL IP is $newip " >>$log_file
       else
           echo '1' > $ssh_status
           echo "$NOWTIME, ssh connection fail..." >>$log_file
       fi
       sleep 2s
    fi
 
    sleep 5s
    vpn_status=$(ipsec auto --status |grep "IPsec SA established")
    tunnels_num=$(/etc/init.d/ipsec status |grep 'tunnels up' |awk  '{print $1}')
 
    if [[ "$vpn_status" = "" ]] || [[ "$tunnels_num" -lt 1 ]];then
        echo "$NOWTIME,Not Established or Tunnel !! ,Restart local openswan ipsec server again ..." >> $log_file
        /etc/init.d/ipsec restart >/dev/null 2>&1
    fi
 
    sleep 20s
 
fi
 
done