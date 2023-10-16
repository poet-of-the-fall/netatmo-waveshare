try:
    from typing import Self
except ImportError:
    from typing_extensions import Self
from PIL import Image
from .View import View
from datetime import datetime, timezone

class Screen(View):
    save_image: bool

    def __init__(self, width: int, height: int, save_image: bool = False):
        super().__init__()
        self.setSize(width = width, height = height)
        self.image = Image.new('RGB', (self.width, self.height), (255, 255, 255))
        self.save_image = save_image
    
    def setView(self, view: View) -> Self:
        self.view = view
        return self

    def render(self) -> Image:
        self.view.setSize(width = (self.width - 2 * self.padding_horizontal), height = (self.height - 2 * self.padding_vertical))
        self.image.paste(self.view.render(), [self.padding_horizontal, self.padding_vertical])
        
        super().render()

        if self.save_image:
            self.image.save(str(datetime.now(timezone.utc).timestamp()) + ".png")

        return self.image