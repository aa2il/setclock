#!/usr/bin/python3
################################################################################
#
# Set Clock - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# GUI to set system date &/or time manually using a time source such as
# a cellphone or WWV.
#
# Notes:
#  - Need this library:
#                  pip3 install tkcalendar
#
#  - The other programs in this directory are for playing with a GPS dongle.
#    Eventually, would like to incorporate that capability into this code.
#    For now, this is a quick & dirty alternative to the GPS dongle for
#    getting the proper time on the RPi (which does not have a real-time clock).
#
################################################################################
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
################################################################################

import os
import glob
import sys
if sys.version_info[0]==3:
    import tkinter as tk
else:
    import Tkinter as tk

from widgets_tk import *
from tkcalendar import *
from ToolTip import *
import gpsd
from pprint import pprint

from datetime import datetime
from dateutil import tz
import rig_io.socket_io as socket_io
import time

################################################################################

# Auto detect time zones
from_zone = tz.tzutc()             # Zulu
to_zone = tz.tzlocal()             # Local

# Look for gps
def find_gps():
    #if os.path.exists('/dev/gps0') or os.path.exists('/dev/gps1'):
    f=glob.glob('/dev/gps*')
    if len( f )>0:
        print('FIND_GPS: It appears that GPS device is plugged in...')
        try:
            gpsd.connect()
            packet = gpsd.get_current()
            print("GPS found!")
            return True
        except:
            print("ERROR: No GPS found.")
            return False
    else:
        print('FIND_GPS: It appears that GPS device is NOT plugged in...')
        return False
        
def SetFromRIG():
    val = gui.rig_date_time
    print('\nSetting system clock from rig to',val,'...') 
    cmd = 'sudo date --set="'+val+'" &'
    os.system("echo "+cmd)
    os.system(cmd)
    print("Done.")

def SetFromGPS():
    val = gui.gps_date_time
    print('Setting system clock to',val,'...') 
    cmd = 'sudo date --set="'+val+'" &'
    os.system("echo "+cmd)
    os.system(cmd)
    print("Done.")

def get_gps_time():
    packet = gpsd.get_current()
    #print('\nPacket:')
    #pprint(vars(packet))
    if packet.mode >= 2:
        utc=str(packet.time)
        #print('UTC Time=',utc,' UTC')

        utc = datetime.strptime(utc[0:19],'%Y-%m-%dT%H:%M:%S')
        utc = utc.replace(tzinfo=from_zone)
        local = utc.astimezone(to_zone)
        #print('Local Tine=',local)
        
    else:
        print(" GPS Time: NOT AVAILABLE")
        local=None
    return local

# Function to select the date
def get_date():
   label.config(text=cal.get_date())
   print('*** NEED to update this ***')

   # Here is the supposed format:
   #date -s '2019-10-17 12:00:00'
   #date --set="20100513 05:30"
   #date +%Y%m%d -s "20081128"

   # This is the "modern" way to do this:
   # timedatectl
   # timedatectl set-time YYYY-MM-DD HH:MM:SS
   # timedatectl set-time '2015-12-01'
   # timedatectl set-time '10:42:43'
   # timedatectl list-timezones
   # timedatectl set-timezone 'Asia/Kolkata'


################################################################################

# The GUI 
class SETCLOCK_GUI():
    def __init__(self):

        # Init
        self.gps_date_time=''                   # Time/date string

        # Root window
        print("\nCreating GUI ...")
        win = tk.Tk()
        self.win = win
        win.title('Date and Time Picker')
        #self.win['bg'] = 'darkgreen'

        # Look for gps device
        print("Looking for GPS dongle ...")
        self.gps_connected=find_gps()
        if not self.gps_connected:
            self.gps_recheck=20

        # Try to open a connection to rig
        print("Looking for rig ...")
        self.sock = socket_io.open_rig_connection('ANY',0,0,0,'SET CLOCK')
        self.rig_connected = self.sock.active and self.sock.rig_type2=='FT991a'
        self.rig_connected = True
        if not self.sock.active:
            print('*** No connection available to rig ***')
        else:
            print('Rig found:',self.sock.rig_type2,self.rig_connected)

        if False:
            d,t,z=self.sock.get_date_time()
            print('d=',d)
            print('t=',t)
            print('z=',z)
            time.sleep(11)
            d,t,z=self.sock.get_date_time()
            print('d=',d)
            print('t=',t)
            print('z=',z)
            sys.exit(0)
            
        # Display GPS time
        row=0
        tk.Label(win, text="GPS Time:").grid(row=row,column=0)
        self.gps_lcd=DigitalClock(win)
        self.gps_lcd.label.grid(row=row,column=1)
        self.gps_lcd.set('')
        tip = ToolTip(self.gps_lcd.label, ' GPS Time ' )

        # Display Rig time
        row+=1
        tk.Label(win, text="Rig Time:").grid(row=row,column=0)
        self.rig_lcd=DigitalClock(win)
        self.rig_lcd.label.grid(row=row,column=1)
        self.rig_lcd.set('')
        tip = ToolTip(self.gps_lcd.label, ' Rig Time ' )

        # GUI to select new time
        row+=1
        tk.Label(win, text="Manual Time:").grid(row=row,column=0)
        self.lcd=DigitalClock(win)
        self.lcd.label.grid(row=row,column=1)
        now = datetime.now().strftime("%H:%M:%S")
        #print('now=',now)
        self.lcd.set(now)
        tip = ToolTip(self.lcd.label, ' Spin Mouse Wheel to Select New Time ' )

        # Display current time
        row+=1
        tk.Label(win, text="Current System Time:").grid(row=row,column=0)
        self.clk_lcd=DigitalClock(win)
        self.clk_lcd.label.grid(row=row,column=1)
        tip = ToolTip(self.clk_lcd.label, ' Current System Time ' )
        self.update_clock()
        
        # Calendar widget
        cal= Calendar(win, selectmode="day")
        cal.grid(row=0,column=2,rowspan=2,columnspan=2)
        tip = ToolTip(cal, ' Click to Select New Date ' )
        
        # Button to set system time & date from gps
        row+=1
        col=0
        self.btn1 = tk.Button(win, text='Set From GPS',command=SetFromGPS )
        self.btn1.grid(row=row,column=col)
        tip = ToolTip(self.btn1, ' Press to Set System Time from GPS' )
        if not self.gps_connected:
            self.btn1.config(state='disabled')

        # Button to set system time & date from rig
        col+=1
        self.btn2 = tk.Button(win, text='Set From Rig',command=SetFromRIG )
        self.btn2.grid(row=row,column=col)
        tip = ToolTip(self.btn2, ' Press to Set System Time from Rig ' )
        if not self.rig_connected:
            self.btn2.config(state='disabled')

        # Button to set system time from manual lcd widget
        col+=1
        btn = tk.Button(win, text='Set Time Manually',command=self.SetSysClock )
        btn.grid(row=row,column=col)
        tip = ToolTip(btn, ' Press to Set System Time mannually' )
        col+=1
        
        # Button to set system date from  claendar widget
        btn= tk.Button(win, text= "Set Date Manually", command= get_date)
        btn.grid(row=row,column=col)
        tip = ToolTip(btn, ' Press to Set System Date from calendar' )
        col+=1

        # Label for displaying selected Date
        label = tk.Label(win, text="")
        label.grid(row=row,column=col)
        col+=1

    def SetSysClock(self):
        val = self.lcd.val
        print('Setting system clock to',val,'...') 
        cmd = "sudo date --set="+val+" &"
        os.system("echo "+cmd)
        os.system(cmd)
        print("Done.")
        
    # Routine to update clock(s)
    def update_clock(self):
        now = datetime.now()
        now_time = now.strftime("%H:%M:%S")
        print('Update: now=',now,now_time)
        self.clk_lcd.label.configure(text=now_time)

        if self.rig_connected:
            d,t,z=self.sock.get_date_time()
            #print('GET_RIG_TIME: d=',d,'\tt=',t,'\tz=',z)
            utc = datetime.strptime(d+' '+t,'%Y%m%d %H%M%S')
            #print('GET_RIG_TIME: utc=',utc)
            utc = utc.replace(tzinfo=from_zone)
            rig = utc.astimezone(to_zone)
            #print('GET_RIG_TIME: rig=',rig)

            rig_date=rig.date().strftime("%Y-%m-%d")
            rig_time=rig.time().strftime("%H:%M:%S")
            self.rig_date_time=rig_date+' '+rig_time
            self.rig_lcd.label.configure(text=rig_time)
            
        if self.gps_connected:
            
            gps=get_gps_time()
            print('Update: gps=',gps)
            if gps!=None:
                gps_date=gps.date().strftime("%Y-%m-%d")
                gps_time=gps.time().strftime("%H:%M:%S")
                self.gps_date_time=gps_date+' '+gps_time
                self.gps_lcd.label.configure(text=gps_time)

        else:
            
            # Look for GPS device again
            self.gps_recheck-=1
            if self.gps_recheck==0:
                self.gps_connected=find_gps()
                if not self.gps_connected:
                    self.gps_recheck=20
    
        self.win.after(1000, self.update_clock)

            
################################################################################

print('\n****************************************************************************')
print('\n   Set System Clock to New Time ...\n')

gui = SETCLOCK_GUI()

gui.win.mainloop()
