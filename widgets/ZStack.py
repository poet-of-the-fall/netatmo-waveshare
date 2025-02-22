try:
    from typing import Self
    from typing import List
except ImportError:
    from typing_extensions import Self
from PIL import Image
from .View import View

class ZStack(View):
    view: List[View]

    def __init__(self):
        super().__init__()
        self.view = []

    def addView(self, view: View) -> Self:
        self.view.append(view)
        return self
    
    def prepareChild(self) -> Self:
        for view in self.view:
            if (view.width == 0):
                view.setWidth(width = (self.width - 2 * self.padding_horizontal))
            if (view.height == 0):
                view.setHeight(height = (self.height - 2 * self.padding_vertical))

        return self
    
    def render(self) -> Image:
        self.prepareChild()
        
        self.image = Image.new('RGBA', (self.width, self.height), (255, 255, 255, 0))
        
        x = self.padding_horizontal
        y = self.padding_vertical

        for view in self.view:
            img = view.render()
            self.image.paste(img, [x, y], img)
        
        super().render()
        return self.image

