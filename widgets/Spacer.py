try:
    from typing import Self
except ImportError:
    from typing_extensions import Self
from .View import View
from PIL import Image

class Spacer(View):
    def render(self) -> Image:
        self.image = Image.new('RGBA', (self.width, self.height), (255, 255, 255, 0))
        super().render()
        return self.image