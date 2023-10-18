#!/usr/bin/python3

from suntime import Sun
import lnetatmo
import configparser
from datetime import datetime, timezone
import pytz
import os
import sys
import logging
import locale
from PIL import Image,ImageDraw,ImageFont
from widgets import Screen, HStack, VStack, ZStack, Spacer, TextWidget, TextAlign, ModuleWidget

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

# Get highlight values
highlight_humidity = config.getint('highlight', 'humidity')
highlight_co2 = config.getint('highlight', 'co2')

if not export_image:
    from waveshare_epd import epd7in5_HD as epd
    from waveshare_epd import epdconfig

welcomeText = TextWidget("Netatmo").addTextLine("Display").setPadding(vertical = 100, horizontal = 100)
welcomeScreen = Screen(width = image_width, height = image_height, save_image = export_image).setView(welcomeText)
lastImage = welcomeScreen.render()


# Initiate Netatmo client
try:
    authorization = lnetatmo.ClientAuth()
    weatherData = lnetatmo.WeatherStationData(authorization)
    #print(weatherData.rawData)
    # print(weatherData.default_station)
    # print(weatherData.stations)
    # print(weatherData.modules)
except:
    print("outch")

coords = weatherData.stations[weatherData.default_station]['place']['location']
tzone = pytz.timezone(weatherData.stations[weatherData.default_station]['place']['timezone'])
sun = Sun(coords[1], coords[0])
rise_time = sun.get_sunrise_time().astimezone(tzone).strftime("%H:%M")
set_time = sun.get_sunset_time().astimezone(tzone).strftime("%H:%M")
logging.info('Sunrise is %s and Sunset at %s', rise_time, set_time)

current_date = datetime.now().strftime('%d. %B')#.decode('utf-8')

main_module = [weatherData.stations[weatherData.default_station]]
outdoor_module = []
rain_module = []
wind_module = []
other_modules = []

for module in weatherData.modules.keys():
    m_data_type = weatherData.modules[module]['data_type']
    if ('Temperature' in m_data_type and 'CO2' not in m_data_type):
        outdoor_module.append(weatherData.modules[module])
    elif ('CO2' in m_data_type):
        other_modules.append(weatherData.modules[module])
    elif ('Wind' in m_data_type):
        wind_module.append(weatherData.modules[module])
    elif ('Rain' in m_data_type):
        rain_module.append(weatherData.modules[module])

print("main", main_module)
print("outdoor", outdoor_module)
print("rain", rain_module)
print("wind", wind_module)
for module in other_modules:
    print("other", module)

screen = Screen(width = image_width, height = image_height, save_image = export_image)
base_layout = VStack()
screen.setPadding(horizontal = 10, vertical = 10).setView(base_layout)

# First row
# Left part
outdoor_module_widget = ModuleWidget().setWidth(350).setHeight(200)
outdoor_module_widget.setHeader(str(outdoor_module[0]['dashboard_data']['Humidity']) + "%, " + str(main_module[0]['dashboard_data']['Pressure']) + "mbar")
outdoor_module_widget.setBody(str(round(outdoor_module[0]['dashboard_data']['Temperature'], 1)) + u'\N{DEGREE SIGN}')
outdoor_module_widget.setFooter(outdoor_module[0]['module_name'] + " (Stand " + datetime.fromtimestamp(main_module[0]['last_status_store']).strftime('%H:%M') + ")")

# Right part
date_display = TextWidget(current_date).setHeight(80).setTextSize(66).setTextAlign(TextAlign.LEFT)

sunrise_text = TextWidget("Sonnenaufgang:").setTextSize(22).setTextAlign(TextAlign.LEFT)
sunset_text = TextWidget("Sonnenuntergang:").setTextSize(22).setTextAlign(TextAlign.LEFT)
sun_text = VStack().setWidth(200).addView(sunrise_text).addView(sunset_text)

sunrise_time = TextWidget(rise_time).setTextSize(22).setTextAlign(TextAlign.RIGHT)
sunset_time = TextWidget(set_time).setTextSize(22).setTextAlign(TextAlign.RIGHT)
sun_time = VStack().setWidth(60).addView(sunrise_time).addView(sunset_time)

temp_min_text = TextWidget("Min:").setTextSize(22).setTextAlign(TextAlign.LEFT)
temp_max_text = TextWidget("Max:").setTextSize(22).setTextAlign(TextAlign.LEFT)
temp_text = VStack().setWidth(60).addView(temp_min_text).addView(temp_max_text)

temp_min_value = TextWidget(str(outdoor_module[0]['dashboard_data']['min_temp']) + u'\N{DEGREE SIGN}').setTextSize(22).setTextAlign(TextAlign.RIGHT)
temp_max_value = TextWidget(str(outdoor_module[0]['dashboard_data']['max_temp']) + u'\N{DEGREE SIGN}').setTextSize(22).setTextAlign(TextAlign.RIGHT)
temp_values = VStack().setWidth(60).addView(temp_min_value).addView(temp_max_value)

day_info = HStack().setHeight(50).addView(sun_text).addView(sun_time).addView(Spacer()).addView(temp_text).addView(temp_values).addView(Spacer().setWidth(10))

date_corner = VStack().setWidth(450).setHeight(200).addView(Spacer()).addView(date_display).addView(Spacer().setHeight(10)).addView(day_info).addView(Spacer())
top_row = HStack().addView(outdoor_module_widget).addView(Spacer()).addView(date_corner)
base_layout.addView(top_row)

# Second row
module_widgets_row = HStack().setHeight(100).setGap(10)

# Main Module
main_module_widget = ModuleWidget()
main_module_widget.setHeader(str(main_module[0]['dashboard_data']['Humidity']) + "%, " + str(main_module[0]['dashboard_data']['CO2']) + "ppm")
main_module_widget.setBody(str(round(main_module[0]['dashboard_data']['Temperature'], 1)))
main_module_widget.setFooter(main_module[0]['module_name'])
if main_module[0]['dashboard_data']['Humidity'] >= highlight_humidity or main_module[0]['dashboard_data']['CO2'] >= highlight_co2:
    main_module_widget.invert()
module_widgets_row.addView(main_module_widget)

# Additional Modules
for module in other_modules:
    other_module_widget = ModuleWidget()
    other_module_widget.setHeader(str(module['dashboard_data']['Humidity']) + "%, " + str(module['dashboard_data']['CO2']) + "ppm")
    other_module_widget.setBody(str(round(module['dashboard_data']['Temperature'], 1)))
    other_module_widget.setFooter(module['module_name'])
    if module['dashboard_data']['Humidity'] >= highlight_humidity or module['dashboard_data']['CO2'] >= highlight_co2:
        other_module_widget.invert()
    module_widgets_row.addView(other_module_widget)

# Rain Module
if len(rain_module) > 0:
    rain_module_widget = ModuleWidget()
    rain_module_widget.setHeader("Regen vor ")
    rain_module_widget.setBody("TODO mm")
    rain_module_widget.setFooter(rain_module[0]['module_name'])
    module_widgets_row.addView(rain_module_widget)

base_layout.addView(module_widgets_row)

# Third row

base_layout.addView(Spacer())
screen.render()