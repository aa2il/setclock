#!/usr/bin/python3
################################################################################
#
# Set Clock - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# GUI to set system date &/or time manually using a time source such as WWV.
#
# Notes:
#  - Need this library:      pip3 install tkcalendar
#  - The other programs in this directory are for playing with a GPS dongle.
#    Eventually, would like to incorporate that capability into this code as well.
#    However, for now, this is a quick & dirty alternative to the GPS dongle for
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
import sys
if sys.version_info[0]==3:
    import tkinter as tk
else:
    import Tkinter as tk
import time
import time

from datetime import datetime,time
from widgets_tk import *
from tkcalendar import *
from ToolTip import *

################################################################################

def SetSysClock():
    val = lcd.val
    print('Setting system clock to',val,'...') 
    cmd = "sudo date --set="+val+" &"
    os.system("echo "+cmd)
    os.system(cmd)
    print("Done.")

def update_clock():
    now = datetime.now().strftime("%H:%M:%S")
    print('Update:',now)
    clk.label.configure(text=now)
    win.after(1000, update_clock)

# Function to select the date
def get_date():
   label.config(text=cal.get_date())
   print('*** NEED to update this ***')

################################################################################

print("\nSet Sys Clock to New Time")

# Root window
win = tk.Tk()
win.title('Date and Time Picker')
#win['bg'] = 'darkgreen'

# GUI to select new time
row=0
tk.Label(win, text="New Time:").grid(row=row,column=0)

lcd=DigitalClock(win)
lcd.label.grid(row=row,column=1)
now = datetime.now().strftime("%H:%M:%S")
#print('now=',now)
lcd.set(now)
tip = ToolTip(lcd.label, ' Spin Mouse Wheel to Select New Time ' )

# Display current time
row+=1
tk.Label(win, text="Current System Time:").grid(row=row,column=0)

clk=DigitalClock(win)
clk.label.grid(row=row,column=1)
tip = ToolTip(clk.label, ' Current System Time ' )
update_clock()

# Calendar widget
cal= Calendar(win, selectmode="day")
cal.grid(row=0,column=2,rowspan=2,columnspan=2)
tip = ToolTip(cal, ' Click to Select New Date ' )

# Button to set system time
row+=1
btn1 = tk.Button(win, text='Set Time',command=SetSysClock )
btn1.grid(row=row,column=1)
tip = ToolTip(btn1, ' Press to Set System Time ' )

# Button to set system date
btn2= tk.Button(win, text= "Set Date", command= get_date)
btn2.grid(row=row,column=2)
tip = ToolTip(btn2, ' Press to Set System Date ' )

# Label for displaying selected Date
label = tk.Label(win, text="")
label.grid(row=row,column=3)

win.mainloop()
