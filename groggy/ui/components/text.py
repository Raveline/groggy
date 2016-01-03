import libtcodpy as tcod
from groggy.utils.dict_path import read_path_dict
from groggy.ui.components.component import Component
from groggy.view.show_console import display_text


class TextBloc(Component):
    """
    A never selectable rectangle of text, used to display long
    information to the player.
    """
    def __init__(self, x, y, w, text):
        super(TextBloc, self).__init__(x, y, w)
        self.text = text

    def display(self, console):
        tcod.console_print_rect(console, self.x, self.y, self.w, 0, self.text)


class StaticText(Component):
    """
    A never selectable simple line of text.
    Typically used as a lable for some information or other component.
    """
    def __init__(self, x, y, text):
        super(StaticText, self).__init__(x, y)
        self.text = text

    def display(self, console):
        display_text(console, self.text, self.x, self.y)


class DynamicText(Component):
    """
    A never selectable, changing according to model, line
    of text.
    """
    def __init__(self, x, y, centered, source):
        super(DynamicText, self).__init__(x, y)
        self.centered = centered
        self.source = source
        self.text = ''

    def set_data(self, data):
        self.data = data
        # We cast to string to be able to display objects
        self.text = str(read_path_dict(data, self.source))

    def display(self, console):
        display_text(console, self.text, self.x, self.y)
