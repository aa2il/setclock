#! /usr/bin/python3
#
# This seems pretty easy - Rerun if it fails the first time
#
# To get this to work:
#    sudo apt-get install gpsd gpsd-clients python3-gps
# then run the get_time script in ~/bin
#
# Don't seem to need this but keeping note just in case:
#pip3 install gpsd-py3
#https://github.com/MartijnBraam/gpsd-py3
#
#####################################################################

import gpsd
from pprint import pprint

"""

# Connect to the local gpsd
gpsd.connect()

# Connect somewhere else
#gpsd.connect(host="127.0.0.1", port=123456)

# Get gps position
packet = gpsd.get_current()

# See the inline docs for GpsResponse for the available data
print(packet.position())

"""

import gpsd

# Connect to the local gpsd
gpsd.connect()

# Connect somewhere else
#
#gpsd.connect()

# Get gps position
packet = gpsd.get_current()
print('\nPacket:')
pprint(vars(packet))

# See the inline docs for GpsResponse for the available data
print("\n ************ PROPERTIES ************* ")
print("  Mode: " + str(packet.mode))
print("Satellites: " + str(packet.sats))
if packet.mode >= 2:
    print("  Latitude: " + str(packet.lat))
    print(" Longitude: " + str(packet.lon))
    print(" Track: " + str(packet.track))
    print("  Horizontal Speed: " + str(packet.hspeed))
    print(" Time: " + str(packet.time))
    print(" Error: " + str(packet.error))
else:
    print("  Latitude: NOT AVAILABLE")
    print(" Longitude: NOT AVAILABLE")
    print(" Track: NOT AVAILABLE")
    print("  Horizontal Speed: NOT AVAILABLE")
    print(" Error: NOT AVAILABLE")

if packet.mode >= 3:
    print("  Altitude: " + str(packet.alt))
    print(" Climb: " + str(packet.climb))
else:
    print("  Altitude: NOT AVAILABLE")
    print(" Climb: NOT AVAILABLE")

print(" ************** METHODS ************** ")
if packet.mode >= 2:
    print("  Location: " + str(packet.position()))
    print(" Speed: " + str(packet.speed()))
    print("Position Precision: " + str(packet.position_precision()))
    #print("  Time UTC: " + str(packet.time_utc()))              # These aren't available?
    #print("Time Local: " + str(packet.time_local()))
    print("   Map URL: " + str(packet.map_url()))
else:
    print("  Location: NOT AVAILABLE")
    print(" Speed: NOT AVAILABLE")
    print("Position Precision: NOT AVAILABLE")
    print("  Time UTC: NOT AVAILABLE")
    print("Time Local: NOT AVAILABLE")
    print("   Map URL: NOT AVAILABLE")

if packet.mode >= 3:
    print("  Altitude: " + str(packet.altitude()))
    # print("  Movement: " + str(packet.movement()))
    # print("  Speed Vertical: " + str(packet.speed_vertical()))
else:
    print("  Altitude: NOT AVAILABLE")
    # print("  Movement: NOT AVAILABLE")
    # print(" Speed Vertical: NOT AVAILABLE")

print(" ************* FUNCTIONS ************* ")
print("Device: " + str(gpsd.device()))
