try:
    from typing import Self
except ImportError:
    from typing_extensions import Self
from .View import View
from .VStack import VStack
from .HStack import HStack
from .TextWidget import TextWidget, TextAlignVertical
from PIL import Image, ImageDraw, ImageFont
import os
    
class ModuleWidget(View):
    header: str
    body: str
    footer: str
    ratio: float
    unit: str = None
    unit_ratio: float
    
    def __init__(self, header: str = "", body: str = "", footer: str = "", ratio: float = 0.2, unit: str = None, unit_ratio: float = 0.2):
        super().__init__()
        self.setHeader(text = header)
        self.setBody(text = body)
        self.setFooter(text = footer)
        self.setRatio(ratio = ratio)
        if unit:
            self.setUnit(text = unit)
        self.setUnitRatio(ratio = unit_ratio)
    
    def setHeader(self, text: str) -> Self:
        self.header = text
        return self
    
    def setBody(self, text: str) -> Self:
        self.body = text
        return self
    
    def setFooter(self, text: str) -> Self:
        self.footer = text
        return self
    
    def setRatio(self, ratio: float) -> Self:
        if ratio > 0.4 and ratio <= 0.95:
            ratio = (1 - ratio) / 2
        if ratio > 0.9 or ratio < 0.05:
            ratio = 0.2
        self.ratio = ratio
        return self
    
    def setUnit(self, text: str) -> Self:
        self.unit = text
        return self
    
    def setUnitRatio(self, ratio: float) -> Self:
        if ratio > 0.4 and ratio <= 0.95:
            ratio = (1 - ratio) / 2
        if ratio > 0.9 or ratio < 0.05:
            ratio = 0.2
        self.unit_ratio = ratio
        return self

    def render(self) -> Image:
        header = TextWidget(self.header).setHeight(round((self.height - 2 * self.padding_vertical) * self.ratio))
        footer = TextWidget(self.footer).setHeight(round((self.height - 2 * self.padding_vertical) * self.ratio))
        body_value = TextWidget(self.body)
        body = HStack().addView(body_value).setWidth(self.width - 2 * self.padding_horizontal).setHeight(round((self.height - 2 * self.padding_vertical) * ( 1 - 2 * self.ratio)))

        if self.unit:
            fontdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Font.ttc')
            image = Image.new('RGBA', (self.width, self.height), (255, 255, 255, 0))
            draw = ImageDraw.Draw(image)
            width = 0

            body.prepareChild()
            text_size = body_value.calculateTextSize()
            font = ImageFont.truetype(fontdir, text_size)
            l, t, r, b = draw.textbbox((0,0), self.body, font)
            unit_width = round((self.width - 2 * self.padding_horizontal) * self.unit_ratio)
            width = r + unit_width
            body_unit = TextWidget(self.unit).setPadding(vertical = self.height * (1 - self.ratio) * 0.1, horizontal = 0).setTextAlignVertical(TextAlignVertical.BOTTOM).setWidth(unit_width)
            
            body.addView(body_unit)
            body_value.setWidth(0)
            body_value.setHeight(0)

            body.setPadding(vertical = 0, horizontal = round((self.width - 2 * self.padding_horizontal - width) / 2))

        body.prepareChild()
        module = VStack().setPadding(vertical = self.padding_vertical, horizontal = self.padding_horizontal)
        module.setHeight(self.height).setWidth(self.width).addView(header).addView(body).addView(footer).prepareChild()

        sizes = []
        sizes.append(header.calculateTextSize())
        sizes.append(footer.calculateTextSize())
        header.setTextSize(min(sizes))
        footer.setTextSize(min(sizes))

        self.image = module.render()
        draw = ImageDraw.Draw(self.image)

        upper = header.height + self.padding_vertical
        lower = self.height - footer.height - self.padding_vertical
        draw.line((self.padding_horizontal, upper, self.width - 2 * self.padding_horizontal, upper), fill = (0, 0, 0, 255))
        draw.line((self.padding_horizontal, lower, self.width - 2 * self.padding_horizontal, lower), fill = (0, 0, 0, 255))

        super().render()
        return self.image