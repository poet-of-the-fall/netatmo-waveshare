try:
    from typing import Self
except ImportError:
    from typing_extensions import Self
from pathlib import Path
import configparser

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]
    
class ConfigHelper(metaclass=Singleton):
    decimal_marker: str
    log_level: str
    export_image: bool
    image_width: int
    image_height: int
    highlight_humidity_max: int
    highlight_co2_max: int
    highlight_battery_min: int
    highlight_calm_max: int
    highlight_wind_max: int

    def __init__(self):
        # Load the config.ini file
        path = Path.cwd()
        config = configparser.ConfigParser()
        config.read(path / 'config.ini')
        
        # Load values
        self.decimal_marker = config.get('general', 'decimal_marker', fallback=".")
        self.log_level = config.get('general','log_level', fallback="none")
        self.export_image = config.getboolean('general','export_image', fallback=False)
        self.image_width = config.getint('general', 'image_width', fallback=880)
        self.image_height = config.getint('general', 'image_height', fallback=528)
        self.highlight_humidity_max = config.getint('highlight', 'humidity_max', fallback=70)
        self.highlight_co2_max = config.getint('highlight', 'co2_max', fallback=2000)
        self.highlight_battery_min = config.getint('highlight', 'battery_min', fallback=25)
        self.highlight_calm_max = config.getint('highlight', 'calm_max', fallback=2)
        self.highlight_wind_max = config.getint('highlight', 'wind_max', fallback=50)

    def format_decimal(self, value) -> str:
        return str(round(float(value), 1)).replace(".", self.decimal_marker)
