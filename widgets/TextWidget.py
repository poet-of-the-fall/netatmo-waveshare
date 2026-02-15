try:
    from typing import Self
except ImportError:
    from typing_extensions import Self
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
    FONT_SIZE_LIMIT = 500
    _font_sizes = []

    def __init__(self, text: str, text_align_horizontal: TextAlignHorizontal = TextAlignHorizontal.CENTER, text_align_vertical: TextAlignVertical = TextAlignVertical.CENTER, text_size: int = None, max_text_size: int = None):
        super().__init__()
        self.setText(text = text)
        self.setTextAlignHorizontal(text_align = text_align_horizontal)
        self.setTextAlignVertical(text_align = text_align_vertical)
        self.setTextSize(size = text_size)
        self.max_text_size = None
        if max_text_size:
            self.setMaxTextSize(size = max_text_size)
        if len(TextWidget._font_sizes) == 0:
            fontpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Font.ttc')
            TextWidget._font_sizes = [ImageFont.truetype(fontpath, x) if x > 0 else 0 for x in range(TextWidget.FONT_SIZE_LIMIT + 1)]
    
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
    
    def calculateTextSize(self, different_width: int = None, different_height: int = None) -> int:
        box_width = self.width
        box_height = self.height
        if different_width:
            box_width = different_width
        if different_height:
            box_height = different_height
        image = Image.new('RGBA', (box_width, box_height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)

        # find right text size horizontal
        sizes = []
        if self.max_text_size != None:
            sizes.append(self.max_text_size)

        for line in self.text:
            size = 5
            while True:
                if line == "":
                    size = TextWidget.FONT_SIZE_LIMIT
                    break
                font = TextWidget._font_sizes[size]
                length = draw.textlength(line, font)
                del font
                if length > (box_width - 2 * self.padding_horizontal):
                    break
                size += 1
                if size > TextWidget.FONT_SIZE_LIMIT:
                    break
            sizes.append(size - 1)

        # find right text size vertical
        size = 5
        while True:
            font = TextWidget._font_sizes[size]
            height = 0
            for line in self.text:
                l, t, r, b = draw.textbbox((0,0), line, font)
                height += b
            del font
            if height > (box_height - 2 * self.padding_vertical):
                break
            size += 1
            if size > TextWidget.FONT_SIZE_LIMIT:
                break
        sizes.append(size - 1)

        return min(sizes)

    def render(self) -> Image:
        self.image = Image.new('RGBA', (self.width, self.height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(self.image)

        if self.text_size == None:
            self.text_size = self.calculateTextSize()

        # set font
        font = TextWidget._font_sizes[self.text_size]

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

        del font
        super().render()
        return self.image