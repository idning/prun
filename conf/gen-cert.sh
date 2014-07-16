#!/bin/bash
#file   : gen-cert.sh
#author : ning
#date   : 2014-07-14 12:28:35


HOST=$1
#1. key:
openssl genrsa -out $HOST.key 2048
#2. certificate:
openssl req -new -x509 -key $HOST.key -out $HOST.cert -days 3650 -subj /CN=$HOST


