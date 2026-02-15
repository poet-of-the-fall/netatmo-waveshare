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
from pathlib import Path
from PIL import Image

libdir = "./e-Paper/RaspberryPi_JetsonNano/python/lib"
if os.path.exists(libdir):
    sys.path.append(libdir)

fontdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Font.ttc')

# Set locale
locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')

# Get config
config = ConfigHelper()
refresh_interval = config.refresh_interval_s

# Configure logging
numeric_level = getattr(logging, config.log_level, None)
logging.basicConfig(filename='log.log',format='%(asctime)s %(levelname)s: %(message)s',level=numeric_level)

if not config.export_image:
    from waveshare_epd import epd2in7_V2 as epd
    from waveshare_epd import epdconfig
    from gpiozero import Button
else:
    Button = None
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
            epd.EPD().display(epd.EPD().getbuffer(last_images[current_page]))

        except IOError as e:
            logging.info(e)

        except KeyboardInterrupt:
            exit_handler()

welcomeText = TextWidget("Netatmo").addTextLine("Display").setPadding(vertical = 10, horizontal = 10)
welcomeScreen = Screen().setView(welcomeText)
last_images = [welcomeScreen.render(), welcomeScreen.render(), welcomeScreen.render(), welcomeScreen.render(), welcomeScreen.render(), welcomeScreen.render(), welcomeScreen.render(), welcomeScreen.render()]
current_page: int = 3
show_secondary: bool = False
renderToDisplay()
del welcomeScreen

def renderError(text: str):
    global last_images
    warning_text = TextWidget(text).setTextAlignHorizontal(TextAlignHorizontal.CENTER).setHeight(25).invert()
    warning_message = VStack().addView(Spacer()).addView(warning_text).addView(Spacer())
    for image in last_images:
        layers = ZStack().addView(ImageWidget(image)).addView(warning_message)
        screen = Screen().setView(layers)
        image = screen.render()
    renderToDisplay()
    del screen

# Button press
def handleButtonPress(btn):
    global current_page
    global show_secondary
    switcher = {
        5: 0,
        6: 1,
        13: 2,
        19: 3
    }
    page = switcher.get(btn.pin.number, "Error") + (4 if show_secondary else 0)
    if current_page == page:
        show_secondary = not show_secondary
        page = switcher.get(btn.pin.number, "Error") + (4 if show_secondary else 0)
    current_page = page 
    renderToDisplay()

if Button:
    Button(5).when_pressed = handleButtonPress
    Button(6).when_pressed = handleButtonPress
    Button(13).when_pressed = handleButtonPress
    Button(19).when_pressed = handleButtonPress

startup = True
lastUpdate = 0
authorization = lnetatmo.ClientAuth()

path = Path.cwd()
caravan = VStack().setShowFrame(True).addView(Spacer()).addView(ImageWidget(Image.open(path / 'images' / 'caravan.png'))).addView(Spacer())
caravan_inverted = VStack().invert().setShowFrame(True).addView(Spacer()).addView(ImageWidget(Image.open(path / 'images' / 'caravan.png'))).addView(Spacer())
tent = VStack().setShowFrame(True).addView(Spacer()).addView(ImageWidget(Image.open(path / 'images' / 'tent.png'))).addView(Spacer())
tent_inverted = VStack().invert().setShowFrame(True).addView(Spacer()).addView(ImageWidget(Image.open(path / 'images' / 'tent.png'))).addView(Spacer())
outside = VStack().setShowFrame(True).addView(Spacer()).addView(ImageWidget(Image.open(path / 'images' / 'palm.png'))).addView(Spacer())
outside_inverted = VStack().invert().setShowFrame(True).addView(Spacer()).addView(ImageWidget(Image.open(path / 'images' / 'palm.png'))).addView(Spacer())
all = VStack().setHeight(25).setShowFrame(True).addView(ImageWidget(Image.open(path / 'images' / 'grid.png')).setPadding(2, 2))
all_inverted = VStack().invert().setHeight(25).setShowFrame(True).addView(ImageWidget(Image.open(path / 'images' / 'grid.png')).setPadding(2, 2))
navigation1 = VStack().setWidth(25).addView(caravan_inverted).addView(tent).addView(outside).addView(all)
navigation2 = VStack().setWidth(25).addView(caravan).addView(tent_inverted).addView(outside).addView(all)
navigation3 = VStack().setWidth(25).addView(caravan).addView(tent).addView(outside_inverted).addView(all)
navigation4 = VStack().setWidth(25).addView(caravan).addView(tent).addView(outside).addView(all_inverted)
navigation = [navigation1, navigation2, navigation3, navigation4, navigation1, navigation2, navigation3, navigation4]

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
            logging.warning('No Data at startup, maybe no WiFi. Waiting 10 Seconds.')
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
    outdoor_module = []
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

    content = [VStack().setPadding(10, 10), VStack().setPadding(10, 10), VStack().setPadding(10, 10), VStack().setPadding(10, 10), VStack().setPadding(10, 10), VStack().setPadding(10, 10), VStack().setPadding(10, 10), VStack().setPadding(10, 10)]
    content[0].addView(IndoorModuleWidget(other_modules[0]))
    content[1].addView(MainModuleWidget(main_module[0]))
    content[2].addView(OutdoorModuleWidget(outdoor_module[0], main_module[0]))

    min_temp = 0
    max_temp = 0
    if 'dashboard_data' in outdoor_module[0]:
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
    temp_block = HStack().setGap(5).addView(temp_value).addView(temp_text)
    min_max = VStack().addView(temp_block)
    first_row = HStack().setGap(10).addView(OutdoorModuleWidget(outdoor_module[0], main_module[0])).addView(min_max)
    second_row = HStack().setGap(10).addView(IndoorModuleWidget(other_modules[0])).addView(MainModuleWidget(main_module[0]))
    content[3].setGap(10).addView(first_row).addView(second_row)

    content[4].addView(GraphWidget(other_modules[0], main_module[0], weatherData, 2, False))
    content[5].addView(GraphWidget(main_module[0], main_module[0], weatherData, 2, False))
    content[6].addView(GraphWidget(outdoor_module[0], main_module[0], weatherData, 2, False))

    coords = weatherData.stations[weatherData.default_station]['place']['location']
    tzone = pytz.timezone(weatherData.stations[weatherData.default_station]['place']['timezone'])
    sun = Sun(coords[1], coords[0])
    rise_time = sun.get_sunrise_time().astimezone(tzone).strftime("%-H:%M")
    set_time = sun.get_sunset_time().astimezone(tzone).strftime("%-H:%M")
    current_date = datetime.now().strftime('%d. %B')#.decode('utf-8')
    date_display = TextWidget(current_date).setHeight(40).setTextSize(30).setTextAlignHorizontal(TextAlignHorizontal.CENTER)
    sunrise = TextWidget("Sonnenaufgang").addTextLine(rise_time).setTextSize(18).setTextAlignHorizontal(TextAlignHorizontal.CENTER)
    sunset = TextWidget("Sonnenuntergang").addTextLine(set_time).setTextSize(18).setTextAlignHorizontal(TextAlignHorizontal.CENTER)
    content[7].addView(date_display).addView(Spacer().setHeight(20)).addView(sunrise).addView(Spacer().setHeight(10)).addView(sunset)

    for i in range(len(content)):
        screen = Screen()
        base_layout = HStack()
        base_layout.addView(navigation[i]).addView(content[i])
        screen.setView(base_layout)
        try:
            last_images[i] = screen.render()
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
    logging.info('Update time ago: %s, need to wait: %s', delta, refresh_interval - delta) 
    time.sleep((refresh_interval - delta) if (delta < refresh_interval) else 10)

exit()
