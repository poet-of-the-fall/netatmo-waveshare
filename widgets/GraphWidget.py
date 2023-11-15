try:
    from typing import Self
except ImportError:
    from typing_extensions import Self
from .View import View
from .TextWidget import TextWidget, TextAlignVertical
from PIL import Image, ImageDraw, ImageFont
import os
    
class GraphWidget(View):
    
    def __init__(self):
        super().__init__()

    def render(self) -> Image:
        self.image = Image.new('RGBA', (self.width, self.height), (255, 255, 255, 0))

        super().render()
        return self.image