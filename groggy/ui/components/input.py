from groggy.utils.dict_path import read_path_dict
from groggy.ui.components.component import Component
from groggy.view.show_console import display_text, display_highlighted_text


class TextInput(Component):
    """
    A never selectable rectangle of text, used to display long
    information to the player.
    """
    def __init__(self, x, y, w, text='', source=None, selectable=True):
        super(TextInput, self).__init__(x, y, w, 1, selectable)
        self.text = text
        self.source = source

    def set_data(self, data):
        if self.source:
            self.text = str(read_path_dict(data, self.source))

    def letter(self, c):
        self.text = self.text + c
        self.publish_change(self.text)

    def backspace(self):
        self.text = self.text[:-1]
        self.publish_change(self.text)

    def display(self, console):
        func = display_text
        to_display = self.text
        if self.focused:
            func = display_highlighted_text
            # If text is empty, we'll replace by a highlited blank space
            # so focus is visible
            if not self.text:
                to_display = ' '
        func(console, to_display, self.x, self.y)
