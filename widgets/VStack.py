try:
    from typing import Self
    from typing import List
except ImportError:
    from typing_extensions import Self
from PIL import Image
from .View import View

class VStack(View):
    view: List[View]
    gap: int

    def __init__(self): 
        super().__init__()
        self.view = []
        self.gap = 0

    def addView(self, view: View) -> Self:
        self.view.append(view)
        return self
    
    def setGap(self, gap: int) -> Self:
        self.gap = gap
        return self
    
    def prepareChild(self) -> Self:
        defined_height = 0
        undefined_weight = 0
        for view in self.view:
            if (view.height > 0):
                defined_height += view.height
            else:
                undefined_weight += view.layoutWeight
        
        remaining_height = self.height - defined_height - (2 * self.padding_vertical) - ((len(self.view) - 1) * self.gap)
        height_per_view = 0
        if (undefined_weight > 0):
            height_per_view = int(remaining_height / undefined_weight)

        for view in self.view:
            if (view.height == 0):
                view.setHeight(height = height_per_view * view.layoutWeight)
            if (view.width == 0):
                view.setWidth(width = (self.width - 2 * self.padding_horizontal))
        
        return self
    
    def render(self) -> Image:
        self.prepareChild()

        self.image = Image.new('RGBA', (self.width, self.height), (255, 255, 255, 0))

        x = self.padding_horizontal
        y = self.padding_vertical

        for view in self.view:
            self.image.paste(view.render(), [x, y])
            y = y + view.height + self.gap
        
        super().render()
        return self.image

