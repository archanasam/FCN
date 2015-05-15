#!/usr/bin/python

import os,sys

os.system("kill -9 $(ps aux | grep python | grep " + sys.argv[1]  + " | grep " + sys.argv[2]  + " | grep -v \"grep\" | awk '{print $2}')")
