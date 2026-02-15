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
    # Load the config.ini file
    path = Path.cwd()
    config = configparser.ConfigParser()
    config.read(path / 'config.ini')

    # Load values
    decimal_marker: str = config.get('general', 'decimal_marker', fallback=",")
    log_level: str = config.get('general','log_level', fallback="none")
    refresh_interval_s: int = config.getint('general','refresh_interval_s', fallback=600)
    export_image: bool = config.getboolean('general','export_image', fallback=False)
    image_width: int = config.getint('general', 'image_width', fallback=880)
    image_height: int = config.getint('general', 'image_height', fallback=528)
    highlight_humidity_max: int = config.getint('highlight', 'humidity_max', fallback=60)
    highlight_co2_max: int = config.getint('highlight', 'co2_max', fallback=2000)
    highlight_battery_min: int = config.getint('highlight', 'battery_min', fallback=15)
    highlight_calm_max: int = config.getint('highlight', 'calm_max', fallback=2)
    highlight_wind_max: int = config.getint('highlight', 'wind_max', fallback=50)

    def format_decimal(self, value) -> str:
        return str(round(float(value), 1)).replace(".", self.decimal_marker)
