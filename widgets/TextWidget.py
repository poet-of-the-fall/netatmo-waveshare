try:
    from typing import Self, List
except ImportError:
    from typing_extensions import Self, List
from .View import View
from PIL import Image, ImageDraw, ImageFont
import enum
import os

class TextAlignHorizontal(enum.Enum):
    LEFT = 1
    CENTER = 2
    RIGHT = 3

class TextAlignVertical(enum.Enum):
    TOP = 1
    CENTER = 2
    BOTTOM = 3
    
class TextWidget(View):
    text: List[str]
    text_align_horizontal: TextAlignHorizontal
    text_align_vertical: TextAlignVertical
    text_size: int
    max_text_size: int = None
    
    def __init__(self, text: str, text_align_horizontal: TextAlignHorizontal = TextAlignHorizontal.CENTER, text_align_vertical: TextAlignVertical = TextAlignVertical.CENTER, text_size: int = None, max_text_size: int = None):
        super().__init__()
        self.setText(text = text)
        self.setTextAlignHorizontal(text_align = text_align_horizontal)
        self.setTextAlignVertical(text_align = text_align_vertical)
        self.setTextSize(size = text_size)
        if max_text_size:
            self.setMaxTextSize(size = max_text_size)
    
    def setText(self, text: str) -> Self:
        self.text = [text]
        return self
    
    def addTextLine(self, text: str) -> Self:
        self.text.append(text)
        return self
    
    def setTextAlignHorizontal(self, text_align: TextAlignHorizontal) -> Self:
        self.text_align_horizontal = text_align
        return self
    
    def setTextAlignVertical(self, text_align: TextAlignVertical) -> Self:
        self.text_align_vertical = text_align
        return self

    def setTextSize(self, size: int) -> Self:
        self.text_size = size
        return self
    
    def setMaxTextSize(self, size: int) -> Self:
        self.max_text_size = size
        return self
    
    def calculateTextSize(self) -> int:
        fontdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Font.ttc')
        image = Image.new('RGBA', (self.width, self.height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)

        # find right text size horizontal
        sizes = []
        if self.max_text_size != None:
            sizes.append(self.max_text_size)

        for line in self.text:
            size = 5
            while True:
                font = ImageFont.truetype(fontdir, size)
                length = draw.textlength(line, font)
                if length > (self.width - 2 * self.padding_horizontal):
                    break
                size += 1
            sizes.append(size - 1)

        # find right text size vertical
        size = 5
        while True:
            font = ImageFont.truetype(fontdir, size)
            height = 0
            for line in self.text:
                l, t, r, b = draw.textbbox((0,0), line, font)
                height += b
            if height > (self.height - 2 * self.padding_vertical):
                break
            size += 1
        sizes.append(size - 1)

        return min(sizes)

    def render(self) -> Image:
        fontdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Font.ttc')
        self.image = Image.new('RGBA', (self.width, self.height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(self.image)

        if self.text_size == None:
            self.text_size = self.calculateTextSize()

        # set font
        font = ImageFont.truetype(fontdir, self.text_size)

        # get vertical position
        height = 0
        for line in self.text:
            l, t, r, b = draw.textbbox((0,0), line, font)
            height += b
        top = 0
        if self.text_align_vertical == TextAlignVertical.TOP:
            top = self.padding_vertical
        elif self.text_align_vertical == TextAlignVertical.CENTER:
            top = self.padding_vertical + ((self.height - 2 * self.padding_vertical - height) / 2)
        elif self.text_align_vertical == TextAlignVertical.BOTTOM:
            top = self.padding_vertical + (self.height - 2 * self.padding_vertical - height)

        # get horizontal position and draw
        for line in self.text:
            l, t, r, b = draw.textbbox((0, 0), line, font)
            left = 0
            if self.text_align_horizontal == TextAlignHorizontal.LEFT:
                left = self.padding_horizontal
            elif self.text_align_horizontal == TextAlignHorizontal.CENTER:
                left = self.padding_horizontal + ((self.width - 2 * self.padding_horizontal - r) / 2)
            elif self.text_align_horizontal == TextAlignHorizontal.RIGHT:
                left = self.padding_horizontal + (self.width - 2 * self.padding_horizontal - r)
            draw.text((left, top), line, font = font, fill = (0, 0, 0, 255))
            top += b

        super().render()
        return self.image