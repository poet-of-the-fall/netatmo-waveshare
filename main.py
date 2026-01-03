#!/usr/bin/python3

from suntime import Sun
import lnetatmo
from datetime import datetime, timezone
import time
import pytz
import os
import sys
import logging
import locale
from widgets import *
import signal

libdir = "./e-Paper/RaspberryPi_JetsonNano/python/lib"
if os.path.exists(libdir):
    sys.path.append(libdir)

fontdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Font.ttc')

# Set locale
locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')

# Get config
config = ConfigHelper()

# Configure logging
numeric_level = getattr(logging, config.log_level, None)
logging.basicConfig(filename='log.log',format='%(asctime)s %(levelname)s: %(message)s',level=numeric_level)

if not config.export_image:
    from waveshare_epd import epd7in5_HD as epd
    from waveshare_epd import epdconfig
else:
    epd = None
    
# Handle script exit
def exit_handler(first=None, second=None):
    logging.info('Script stopped')
    logging.debug(first, second)
    if not config.export_image:
        epd.EPD().Clear()
        epdconfig.module_exit()
    exit()

signal.signal(signal.SIGINT, exit_handler)
signal.signal(signal.SIGTERM, exit_handler)
signal.signal(signal.SIGABRT, exit_handler)

def renderToDisplay():
    if epd:
        try:
            logging.info("Power up display")
            epd.EPD().init()
            epd.EPD().Clear()
            epd.EPD().display(epd.EPD().getbuffer(last_image))

        except IOError as e:
            logging.info(e)

        except KeyboardInterrupt:
            exit_handler()

welcomeText = TextWidget("Netatmo").addTextLine("Display").setPadding(vertical = 100, horizontal = 100)
welcomeScreen = Screen().setView(welcomeText)
last_image = welcomeScreen.render()
renderToDisplay()
del welcomeScreen

def renderError(text: str):
    global last_image
    warning_text = TextWidget(text).setTextAlignHorizontal(TextAlignHorizontal.CENTER).setHeight(25).invert()
    warning_message = VStack().addView(Spacer()).addView(warning_text).addView(Spacer())
    layers = ZStack().addView(ImageWidget(last_image)).addView(warning_message)
    screen = Screen().setView(layers)
    last_image = screen.render()
    renderToDisplay()
    del screen

startup = True
lastUpdate = 0
authorization = lnetatmo.ClientAuth()

while True:
    # Initiate Netatmo client
    try:
        weatherData = lnetatmo.WeatherStationData(authorization)
        # print(weatherData.rawData)
        # print(weatherData.default_station)
        # print(weatherData.stations)
        # print(weatherData.modules)
    except Exception as e:
        if startup:
            logging.warning('No Data at sturtup, maybe no WiFi. Waiting 10 Seconds.')
            time.sleep(10)
            continue
        else: 
            logging.warning('Fetching data failed! Waiting 20 Minutes.')
            logging.warning(e)
            renderError("Aktuelle Daten konnten nicht geladen werden.")
            time.sleep(1200)
            continue

    startup = False

    main_module = [weatherData.stations[weatherData.default_station]]
    second_station = [weatherData.stations['Barbing (Keller)']]
    outdoor_module = []
    rain_module = []
    wind_module = []
    other_modules = []

    if main_module[0]["reachable"] == False:
        logging.warning('Station not reachable! Waiting 20 Minutes.')
        renderError("Station nicht verbunden.")
        time.sleep(1200)
        continue

    updateTimeUTC = main_module[0]["last_status_store"]
    updateTime = datetime.fromtimestamp(updateTimeUTC) 
    logging.info('Last update: %s', updateTime.strftime('%A, %d.%m.%Y %H:%M:%S'))
    if (updateTimeUTC == lastUpdate):
        logging.info("No new data in between, won't update display and sleep 60 sec")
        time.sleep(60)
        continue
    else: 
        lastUpdate = updateTimeUTC

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

    screen = Screen()
    base_layout = VStack()
    screen.setPadding(horizontal = 10, vertical = 10).setView(base_layout)

    # First row
    # Left part
    outdoor_module_widget = OutdoorModuleWidget(outdoor_module[0], main_module[0], 0.15).setWidth(335)

    # Middle part
    coords = weatherData.stations[weatherData.default_station]['place']['location']
    tzone = pytz.timezone(weatherData.stations[weatherData.default_station]['place']['timezone'])
    sun = Sun(coords[1], coords[0])
    rise_time = sun.get_sunrise_time().astimezone(tzone).strftime("%-H:%M")
    set_time = sun.get_sunset_time().astimezone(tzone).strftime("%-H:%M")
    logging.debug('Sunrise is %s and Sunset at %s', rise_time, set_time)

    current_date = datetime.now().strftime('%d. %B')#.decode('utf-8')

    date_display = TextWidget(current_date).setHeight(60).setTextSize(50).setTextAlignHorizontal(TextAlignHorizontal.CENTER)

    sunrise_time = TextWidget(rise_time).setTextSize(18).setTextAlignHorizontal(TextAlignHorizontal.RIGHT)
    sunset_time = TextWidget(set_time).setTextSize(18).setTextAlignHorizontal(TextAlignHorizontal.RIGHT)
    sun_value = VStack().addView(sunrise_time).addView(sunset_time)
    sunrise_text = TextWidget("Sonnenaufgang").setTextSize(18).setTextAlignHorizontal(TextAlignHorizontal.LEFT).setTextAlignVertical(TextAlignVertical.BOTTOM)
    sunset_text = TextWidget("Sonnenuntergang").setTextSize(18).setTextAlignHorizontal(TextAlignHorizontal.LEFT).setTextAlignVertical(TextAlignVertical.BOTTOM)
    sun_text = VStack().setLayoutWeight(3).addView(sunrise_text).addView(sunset_text)
    sun_block = HStack().setGap(10).addView(Spacer()).addView(sun_value).addView(sun_text).addView(Spacer())


    min_temp = "?"
    max_temp = "?"
    if outdoor_module[0]:
        min_temp = outdoor_module[0]['dashboard_data']['Temperature']
        if 'min_temp' in outdoor_module[0]['dashboard_data']: # might be empty right after midnight
            min_temp = outdoor_module[0]['dashboard_data']['min_temp']
        max_temp = outdoor_module[0]['dashboard_data']['Temperature']
        if 'max_temp' in outdoor_module[0]['dashboard_data']: 
            max_temp = outdoor_module[0]['dashboard_data']['max_temp']
    temp_min_value = TextWidget(config.format_decimal(min_temp) + u'\N{DEGREE SIGN}').setTextSize(18).setTextAlignHorizontal(TextAlignHorizontal.RIGHT)
    temp_max_value = TextWidget(config.format_decimal(max_temp) + u'\N{DEGREE SIGN}').setTextSize(18).setTextAlignHorizontal(TextAlignHorizontal.RIGHT)
    temp_value = VStack().addView(temp_min_value).addView(temp_max_value)
    temp_min_text = TextWidget("Min").setTextSize(18).setTextAlignHorizontal(TextAlignHorizontal.LEFT)
    temp_max_text = TextWidget("Max").setTextSize(18).setTextAlignHorizontal(TextAlignHorizontal.LEFT)
    temp_text = VStack().addView(temp_min_text).addView(temp_max_text)
    temp_block = HStack().setGap(10).addView(Spacer()).addView(temp_value).addView(temp_text).addView(Spacer())

    date_corner = VStack().addView(date_display).addView(Spacer().setHeight(15)).addView(sun_block).addView(temp_block)

    # Right Part
    other_outdoor_widgets = VStack().setGap(15).setWidth(160)
    # Rain Module
    if len(rain_module) > 0:
        rain_module_widget = RainModuleWidget(rain_module[0], main_module[0], weatherData, 0.25)
        other_outdoor_widgets.addView(rain_module_widget)
    # Wind Module
    if len(wind_module) > 0:
        wind_module_widget = WindModuleWidget(wind_module[0], main_module[0], weatherData, 0.25)
        other_outdoor_widgets.addView(wind_module_widget)

    top_row = HStack().setGap(15).addView(outdoor_module_widget).addView(date_corner).addView(other_outdoor_widgets).setHeight(185)
    base_layout.addView(top_row)

    # Second row
    module_widgets_row = HStack().setHeight(115).setGap(15).setPadding(horizontal = 0, vertical = 15)

    # Main Module
    main_module_widget = MainModuleWidget(main_module[0], 0.25)
    module_widgets_row.addView(main_module_widget)

    # Additional Modules
    for module in other_modules:
        other_module_widget = IndoorModuleWidget(module, 0.25)
        module_widgets_row.addView(other_module_widget)

    # Module from other station
    if second_station[0]:
        other_module_widget = MainModuleWidget(second_station[0], 0.25)
        module_widgets_row.addView(other_module_widget)

    base_layout.addView(module_widgets_row)

    # Third row
    
    base_layout.addView(GraphWidget(outdoor_module[0], main_module[0], weatherData, rain_module=(rain_module[0] if len(rain_module) > 0 else None)))
    try:
        last_image = screen.render()
    except:
        logging.warning('Screen could not render.')
        renderError("Fehler")
        time.sleep(1200)
        continue
    
    # Draw image
    renderToDisplay()
    del screen

    # Wait time for next update
    delta = (datetime.now() - updateTime).total_seconds()
    logging.info('Update time ago: %s, need to wait: %s', delta, 600 - delta) 
    time.sleep((600 - delta) if (delta < 600) else 10)

exit()
