try:
    from typing import Self
except ImportError:
    from typing_extensions import Self
from PIL import Image
from .View import View
from .ConfigHelper import ConfigHelper
from datetime import datetime, timezone

class Screen(View):
    def __init__(self, width: int = None, height: int = None):
        super().__init__()
        config = ConfigHelper()
        self.setSize(width = width if width else config.image_width, height = height if height else config.image_height)
        self.image = Image.new('RGB', (self.width, self.height), (255, 255, 255))
        self.save_image = config.export_image
    
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