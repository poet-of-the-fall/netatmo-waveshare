try:
    from typing import Self
except ImportError:
    from typing_extensions import Self
from PIL import Image, ImageOps, ImageDraw

class View(object):
    width: int
    height: int
    layoutWeight: int
    image: Image
    view: Self
    padding_vertical: int
    padding_horizontal: int
    inverted: bool
    show_frame: bool

    def __init__(self):
        self.width = 0
        self.height = 0
        self.padding_horizontal = 0
        self.padding_vertical = 0
        self.inverted = False
        self.layoutWeight = 1
        self.show_frame = False

    def render(self) -> Image:
        if self.show_frame:
            draw = ImageDraw.Draw(self.image)
            draw.rectangle([(self.padding_horizontal, self.padding_vertical), (self.width - self.padding_horizontal - 1, self.height - self.padding_vertical - 1)], outline = "black", width = 1)
        if self.inverted:
            self.image = ImageOps.invert(self.image.convert('RGB')).convert('RGBA')
    
    def setSize(self, width: int, height: int) -> Self:
        self.setWidth(width = width).setHeight(height = height)
        return self

    def setHeight(self, height: int) -> Self:
        self.height = height
        return self
    
    def setWidth(self, width: int) -> Self:
        self.width = width
        return self
    
    def setPadding(self, vertical: int, horizontal: int) -> Self:
        self.padding_horizontal = horizontal
        self.padding_vertical = vertical
        return self
    
    def setLayoutWeight(self, weight: int) -> Self:
        self.layoutWeight = weight
        return self
    
    def setShowFrame(self, show_frame: bool) -> Self:
        self.show_frame = show_frame
        return self

    def invert(self) -> Self:
        self.inverted = not self.inverted
        return self