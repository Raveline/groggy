import libtcodpy as tcod
from groggy.utils.dict_path import read_path_dict
from groggy.ui.components.component import Component
from groggy.ui.components.container import ContainerComponent
from groggy.view.show_console import display_highlighted_text, display_text


class ListComponent(ContainerComponent):
    """
    A combo box of sort.
    """
    def __init__(self, x, y, w, h, source, selectable=True):
        self.source = source
        super(ListComponent, self).__init__(x, y, w, h, selectable, None)

    def set_data(self, data):
        items = read_path_dict(data, self.source)
        self.children = []
        for idx, elem in enumerate(items):
            self.children.append(
                ListItemComponent(self.x, self.y + idx, self.w, elem)
            )

    def display(self, console):
        for child in self.children:
            child.display(console)


class ListItemComponent(Component):
    def __init__(self, x, y, w, item):
        super(ListItemComponent, self).__init__(x, y, w, 1)
        self.item = item
        self.activated = False

    def enter(self):
        self.activated = not self.activated

    def display(self, console):
        if self.activated:
            display_highlighted_text(console, str(self.item), self.x, self.y,
                                     tcod.green, tcod.white)
        else:
            func = display_text
            if self.focused:
                func = display_highlighted_text
            func(console, str(self.item), self.x, self.y)
