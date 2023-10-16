#!/usr/bin/python3

from suntime import Sun
import lnetatmo
import configparser
from datetime import datetime, timezone
import os
import sys
import logging
import locale
from PIL import Image,ImageDraw,ImageFont
from widgets import Screen, HStack, VStack, ZStack, Spacer

libdir = "./e-Paper/RaspberryPi_JetsonNano/python/lib"
if os.path.exists(libdir):
    sys.path.append(libdir)

fontdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Font.ttc')

# Set locale
locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')

# Load the config.ini file
path = os.path.dirname(__file__)
config = configparser.ConfigParser()
config.read(path + '/config.ini')

# Display preferences
temp_units    = config.get('general','temperature_units')

# Use Celsius unless the config file is attempting to set things to Farenheit
temp_units = 'C' if temp_units[0].upper() != 'F' else 'F'

# Configure logging
loglevel = config.get('general','loglevel')
numeric_level = getattr(logging, loglevel.upper(), None)
logging.basicConfig(filename='log.log',format='%(asctime)s %(levelname)s: %(message)s',level=numeric_level)

# Toggle image export
export_image = config.getboolean('general','export_image')
image_width = config.getint('general', 'image_width')
image_height = config.getint('general', 'image_height')

if not export_image:
    from waveshare_epd import epd7in5_HD as epd
    from waveshare_epd import epdconfig

screen = Screen(width = image_width, height = image_height, save_image = export_image)
screen.setPadding(horizontal = 10, vertical = 10)
s0 = ZStack()
s1 = VStack()
s2 = HStack()
s2.addView(Spacer().setShowFrame(show_frame = True))
s2.addView(Spacer())
s2.addView(Spacer())
s3 = HStack().setLayoutWeight(2)
s3.addView(Spacer())
s3.addView(Spacer().setShowFrame(show_frame = True).setLayoutWeight(3))
s3.addView(Spacer())
s4 = HStack().setShowFrame(show_frame = True)
s4.addView(Spacer())
s4.addView(Spacer())
s4.addView(Spacer().setShowFrame(show_frame = True))
s1.addView(s2)
s1.addView(s3)
s1.addView(s4)
s1.setGap(10)
s5 = VStack()
s5.addView(Spacer())
r = Spacer()
r.setHeight(50)
r.invert()
s5.addView(r)
s5.addView(Spacer())
s0.addView(s1)
s0.addView(s5)
screen.setView(s0)
screen.render()

# Himage = Image.new('1', (image_width, image_height), 255)
# draw = ImageDraw.Draw(Himage)
# draw.text(((image_width - draw.textlength('Netatmo', ImageFont.truetype(fontdir, 132))) / 2, 100), 'Netatmo', font = ImageFont.truetype(fontdir, 132), fill = 0)
# draw.text(((image_width - draw.textlength('Display', ImageFont.truetype(fontdir, 132))) / 2, 275), 'Display', font = ImageFont.truetype(fontdir, 132), fill = 0)
# Himage.save(str(datetime.now(timezone.utc).timestamp()) + ".png")



# Initiate Netatmo client
try:
    authorization = lnetatmo.ClientAuth()
    weatherData = lnetatmo.WeatherStationData(authorization)
    #print(weatherData.rawData)
    #print(weatherData.default_station)
    #print(weatherData.stations)
    print(weatherData.modules)
except:
    print("outch")

#sun = Sun(latitude, longitude)
#rise_time = sun.get_sunrise_time()
#set_time = sun.get_sunset_time()
#logging.info('Sunrise is %s and Sunset at %s', rise_time.strftime("%H:%M"), set_time.strftime("%H:%M"))
