#!/bin/bash
# create docker host
# by avyou
# at 20150205


while [ -z  $docker_name ];do
    read -p "Pleae input your docker name: " docker_name
    echo
done

if [ -n $docker_name ];then
    while [ `docker ps -a |awk '!/NAMES/{print $NF}' |grep -w $docker_name` ];do
        read -p "You enter the host name already exists. Please enter Your docker name again: " docker_name

        while [ -z  $docker_name ];do
            read -p "Pleae input your docker name: " docker_name
            echo
        done
    done
fi

echo "At present, the following image:"
echo
echo "########################################################################################"
docker images
echo "########################################################################################"
echo
read -p "Please select the image you need('eg: centos:6'; default is: '5u:centos6'): " choose_images
if [ -n $choose_images ];then
    while [ -z `docker images |awk '!/REPOSITORY/{print $1":"$2}'|grep $choose_images` ];do
        echo "sorry,Without  this images."
        read -p "Please select the image you need('eg: centos:6'; default is: '5u:centos6'): " choose_images
        echo
    done
fi
echo "Please enter ip address for docker host, suggest 192.168.1.30-60/192.168.5.10-192.168.5.30."
read -p "===>IP:" ipaddress
echo
echo "Will be create docker container, Information is as follows:"
read -p "Do you want to continue(Yes|No)?" answer
echo "--------------------------------------------------------"
echo "docker host name: $docker_name"
echo "docker host IP: $ipaddress"
echo "'/data' fs mount at local directory: /data/docker/disk/$docker_name"
echo "--------------------------------------------------------"

if [[ -z `echo $answer|grep -i "yes"` ]];then
   exit 1
else
   if [ -z $choose_images ];then
       docker run --net=none  --privileged=true  -d --name $docker_name --hostname $docker_name -v  /data/docker/disk/$docker_name:/data -i -t xx:centos6
   else
       docker run --net=none  --privileged=true  -d --name $docker_name --hostname $docker_name -v  /data/docker/disk/$docker_name:/data -i -t $choose_images
   fi
   pipework docker0 -i eth0  $docker_name  ${ipaddress}/23
   if [[ $? -eq 0 ]];then
       echo "Already created  docker container called name '$docker_name'"
       echo
       echo "==========================================="
       echo "Run Docker container:"
       echo
       docker ps -a
       echo
       echo "==========================================="
   fi
fi