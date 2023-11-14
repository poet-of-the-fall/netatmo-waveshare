try:
    from typing import Self
except ImportError:
    from typing_extensions import Self
from .View import View
from .VStack import VStack
from .TextWidget import TextWidget
from PIL import Image, ImageDraw, ImageFont
import os
    
class ModuleWidget(View):
    header: str
    body: str
    footer: str
    ratio: float
    
    def __init__(self, header: str = "", body: str = "", footer: str = "", ratio: float = 0.2):
        super().__init__()
        self.setHeader(text = header)
        self.setBody(text = body)
        self.setFooter(text = footer)
        self.setRatio(ratio = ratio)
    
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

    def render(self) -> Image:
        header = TextWidget(self.header).setHeight(round((self.height - 2 * self.padding_vertical) * self.ratio))
        body = TextWidget(self.body)
        footer = TextWidget(self.footer).setHeight(round((self.height - 2 * self.padding_vertical) * self.ratio))

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