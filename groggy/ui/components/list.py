import libtcodpy as tcod

from groggy.utils.dict_path import read_path_dict
from groggy.ui.components.component import Component
from groggy.ui.components.container import ContainerComponent
from groggy.view.show_console import display_highlighted_text, display_text


class ListComponent(ContainerComponent):
    """
    A combo box of sort.
    Components should be able to read in a data dictionary a
    list of dicts containing "object" and "selected".
    """
    def __init__(self, x, y, w, h, source, selectable=True):
        self.source = source
        super(ListComponent, self).__init__(x, y, w, h, selectable, None)

    def set_data(self, data):
        items = read_path_dict(data, self.source)
        children = []
        for idx, elem in enumerate(items):
            children.append(
                ListItemComponent(self.x, self.y + idx, self.w, self.source,
                                  elem)
            )
        self.set_children(children)

    def set_children(self, children):
        super(ListComponent, self).set_children(children)
        if self.focused and len(self.selectable_children):
            self.selectable_children[0].enter_focus()

    def display(self, console):
        for child in self.children:
            child.display(console)


class ListItemComponent(Component):
    def __init__(self, x, y, w, source, item):
        super(ListItemComponent, self).__init__(x, y, w, 1, True)
        self.source = source
        self.item = item
        self.displayed_text = str(self.item['object'])
        self.selected = self.item['selected']

    def is_activated(self):
        return self.item['selected']

    def enter(self):
        self.item['selected'] = not self.is_activated()
        self.selected = not self.selected
        # No need to update here : we're directly manipulating the object

    def display(self, console):
        if self.is_activated():
            if self.focused:
                fb = tcod.green
                bg = tcod.yellow
            else:
                fb = tcod.black
                bg = tcod.green
            display_highlighted_text(console, self.displayed_text,
                                     self.x, self.y, bg, fb)
        else:
            func = display_text
            if self.focused:
                func = display_highlighted_text
            func(console, self.displayed_text, self.x, self.y)
