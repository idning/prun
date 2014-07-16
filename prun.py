#!/usr/bin/env python
#coding: utf-8
#file   : prun.py
#author : ning
#date   : 2013-03-13 22:46:29


import urllib, urllib2
import os, sys
import re, time
import logging

PWD = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(PWD, './lib/'))

so = PWD + '/libprun/libprun.so'

'''
this is for a normal http CONNECT proxy
'''
def main():
    os.putenv('PRUN_PROXY', '127.0.0.1:8888')
    os.putenv('PRUN_PROXY_PREFIX', 'CONNECT ')
    os.putenv('LD_PRELOAD', so)
    os.execvp(sys.argv[1], sys.argv[1:])
    print PWD

'''
this is for a private proxy
'''
def main():
    os.putenv('PRUN_PROXY', '127.0.0.1:8888')
    os.putenv('PRUN_PROXY_PREFIX', 'CONNECTX ')
    os.putenv('LD_PRELOAD', so)
    os.execvp(sys.argv[1], sys.argv[1:])
    print PWD

if __name__ == "__main__":
    main()

