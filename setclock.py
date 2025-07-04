#!/usr/bin/env -S uv run --script
#
# OLD: !/usr/bin/python3
################################################################################
#
# Set Clock - Rev 1.0
# Copyright (C) 2021-5 by Joseph B. Attili, joe DOT aa2il AT gmail DOT com
#
# GUI to set system date &/or time manually using a time source such as
# a cellphone or WWV.
#
# Notes:
#  - Need these libraries:
#                  pip3 install tkcalendar gpsd-py3
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
from  rig_io import socket_io
import time
from latlon2maiden import *
from fileio import save_gps_coords

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
            time.sleep(1)
            print('Connecting to GPS ...')
            gpsd.connect()
            time.sleep(1)
            print('Querying to GPS ...')
            packet = gpsd.get_current()
            print("GPS found!")
            return True
        except Exception as e: 
            print("ERROR: No GPS found or other error")
            print(e)
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
    time.sleep(1)

    # Update manual time
    now = datetime.now()
    now_time = now.strftime("%H:%M:%S")
    gui.lcd.set(now_time)

    # Update calendar
    gui.cal.selection_set(now)
    
    print("Done.")

def SetFromGPS():
    val = gui.gps_date_time
    print('Setting system clock to',val,'...' )
    cmd = 'sudo date --set="'+val+'" &'
    os.system("echo "+cmd)
    os.system(cmd)
    time.sleep(1)

    # Update manual time
    now = datetime.now()
    now_time = now.strftime("%H:%M:%S")
    gui.lcd.set(now_time)

    # Update calendar
    gui.cal.selection_set(now)

    # Update the rig also
    if gui.set_rig_also.get():
        print('Setting rig time also...')
        gui.sock.set_date_time()

    # Save location info
    save_gps_coords(gui.gps_loc)
    
    print("Done.")

def get_gps_time():
    VERBOSITY=0
    packet = gpsd.get_current()
    if VERBOSITY>0:
        print('\nPacket:')
        pprint(vars(packet))
    if packet.mode >= 2:
        utc=str(packet.time)
        #print('UTC Time=',utc,' UTC')

        utc = datetime.strptime(utc[0:19],'%Y-%m-%dT%H:%M:%S')
        utc = utc.replace(tzinfo=from_zone)
        local = utc.astimezone(to_zone)
        #print('Local Tine=',local)

        lat=packet.lat
        lon=packet.lon
        alt=packet.alt
        gridsq = latlon2maidenhead(lat,lon,12)
        try:
            # This fails if gui isn't up yet
            gui.gridsq['text']=str(lat)+' deg\n'+str(lon)+' deg\n'+ \
                str(alt)+' m='+str(alt/.3048)+' ft\n'+gridsq
        except:
            print('GPS Position:',lat,lon,alt,'\t',gridsq)
            
    else:
        print(" GPS Time: NOT AVAILABLE")
        local=None
        lat=None
        lon=None
        alt=None
        gridsq=''
        
    return local,(lat,lon,alt,gridsq)

# Function to select the date
def get_date():
   gui.date_label.config(text=gui.cal.get_date())
   print('*** NEED to update this - time isbogus ***')

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

   val = gui.cal.get_date()   #.replace('/21','/2021')
   print('Setting system date to',val,'...' )
   #cmd = 'sudo date --set="'+val+'" &'
   cmd = 'sudo date -s "'+val+' $(date +%H:%M:%S)" &'
   os.system("echo "+cmd)
   os.system(cmd)
   time.sleep(1)
   
   #print('date=',date)
   #gui.cal.selection_set(date) 

"""
selection_set(self, date) :
If selectmode is ‘day’, set the selection to date where date can be either a datetime.date instance or a string corresponding to the date format "%x" in the Calendar locale. Does nothing if selectmode is "none".

#dt=date(2021,8,19) # specific date Year, month , day
#cal.selection_set(dt) # Set the selected date 
cal.selection_set('8/16/2021') # Set the local calendar format

   dt=cal.selection_get()
    str=dt.strftime("%d-%m-%Y") # format changed 
    l1.config(text=str) # read and display date

"""

################################################################################

# The GUI 
class SETCLOCK_GUI():
    def __init__(self):

        # Init
        self.gps_date_time=''                   # Time/date string
        self.gps_log=None                       # Location 

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
        #self.rig_connected = self.sock.active and self.sock.rig_type2=='FT991a'
        #self.rig_connected = True
        self.rig_connected = self.sock.active
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
        col=0
        tk.Label(win, text="GPS Time:").grid(row=row,column=col)
        self.gps_lcd=DigitalClock(win)
        self.gps_lcd.label.grid(row=row,column=col+1)
        self.gps_lcd.set('')
        tip = ToolTip(self.gps_lcd.label, ' GPS Time ' )

        # Display Rig time
        row+=1
        tk.Label(win, text="Rig Time:").grid(row=row,column=col)
        self.rig_lcd=DigitalClock(win)
        self.rig_lcd.label.grid(row=row,column=col+1)
        self.rig_lcd.set('')
        tip = ToolTip(self.gps_lcd.label, ' Rig Time ' )

        # GUI to select new time
        row+=1
        tk.Label(win, text="Manual Time:").grid(row=row,column=col)
        self.lcd=DigitalClock(win)
        self.lcd.label.grid(row=row,column=col+1)
        now = datetime.now().strftime("%H:%M:%S")
        #print('now=',now)
        self.lcd.set(now)
        tip = ToolTip(self.lcd.label, ' Spin Mouse Wheel to Select New Time ' )

        # Display current time
        row+=1
        tk.Label(win, text="Current System Time:").grid(row=row,column=col)
        self.clk_lcd=DigitalClock(win)
        self.clk_lcd.label.grid(row=row,column=col+1)
        tip = ToolTip(self.clk_lcd.label, ' Current System Time ' )
        self.update_clock()
        
        # Calendar widget
        row=0
        col=2
        self.cal = Calendar(win, selectmode="day")
        self.cal.grid(row=row,column=col,rowspan=2,columnspan=2)
        tip = ToolTip(self.cal, ' Click to Select New Date ' )

        # Checbox to set rig time also
        row+=2
        self.set_rig_also=tk.IntVar()
        self.set_rig_also.set(1)
        chkbox=tk.Checkbutton(win,text='Set Rig Time Also', \
                              variable=self.set_rig_also)
        chkbox.grid(row=row,column=col,columnspan=2)
        tip = ToolTip(chkbox, ' Set Rig Time Also On/Off ')

        # Display GPS position
        if False:
            row+=1
            self.position=tk.Label(win, text="Lat Long Alt")
            self.position.grid(row=row,column=col,columnspan=2)
        row+=1
        self.gridsq=tk.Label(win, text="Grid Square")
        self.gridsq.grid(row=row,column=col,columnspan=2)
        
        # Button to set system time & date from gps
        row=4
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
        self.btn3 = tk.Button(win, text='Set Time Manually',command=self.SetSysClock )
        self.btn3.grid(row=row,column=col)
        tip = ToolTip(self.btn3, ' Press to Set System Time mannually' )
        col+=1
        
        # Button to set system date from  claendar widget
        self.btn4= tk.Button(win, text= "Set Date Manually", command= get_date)
        self.btn4.grid(row=row,column=col)
        tip = ToolTip(self.btn4, ' Press to Set System Date from calendar' )
        col+=1

        # Label for displaying selected Date
        self.date_label = tk.Label(win, text="")
        self.date_label.grid(row=row,column=col)
        col+=1

    def SetSysClock(self):
        val = self.lcd.val
        print('SET SYS CLOCK: Setting system clock to',val,'...') 
        cmd = "sudo date --set="+val+" &"
        os.system("echo "+cmd)
        os.system(cmd)

        # Update the rig also
        if gui.set_rig_also.get():
            print('Setting rig time also...')
            gui.sock.set_date_time()

        print("Done.")
        
    # Routine to update clock(s)
    def update_clock(self):
        now = datetime.now()
        now_time = now.strftime("%H:%M:%S")
        now_date = now.strftime("%m/%d/%Y")
        print('Update: now=',now,'\t',now_time,'\t',now_date)
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
            
            gps,loc=get_gps_time()
            if gps!=None:
                print('Update: gps=',gps,'\tloc=',loc)
                gps_date=gps.date().strftime("%Y-%m-%d")
                gps_time=gps.time().strftime("%H:%M:%S")
                self.gps_date_time=gps_date+' '+gps_time
                self.gps_lcd.label.configure(text=gps_time)
                self.gps_loc=loc

        else:
            
            # Look for GPS device again
            self.gps_recheck-=1
            if self.gps_recheck==0:
                self.gps_connected=find_gps()
                if self.gps_connected:
                    self.btn1.config(state='normal')
                else:
                    self.gps_recheck=20

        self.win.after(1000, self.update_clock)

            
################################################################################

print('\n****************************************************************************')
print('\n   Set System Clock to New Time ...\n')

gui = SETCLOCK_GUI()

gui.win.mainloop()
