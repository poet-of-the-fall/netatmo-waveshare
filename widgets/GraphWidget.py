try:
    from typing import Self
    from typing import List
except ImportError:
    from typing_extensions import Self
    from typing_extensions import List
from .View import View
from .ConfigHelper import ConfigHelper
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timezone, timedelta
from lnetatmo import WeatherStationData
import logging
import math
import os

class DataPoint(object):
    timestamp: datetime = None
    x_position: int = None
    temp_value: float = None
    rain_value: float = None
    is_midnight: bool = False
    show_tick: bool = False
    is_latest: bool = False
    day_text: str = None
    day_values: List[float] = None

    def __str__(self):
        return f"timestamp: {self.timestamp}, x_position: {self.x_position}, temp_value: {self.temp_value}, rain_value: {self.rain_value}, day_text: {self.day_text}, day_values: {self.day_values}, is_midnight: {self.is_midnight}, show_tick: {self.show_tick}, is_latest: {self.is_latest}"
    
class GraphWidget(View):
    netatmo_client: WeatherStationData
    density: int
    show_days: bool
    day_height: int
    temp_min: int
    temp_max: int
    temp_steps: int
    temp_size: int
    indicator_size: int
    line_width: int
    current_value_radius: int
    hour_tick_interval: int
    rain_module: bool
    rain_max: int
    rain_steps: int

    def __init__(self, temperature_module, main_module, netatmo_client: WeatherStationData, density: int = 4, show_days: bool = True, day_height: int = 20, temp_min: int = -10, temp_max: int = 40, temp_steps: int = 10, temp_size: int = 10, indicator_size: int = 3, line_width: int = 1, current_value_radius: int = 2, hour_tick_interval: int = 6, rain_module = None, rain_max: int = 10, rain_steps: int = 10):
        super().__init__()
        self.temperature_module = temperature_module
        self.main_module = main_module
        self.netatmo_client = netatmo_client
        self.setDensity(density)
        self.setShowDays(show_days)
        self.setDayHeight(day_height)
        self.setTempMin(temp_min)
        self.setTempMax(temp_max)
        self.setTempSteps(temp_steps)
        self.setTempSize(temp_size)
        self.setIndicatorSize(indicator_size)
        self.setLineWidth(line_width)
        self.setCurrentValueRadius(current_value_radius)
        self.setHourTickInterval(hour_tick_interval)
        self.setRainModule(rain_module)
        self.setRainMax(rain_max)
        self.setRainSteps(rain_steps)

    def setDensity(self, density: int) -> Self:
        self.density = density
        return self

    def setShowDays(self, show_days: bool) -> Self:
        self.show_days = show_days
        return self
    
    def setDayHeight(self, day_height: int) -> Self:
        self.day_height = day_height
        return self

    def setTempMin(self, temp_min: int) -> Self:
        self.temp_min = temp_min
        return self
    
    def setTempMax(self, temp_max: int) -> Self:
        self.temp_max = temp_max
        return self
    
    def setTempSteps(self, temp_steps: int) -> Self:
        self.temp_steps = temp_steps
        return self
    
    def setTempSize(self, temp_size: int) -> Self:
        self.temp_size = temp_size
        return self
    
    def setIndicatorSize(self, indicator_size) -> Self:
        self.indicator_size = indicator_size
        return self
    
    def setLineWidth(self, line_width: int) -> Self:
        self.line_width = line_width
        return self
    
    def setCurrentValueRadius(self, current_value_radius: int) -> Self:
        self.current_value_radius = current_value_radius
        return self
    
    def setHourTickInterval(self, hour_tick_interval: int) -> Self:
        self.hour_tick_interval = hour_tick_interval
        return self
        
    def setRainModule(self, rain_module: bool) -> Self:
        self.rain_module = rain_module
        return self
    
    def setRainMax(self, rain_max: int) -> Self:
        self.rain_max = rain_max
        return self
    
    def setRainSteps(self, rain_steps: int) -> Self:
        self.rain_steps = rain_steps
        return self
    
    def roundTimestampToHalfHours(self, timestamp: datetime) -> datetime:
        if timestamp.minute < 15:
            return timestamp.replace(second = 0, microsecond = 0, minute = 0)
        elif timestamp.minute < 45:
            return timestamp.replace(second = 0, microsecond = 0, minute = 30)
        else:
            return timestamp.replace(second = 0, microsecond = 0, minute = 0) + timedelta(hours = 1)
        
    def findNearestDataPoint(self, data: List[DataPoint], time: datetime) -> DataPoint:
        for i in range(len(data)):
            dp1 = data[i]
            dp2 = data[i + 1] if i < len(data) - 1 else None
            if dp1.timestamp > time:
                return dp1
                break
            elif dp1.timestamp == time:
                return dp1
            elif dp1.timestamp < time and dp2 and dp2.timestamp > time:
                if time - dp1.timestamp <= dp2.timestamp - time:
                    return dp1
                else:
                    return dp2
        return None

    def render(self) -> Image:
        config = ConfigHelper()
        fontdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Font.ttc')
        indicator_font = ImageFont.truetype(fontdir, self.temp_size)
        day_font = ImageFont.truetype(fontdir, self.day_height)
        self.image = Image.new('RGBA', (self.width, self.height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(self.image)
        now = datetime.now(timezone.utc).timestamp()
        
        # Prepare height variables
        graph_height = self.height - 2 * self.padding_vertical - 2 * self.temp_size - (self.day_height if self.show_days else 0)
        temp_range = self.temp_max - self.temp_min
        temp_resolution = graph_height / temp_range
        rain_resolution = (temp_resolution * self.temp_max) / self.rain_max
        y_zero = math.ceil(self.padding_vertical + self.temp_size + temp_resolution * self.temp_max)

        # Prepare width variables
        indicator_text_length = max(draw.textlength(str(self.temp_min) + u'\N{DEGREE SIGN}', indicator_font), draw.textlength(str(self.temp_max)  + u'\N{DEGREE SIGN}', indicator_font))
        x_start = self.padding_horizontal + indicator_text_length + self.indicator_size
        graph_width = self.width - 2 * self.padding_horizontal - indicator_text_length - self.indicator_size - self.current_value_radius
        
        # Calculate time range
        hours_visible = math.ceil(graph_width / (self.density * 2))
        days_visible = math.ceil(hours_visible / 24)

        # Prepare data
        data: List[DataPoint] = []
        x_position = x_start + math.floor((graph_width - self.current_value_radius) / self.density) * self.density
        i = 0
        while x_position >= x_start:
            dp: DataPoint = DataPoint()
            dp.timestamp = self.roundTimestampToHalfHours(datetime.fromtimestamp(now - i * 1800))
            dp.x_position = x_position
            if i == 0:
                dp.is_latest = True
            if dp.timestamp.hour == 0 and dp.timestamp.minute == 0:
                dp.is_midnight = True
                dp.day_text = dp.timestamp.strftime('%a') 
            if dp.timestamp.hour % self.hour_tick_interval == 0 and dp.timestamp.minute == 0:
                dp.show_tick = True
            data.append(dp)
            x_position = x_position - self.density
            i = i + 1
        data[-1].day_text = dp.timestamp.strftime('%a') 
        data.reverse()

        # Get temperature data
        date_begin = now - hours_visible * 3600
        try:
            temp_measures = self.netatmo_client.getMeasure(self.main_module['_id'], '30min', 'Temperature', self.temperature_module['_id'], date_begin = date_begin, date_end = now, optimize = True)

            if temp_measures:
                for chunk in temp_measures['body']:
                    begin_time = chunk['beg_time']
                    step_time = chunk['step_time']
                    values = chunk['value']
                    for i in range(len(values)):
                        time = datetime.fromtimestamp(begin_time + i * step_time)
                        value = values[i][0]
                        dp = self.findNearestDataPoint(data, time)
                        if dp:
                            dp.temp_value = value
        except:
            logging.warning('Fetching temperature data for graph failed!')

        if data[-1].temp_value == None:
            data[-2].is_latest = True

        # Get daily temperature max min values for day display if needed
        if self.show_days:
            date_begin  = now - days_visible * 24 * 3600
            try:
                minmax_measures = self.netatmo_client.getMeasure(self.main_module['_id'], '1day', 'min_temp,max_temp', self.temperature_module['_id'], date_begin = date_begin, date_end = now, optimize = True)
                
                if minmax_measures:
                    for chunk in minmax_measures['body']:
                        begin_time = chunk['beg_time']
                        step_time = chunk['step_time']
                        values = chunk['value']
                        for i in range(len(values)):
                            time = datetime.fromtimestamp(begin_time + i * step_time).replace(hour = 0)
                            dp = self.findNearestDataPoint(data, time)
                            value = values[i]
                            if dp:
                                dp.day_values = value
            except:
                logging.warning('Fetching daily temperature min and max values for graph failed!')


        # Get hourly rain data if needed
        if self.rain_module:
            date_begin  = now - hours_visible * 3600
            try:
                rain_measures = self.netatmo_client.getMeasure(self.main_module["_id"], '1hour', 'sum_rain', self.rain_module["_id"], date_begin = date_begin, date_end = now, optimize = True)

                if rain_measures and rain_measures['body']:
                    for chunk in rain_measures['body']:
                        begin_time = chunk['beg_time']
                        step_time = chunk['step_time']
                        values = chunk['value']
                        for i in range(len(values)):
                            time = datetime.fromtimestamp(begin_time + i * step_time)
                            value = values[i][0]
                            dp = self.findNearestDataPoint(data, time)
                            if dp:
                                dp.rain_value = value
            except:
                logging.warning('Fetching rain data for graph failed!')

        # Draw y axis
        draw.line((x_start, self.padding_vertical, x_start, self.height - self.padding_vertical - (self.day_height if self.show_days else 0)), fill = 0) # y axis
        text = str(0) + u'\N{DEGREE SIGN}'
        l, t, r, b = draw.textbbox((0,0), text, indicator_font)
        draw.text((x_start - self.indicator_size - r, y_zero - (b / 2)), text, font = indicator_font, fill = 0)
        temp_indicator = self.temp_steps
        while temp_indicator <= self.temp_max:
            y_position = y_zero - (temp_resolution * temp_indicator)
            text = str(temp_indicator) + u'\N{DEGREE SIGN}'
            l, t, r, b = draw.textbbox((0,0), text, indicator_font)
            draw.text((x_start - self.indicator_size - r, y_position - (b / 2) - 1), text, font = indicator_font, fill = 0)
            draw.line((x_start - self.indicator_size, y_position, x_start, y_position), fill = 0)
            temp_indicator = temp_indicator + self.temp_steps
        temp_indicator = -self.temp_steps
        while temp_indicator >= self.temp_min:
            y_position = y_zero - (temp_resolution * temp_indicator)
            text = str(temp_indicator) + u'\N{DEGREE SIGN}'
            l, t, r, b = draw.textbbox((0,0), text, indicator_font)
            draw.text((x_start - self.indicator_size - r, y_position - (b / 2 + 1)), text, font = indicator_font, fill = 0)
            draw.line((x_start - self.indicator_size, y_position, x_start, y_position), fill = 0)
            temp_indicator = temp_indicator - self.temp_steps
        if self.rain_module:
            rain_indicator = self.rain_steps
            while rain_indicator <= self.rain_max:
                y_position = y_zero - (rain_resolution * rain_indicator)
                if rain_indicator + self.rain_steps > self.rain_max:
                    text = str(rain_indicator) + 'mm'
                    l, t, r, b = draw.textbbox((0,0), text, indicator_font)
                    draw.text((x_start + self.indicator_size, y_position - (b / 2) - 1), text, font = indicator_font, fill = 0)
                draw.line((x_start, y_position, x_start + self.indicator_size, y_position), fill = 0)
                rain_indicator = rain_indicator + self.rain_steps

        # Draw x axis
        draw.line((x_start, y_zero, self.width - self.padding_horizontal, y_zero), fill = 0) # x axis

        for i in range(len(data)):
            dp = data[i]
            # Draw y axis at midnight
            if dp.is_midnight:
                draw.line((dp.x_position, self.padding_vertical, dp.x_position, self.height - self.padding_vertical - (self.day_height if self.show_days else 0)), fill = 0) # y axis
                temp_indicator = self.temp_steps
                while temp_indicator <= self.temp_max:
                    y_position = y_zero - (temp_resolution * temp_indicator)
                    draw.line((dp.x_position - self.indicator_size, y_position, dp.x_position, y_position), fill = 0)
                    temp_indicator = temp_indicator + self.temp_steps
                temp_indicator = -self.temp_steps
                while temp_indicator >= self.temp_min:
                    y_position = y_zero - (temp_resolution * temp_indicator)
                    draw.line((dp.x_position - self.indicator_size, y_position, dp.x_position, y_position), fill = 0)
                    temp_indicator = temp_indicator - self.temp_steps
                if self.rain_module:
                    rain_indicator = self.rain_steps
                    while rain_indicator <= self.rain_max:
                        y_position = y_zero - (rain_resolution * rain_indicator)
                        draw.line((dp.x_position, y_position, dp.x_position + self.indicator_size, y_position), fill = 0)
                        rain_indicator = rain_indicator + self.rain_steps
                        

            # Draw hour marker if needed
            if dp.show_tick:
                draw.line((dp.x_position, y_zero, dp.x_position, y_zero + self.indicator_size), fill = 0)

            # Draw temp value
            if dp.temp_value != None and i < len(data) - 1 and data[i + 1].temp_value != None:
                x1 = dp.x_position
                y1 = y_zero - max(min(dp.temp_value, self.temp_max), self.temp_min) * temp_resolution
                x2 = data[i + 1].x_position
                y2 = y_zero - max(min(data[i + 1].temp_value, self.temp_max), self.temp_min) * temp_resolution
                draw.line((x1, y1, x2, y2), fill = 0, width = self.line_width)

            # Draw current value dot if latest value
            if dp.is_latest and dp.temp_value:
                x1 = dp.x_position - self.current_value_radius
                y1 = y_zero - max(min(data[i].temp_value, self.temp_max), self.temp_min) * temp_resolution - self.current_value_radius
                x2 = dp.x_position + self.current_value_radius
                y2 = y_zero - max(min(data[i].temp_value, self.temp_max), self.temp_min) * temp_resolution + self.current_value_radius
                draw.ellipse((x1, y1, x2, y2), fill = 0)

            # Draw rain if needed
            if dp.rain_value and dp.rain_value > 0.0:
                x1 = max(dp.x_position - self.density, x_start)
                y1 = y_zero - (min(dp.rain_value, self.rain_max) * rain_resolution)
                x2 = min(dp.x_position + self.density, x_start + graph_width)
                y2 = y_zero
                draw.rectangle((x1, y1, x2, y2), fill = 0)

            # Draw day text if needed
            if dp.day_text and self.show_days:
                next_day = data[-1]
                for j in range(i + 1, len(data)):
                    if data[j].day_text:
                        next_day = data[j]
                        break
                available_space = next_day.x_position - dp.x_position
                short_text = dp.day_text 
                full_text = short_text
                value_text = ''
                if dp.day_values and len(dp.day_values) == 2:
                    value_text = '(' + config.format_decimal(dp.day_values[0]) + u'\N{DEGREE SIGN}' + '/' + config.format_decimal(dp.day_values[1]) + u'\N{DEGREE SIGN}' + ')'
                    full_text = full_text + ' ' + value_text
                
                length = draw.textlength(full_text, day_font)
                short_length = draw.textlength(short_text, day_font)
                l, t, r, b = draw.textbbox((0,0), full_text, day_font)
                if length <= available_space:
                    offset = math.floor((available_space - length) / 2)
                    y_position = self.height - self.padding_vertical - b
                    draw.text((dp.x_position + offset, y_position), full_text, font = day_font, fill = 0)
                elif short_length <= available_space:
                    offset = math.floor((available_space - short_length) / 2)
                    y_position = self.height - self.padding_vertical - b
                    draw.text((dp.x_position + offset, y_position), short_text, font = day_font, fill = 0)

        super().render()
        return self.image