try:
    from typing import Self
except ImportError:
    from typing_extensions import Self
from .View import View
from PIL import Image, ImageDraw, ImageFont
import enum
import os

class TextAlign(enum.Enum):
    LEFT = 1
    CENTER = 2
    RIGHT = 3
    
class TextWidget(View):
    text: list[str]
    text_align: TextAlign
    text_size: int
    
    def __init__(self, text: str, text_align: TextAlign = TextAlign.CENTER, text_size: int = None):
        super().__init__()
        self.setText(text = text)
        self.setTextAlign(text_align = text_align)
        self.setTextSize(size = text_size)
    
    def setText(self, text: str) -> Self:
        self.text = [text]
        return self
    
    def addTextLine(self, text: str) -> Self:
        self.text.append(text)
        return self
    
    def setTextAlign(self, text_align: TextAlign) -> Self:
        self.text_align = text_align
        return self

    def setTextSize(self, size: int) -> Self:
        self.text_size = size
        return self

    def render(self) -> Image:
        fontdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Font.ttc')
        self.image = Image.new('RGBA', (self.width, self.height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(self.image)

        if self.text_size == None:
            # find right text size horizontal
            sizes = []
            for line in self.text:
                size = 5
                while True:
                    font = ImageFont.truetype(fontdir, size)
                    length = draw.textlength(line, font)
                    size += 1
                    if length > (self.width - 2 * self.padding_horizontal):
                        break
                sizes.append(size - 1)

            # find right text size vertical
            size = 5
            while True:
                font = ImageFont.truetype(fontdir, size)
                height = 0
                for line in self.text:
                    l, t, r, b = draw.textbbox((0,0), line, font)
                    height += b
                size += 1
                if height > (self.height - 2 * self.padding_vertical):
                    break
            sizes.append(size - 1)

            self.text_size = min(sizes)

        # set font
        font = ImageFont.truetype(fontdir, self.text_size)

        # get vertical position
        height = 0
        for line in self.text:
            l, t, r, b = draw.textbbox((0,0), line, font)
            height += b
        top = self.padding_vertical + ((self.height - 2 * self.padding_vertical - height) / 2)

        # get horizontal position and draw
        for line in self.text:
            l, t, r, b = draw.textbbox((0, 0), line, font)
            left = 0
            if self.text_align == TextAlign.LEFT:
                left = self.padding_horizontal
            elif self.text_align == TextAlign.CENTER:
                left = self.padding_horizontal + ((self.width - 2 * self.padding_horizontal - r) / 2)
            elif self.text_align == TextAlign.RIGHT:
                left = self.padding_horizontal + (self.width - 2 * self.padding_horizontal - r)
            draw.text((left, top), line, font = font, fill = (0, 0, 0, 255))
            top += b

        super().render()
        return self.image