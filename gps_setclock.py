#!/usr/bin/python3

# To get this to work:
#    sudo apt-get install gpsd gpsd-clients python3-gps
# then run the get_time script in ~/bin

import os
import sys
import time
from gps import *
import tkinter as tk
from datetime import datetime,time
from widgets_tk import *


def SetSysClock():
    val = lcd.val
    print('Setting system clock to',val,'...') 
    cmd = "sudo date --set="+val+" &"
    os.system("echo "+cmd)
    os.system(cmd)
    print("Done.")

print("Set Sys Clock to GPS UTC time")

try:
    gpsd = gps(mode=WATCH_ENABLE)
except:
    print("ERROR: No GPS found, the time has not been set")
    sys.exit()

while True:
    #wait until the next GPSD time tick
    gpsd.next()
    print('tic',gpsd.utc)
    if gpsd.utc != None and gpsd.utc != "":
        #gpsd.utc is formatted like 2015-04-01T17:32:04.000Z
        #convert it to a form the date -u command will accept: 20140401 17:32:04
        #use python slice notation [start:end] (where end desired end char + 1)
        # gpsd.utc[0:4]  is 2015
        # gpsd.utc[5:7]  is 04
        # gpsd.utc[8:10] is 01 
        gpsutc = gpsd.utc[0:4] + gpsd.utc[5:7] + gpsd.utc[8:10] + ' ' + gpsd.utc[11:19]
        print('GPS Time=',gpsutc,' UTC')
        #os.system("sudo date -u -set=%s" % gpsutc)
        #sys.exit()


