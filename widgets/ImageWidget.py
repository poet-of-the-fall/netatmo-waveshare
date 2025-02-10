try:
    from typing import Self
except ImportError:
    from typing_extensions import Self
from .View import View
from .ConfigHelper import ConfigHelper
from PIL import Image
from pathlib import Path
    
class ImageWidget(View):
    image: Image = None
    rotation: float = 0.0

    def __init__(self, image: Image = None, rotation: float = 0.0):
        super().__init__()
        self.setImage(image = image)
        self.setRotation(rotation)
    
    def setImage(self, image: Image) -> Self:
        self.image = image
        return self
    
    def setRotation(self, rotation: float) -> Self:
        self.rotation = rotation
        return self

    def render(self) -> Image:
        resized_image = Image.new("RGBA", self.image.size, (255, 255, 255))
        resized_image.paste(self.image, mask=self.image)
        resized_image.thumbnail((self.width - 2 * self.padding_horizontal, self.height - 2 * self.padding_vertical))

        bbox = resized_image.getbbox()
        left = round((self.width - bbox[2]) / 2)
        upper = round((self.height - bbox[3]) / 2)
        rearranged_image = Image.new("RGBA", (self.width, self.height), (255, 255, 255))
        rearranged_image.paste(resized_image.rotate(self.rotation, fillcolor=(255, 255, 255)), (left, upper, left + bbox[2], upper + bbox[3]))

        super().render()
        return rearranged_image
    
class WindDirectionImage(ImageWidget):
    def __init__(self, module):
        config = ConfigHelper()
        path = Path.cwd()
        rotation = 360 - module['dashboard_data']['WindAngle'] if module['dashboard_data']['WindAngle'] else 0
        strength = module['dashboard_data']['WindStrength'] if module['dashboard_data']['WindStrength'] else 1
        icon_name = 'wind_direction_calm.png'
        if strength >= config.highlight_breeze_max:
            icon_name = 'wind_direction_gale.png'
        elif strength >= config.highlight_calm_max:
            icon_name = 'wind_direction_breeze.png'
        image = Image.open(path / 'images' / icon_name)
        super().__init__(image, rotation)