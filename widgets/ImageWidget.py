try:
    from typing import Self
except ImportError:
    from typing_extensions import Self
from .View import View
from PIL import Image, ImageDraw
import os
    
class ImageWidget(View):
    image: Image = None

    def __init__(self, image: Image = None):
        super().__init__()
        self.setImage(image = image)
    
    def setImage(self, image: Image) -> Self:
        self.image = image
        return self

    def render(self) -> Image:
        self.image = Image.new('RGBA', (self.width, self.height), (255, 255, 255, 0))

        super().render()
        return self.image