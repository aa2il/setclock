#! /usr/bin/python3
############################################################################################
#
# TK Widgets - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Modified/augmented gui widgets
#
# To Do - does the standalone version work under python3?
#       - Proably should be part of a library.
#
############################################################################################
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
############################################################################################

import sys
if sys.version_info[0]==3:
    import tkinter as tk
    import tkinter.font
else:
    import Tkinter as tk
    import tkFont

from datetime import datetime,time
#import time  
    
################################################################################

# LCD which responds to mouse wheel & has a call back
class DigitalClock():
 
    def __init__(self,parent=None,fmt='hh:mm:ss',val=0,wheelCB=None):
        self.wheelCB = wheelCB

        self.val=val
        FONT_SIZE=48    # 120

        # Determine total number of display "digits" including spaced and decimal point
        self.nspaces = 2
        ntot    = 3*self.nspaces+2

        # Create label & bind mouse wheel events
        self.digitCount = ntot                                # Set no. of digits
        self.label = tk.Label(parent, font=('courier', FONT_SIZE, 'bold'), \
                         width=ntot,anchor='e')
        self.set(val)                                         # Display starting value
        self.label.bind("<Button-4>", self.wheelEvent)
        self.label.bind("<Button-5>", self.wheelEvent)


    # Callback for mouse wheel event
    def wheelEvent(self,event):
        #print("wheelEvent:",self.val,event.num,event.x,event.y )

        # Determine which digit the mouse was over when the wheel was spun
        x    = event.x                                    # Width of lcd widget
        ndig = self.digitCount                            # Includes spaces & dec point
        w    = self.label.winfo_width()                   # Width of the display
        edge = 0*.028*w                                     # Offset of border
        idx1 = (w-x-edge)*float(ndig) / (w-2*edge)        # Indicator of digit with mouse but...
        print('\nx=',x,'ndig=',ndig,'w=',w,'edge=',edge,'idx1=',idx1)

        # ... Need to adjust for decimal point and spaces
        for n in range(self.nspaces):
            ns = 2*(n+1)
            if idx1>ns and idx1<ns+1:
                idx1 -= 0.5                    # We're over a colon
                #print('Over',n,ns)
            elif idx1>ns+1:
                idx1 -= 1                      # We're to the left of a colon
        idx = int(idx1)                        # Finally, we can determine which digit it is
        print('idx=',idx,ndig)

        # Adjust step size based on digit 
        self.step = pow(10,idx)
        if event.num == 5:
            delta = -1
        if event.num == 4:
            delta = 1

        # Display new value
        #print('val in=',self.val)
        val=self.val.replace(':','')
        #xx = str( int(val) + self.step*delta ).zfill(6)
        xx = int(val) + self.step*delta
        #print('xx1=',xx)
        if xx<0:
            xx+=240000
        #print('xx2=',xx)
        xx = str( xx ).zfill(6)
        print('val=',self.val,int(val),'\tstep=',self.step,'\tdelta=',delta,'\txx=',xx)
        
        h=int(xx[0:2])
        m=int(xx[2:4])
        s=int(xx[4:])
        print('h m s=',h,m,s)
        if s>80:
            s-=99-59
        elif s>=60:
            s-=60
            m+=1
        if m>80:
            m-=99-59
        elif m>=60:
            m-=60
            h+=1
        #if h>80:
        #    h-=99-23
        if h>=24:
            h-=24
        newval = time(h,m,s).strftime("%H:%M:%S")
        print('xx=',xx,'\tnewval=',newval)
        self.set(newval)

        # Do additional work if necessary
        if self.wheelCB:
            self.wheelCB(xx)


    # Function to set LCD display value
    def set(self,t):
        if t!=None:
            self.val=t
            #self.display(format(self.val,self.fmt))
            self.label['text'] = self.val
            #self.label['text'] = format(self.val,self.fmt)
            #print('val=',t)


    # Function to get LCD display value
    def get(self):
        return self.val

################################################################################

# Test program
if __name__ == '__main__':
    root = tk.Tk()
    root.title('turn mouse wheel')
    root['bg'] = 'darkgreen'
    
    lcd=DigitalClock(root)
    lcd.label.pack()
    #now = time.strftime("%H:%M:%S")
    now = datetime.now().strftime("%H:%M:%S")
    #now = time(hour=1,minute=2,second=3)
    print('now=',now)
    lcd.set(now)
    
    root.mainloop()

