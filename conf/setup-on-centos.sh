#!/bin/bash

# this script will setup pserver on a new centos(linode) instance
# run it with root

wget http://mirror-fpt-telecom.fpt.net/fedora/epel/6/i386/epel-release-6-8.noarch.rpm
rpm -ivh epel-release-6-8.noarch.rpm

#yum -y update
yum -y install git vim
yum -y install python-pip python-argparse python-tornado

git clone https://github.com/idning/prun.git
cd prun

nohup ./pserver/pserver.py --https -p 9527 &

#vps:
# curl https://raw.githubusercontent.com/idning/prun/master/conf/setup-on-centos.sh | sh

#local
#sudo echo '106.185.42.245 idning.com' >> /etc/hosts
#nohup python /home/ning/idning-github/prun/pserver/pserver.py --upstream=https://idning.com:9527/CONNECTX -p 9527 &
