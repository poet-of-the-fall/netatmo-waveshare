try:
    from typing import Self
except ImportError:
    from typing_extensions import Self
from .View import View
from .VStack import VStack
from .HStack import HStack
from .ZStack import ZStack
from .TextWidget import TextWidget, TextAlignVertical
from .ImageWidget import ImageWidget
from .ConfigHelper import ConfigHelper
from PIL import Image, ImageDraw, ImageFont
import os
import math
from datetime import datetime, timezone
from lnetatmo import WeatherStationData
import logging

class ModuleWidget(View):
    header: str
    body: None # should be: str | View
    footer: str
    ratio: float
    unit: str = None
    unit_ratio: float
    
    def __init__(self, header: str = "", body: str = "", footer: str = "", ratio: float = 0.2, unit: str = None, unit_ratio: float = 0.2):
        super().__init__()
        self.setHeader(text = header)
        self.setBody(text = body)
        self.setFooter(text = footer)
        self.setRatio(ratio = ratio)
        if unit:
            self.setUnit(text = unit)
        self.setUnitRatio(ratio = unit_ratio)
    
    def setHeader(self, text: str) -> Self:
        self.header = text
        return self
    
    def setBody(self, text: str) -> Self:
        self.body = text
        return self
    
    def setFooter(self, text: str) -> Self:
        self.footer = text
        return self
    
    def setRatio(self, ratio: float) -> Self:
        if ratio > 0.4 and ratio <= 0.95:
            ratio = (1 - ratio) / 2
        if ratio > 0.9 or ratio < 0.05:
            ratio = 0.2
        self.ratio = ratio
        return self
    
    def setUnit(self, text: str) -> Self:
        self.unit = text
        return self
    
    def setUnitRatio(self, ratio: float) -> Self:
        if ratio > 0.4 and ratio <= 0.95:
            ratio = (1 - ratio) / 2
        if ratio > 0.9 or ratio < 0.05:
            ratio = 0.2
        self.unit_ratio = ratio
        return self
    
    def prepareBody(self) -> View:
        body_value = TextWidget(self.body).setTextAlignVertical(TextAlignVertical.BOTTOM)
        body = HStack().addView(body_value).setWidth(self.width - 2 * self.padding_horizontal).setHeight(round((self.height - 2 * self.padding_vertical) * ( 1 - 2 * self.ratio)))

        fontdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Font.ttc')
        image = Image.new('RGBA', (self.width, self.height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)
        body.prepareChild()
        body_value.setTextSize(body_value.calculateTextSize(different_height = math.floor(body_value.height * 1.175)))
        body_value.setWidth(0)
        body_value.setHeight(0)

        if self.unit:
            width = 0
            body.prepareChild()
            text_size = body_value.calculateTextSize(different_width = math.floor((self.width - 2 * self.padding_horizontal) * (1 - self.unit_ratio)), different_height = math.floor(body_value.height * 1.175))
            body_value.setTextSize(text_size)
            font = ImageFont.truetype(fontdir, text_size)
            l, t, r, b = draw.textbbox((0,0), self.body, font)
            unit_width = round((self.width - 2 * self.padding_horizontal) * self.unit_ratio)
            width = r + unit_width
            body_unit = TextWidget(self.unit).setPadding(vertical = self.height * (1 - self.ratio) * 0.1, horizontal = 0).setTextAlignVertical(TextAlignVertical.BOTTOM).setWidth(unit_width)
            
            body.addView(body_unit)
            body.setPadding(vertical = 0, horizontal = round((self.width - 2 * self.padding_horizontal - width) / 2))
        
        body_value.setWidth(0)
        body_value.setHeight(0)
        body.prepareChild()
        return body

    def render(self) -> Image:
        header = TextWidget(self.header).setHeight(round((self.height - 2 * self.padding_vertical) * self.ratio))
        footer = TextWidget(self.footer).setHeight(round((self.height - 2 * self.padding_vertical) * self.ratio))
        if type(self.body) is str:
            body = self.prepareBody()
        else:
            body = self.body.setWidth(self.width - 2 * self.padding_horizontal).setHeight(round((self.height - 2 * self.padding_vertical) * ( 1 - 2 * self.ratio)))
        module = VStack().setPadding(vertical = self.padding_vertical, horizontal = self.padding_horizontal)
        module.setHeight(self.height).setWidth(self.width).addView(header).addView(body).addView(footer).prepareChild()

        sizes = []
        sizes.append(header.calculateTextSize())
        sizes.append(footer.calculateTextSize())
        header.setTextSize(min(sizes))
        footer.setTextSize(min(sizes))

        self.image = module.render()
        draw = ImageDraw.Draw(self.image)

        upper = header.height + self.padding_vertical
        lower = self.height - footer.height - self.padding_vertical
        draw.line((self.padding_horizontal, upper, self.width - 2 * self.padding_horizontal, upper), fill = (0, 0, 0, 255))
        draw.line((self.padding_horizontal, lower, self.width - 2 * self.padding_horizontal, lower), fill = (0, 0, 0, 255))

        super().render()
        return self.image
    
class MainModuleWidget(ModuleWidget):
    def __init__(self, module, ratio: float = 0.2):
        config = ConfigHelper()
        header = ""
        if 'dashboard_data' in module:
            header = str(module['dashboard_data']['Humidity']) + "%, " + str(module['dashboard_data']['CO2']) + "ppm"
        body = config.format_decimal(module['dashboard_data']['Temperature']) + u'\N{DEGREE SIGN}'
        footer = module['module_name']
        super().__init__(header, body, footer, ratio)
        if 'dashboard_data' in module:
            if module['dashboard_data']['Humidity'] >= config.highlight_humidity_max or module['dashboard_data']['CO2'] >= config.highlight_co2_max:
                self.invert()
    
class OutdoorModuleWidget(ModuleWidget):
    def __init__(self, module, main_module, ratio: float = 0.2):
        config = ConfigHelper()
        header = ""
        if 'dashboard_data' in module:
            header = str(module['dashboard_data']['Humidity']) + "%, " + config.format_decimal(main_module['dashboard_data']['Pressure']) + "mbar"
        body = config.format_decimal(module['dashboard_data']['Temperature']) + u'\N{DEGREE SIGN}'
        footer = module['module_name'] + " (Stand " + datetime.fromtimestamp(main_module['last_status_store']).strftime('%H:%M') + ")"
        super().__init__(header, body, footer, ratio)
        if module['battery_percent'] < config.highlight_battery_min:
            self.setShowFrame(show_frame = True)

class IndoorModuleWidget(ModuleWidget):
    def __init__(self, module, ratio: float = 0.2):
        config = ConfigHelper()
        header = ""
        if 'dashboard_data' in module:
            header = str(module['dashboard_data']['Humidity']) + "%, " + str(module['dashboard_data']['CO2']) + "ppm"
        body = config.format_decimal(module['dashboard_data']['Temperature']) + u'\N{DEGREE SIGN}'
        footer = module['module_name']
        super().__init__(header, body, footer, ratio)
        if module['battery_percent'] < config.highlight_battery_min:
            self.setShowFrame(show_frame = True)
        if 'dashboard_data' in module:
            if module['dashboard_data']['Humidity'] >= config.highlight_humidity_max or module['dashboard_data']['CO2'] >= config.highlight_co2_max:
                self.invert()
    
class RainModuleWidget(ModuleWidget):
    def __init__(self, module, main_module, netatmo_client: WeatherStationData, ratio: float = 0.2, unit: str = "mm", unit_ratio: float = 0.2):
        config = ConfigHelper()

        # Get hourly rain of last month
        now = datetime.now(timezone.utc).timestamp()
        last_month  = now - 36 * 24 * 3600
        hours = 0
        time_unit = "?"
        try:
            measure = netatmo_client.getMeasure(main_module["_id"], '1hour', 'sum_rain', module["_id"], date_begin = last_month, date_end = now, optimize = True)
            hours = 0

            rain_hour_values = []

            if measure and measure['body']:
                for chunk in measure['body']:
                    rain_hour_values.extend(chunk['value'])
                rain_hour_values = [v[0] for v in rain_hour_values]
                logging.debug('Rain values: %s', rain_hour_values)
                for x in reversed(rain_hour_values):
                    if x > 0:
                        break
                    hours = hours + 1
                time_unit = 'h'
                if hours > 24:
                    hours = int(hours / 24)
                    time_unit = 'd'
        except:
            logging.warning('Fetching rain data failed!')

        sum_rain = 0
        if 'dashboard_data' in module:
            sum_rain = module['dashboard_data']['sum_rain_24'] if 'sum_rain_24' in module['dashboard_data'] else 0
        header = "Regen vor " + str(hours) + time_unit
        body = config.format_decimal(sum_rain)
        footer = module['module_name']
        super().__init__(header, body, footer, ratio, unit, unit_ratio)
        if module['battery_percent'] < config.highlight_battery_min:
            self.setShowFrame(show_frame = True)
    
class WindModuleWidget(ModuleWidget):
    def __init__(self, module, main_module, netatmo_client: WeatherStationData, ratio: float = 0.2):
        config = ConfigHelper()

        now = datetime.now(timezone.utc).timestamp()
        last_day  = now - 24 * 3600
        wind_angle_history = Image.new('RGBA', (100, 100), (255, 255, 255, 0))
        draw_wind_angle = ImageDraw.Draw(wind_angle_history)
        draw_wind_angle.ellipse((2, 2, 98, 98), (255, 255, 255, 1), (0, 0, 0), 4)
        try:
            measure = netatmo_client.getMeasure(main_module['_id'], '30min', 'windangle', module['_id'], date_begin = last_day, date_end = now, optimize = True)
            angle_values = []
            if measure and measure['body']:
                for chunk in measure['body']:
                    angle_values.extend(chunk['value'])
                angle_values = [v[0] for v in angle_values]
                logging.debug('Wind angle values: %s', angle_values)
                for x in angle_values:
                    draw_wind_angle.arc((10, 10, 90, 90), x - 95, x - 85, (0, 0, 0), 10)
        except:
            logging.warning('Fetching wind angle data failed!')

        current_angle = 0
        current_strength = 1
        if 'dashboard_data' in module:
            current_angle = 360 - module['dashboard_data']['WindAngle'] if module['dashboard_data']['WindAngle'] else 0
            current_strength = module['dashboard_data']['WindStrength'] if module['dashboard_data']['WindStrength'] else 1
        wind_gauge = Image.new('RGBA', (100, 100), (255, 255, 255, 0))
        draw_wind_gauge = ImageDraw.Draw(wind_gauge)
        polygon_points = [(30, 30), (50, 42), (70, 30), (50, 75), (30, 30)]
        if current_strength >= config.highlight_calm_max:
            draw_wind_gauge.polygon(polygon_points, (0, 0, 0))
        else:
            draw_wind_gauge.ellipse((40, 40, 60, 60), (0, 0, 0))
        wind_gauge = wind_gauge.rotate(current_angle, resample=Image.Resampling.BICUBIC)

        wind_angle_history.paste(wind_gauge, mask=wind_gauge)

        header = ""
        if 'dashboard_data' in module:
            header = str(module['dashboard_data']['WindStrength']) + 'km/h (max: ' + str(module['dashboard_data']['max_wind_str'] if 'max_wind_str' in module['dashboard_data'] else 0) + ')'
        body = ZStack().addView(ImageWidget(wind_angle_history)).setPadding(2, 2)
        footer = module['module_name']
        super().__init__(header, body, footer, ratio)
        if module['battery_percent'] < config.highlight_battery_min:
            self.setShowFrame(show_frame = True)
        if 'dashboard_data' in module:
            if module['dashboard_data']['WindStrength'] >= config.highlight_wind_max:
                self.invert()
    