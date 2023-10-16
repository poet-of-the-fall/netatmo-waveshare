try:
    from typing import Self
except ImportError:
    from typing_extensions import Self
from .View import View
from PIL import Image, ImageDraw

class TextWidget(View):
    text: str
    
    def __init__(self, text: str) -> Self:
        super().__init__()
        self.setText(text = text)
        return self
    
    def setText(self, text: str) -> Self:
        self.text = text
        return self

    def render(self) -> Image:
        self.image = Image.new('RGBA', (self.width, self.height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(self.image)
        draw.text(text = self.text)
        super().render()
        return self.image