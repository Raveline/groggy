from groggy.ui.components.component import Component
from groggy.view.show_console import display_highlighted_text, display_text


class CheckboxComponent(Component):
    def __init__(self, x, y, w, label, selectable=True, checked=False):
        super(CheckboxComponent, self).__init__(x, y, w, 1, selectable)
        self.checked = checked
        self.label = label

    def enter(self):
        self.checked = not self.checked

    def display(self, console):
        if self.checked:
            num = 225
        else:
            num = 224
        to_display = chr(num) + ' ' + self.label
        func = display_text
        if self.focused:
            func = display_highlighted_text

        func(console, to_display, self.x, self.y)
