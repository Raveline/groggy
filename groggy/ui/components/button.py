from groggy.events import bus
from groggy.ui.components.component import Component
from groggy.view.show_console import display_highlighted_text, display_text


class Button(Component):
    """
    A button that, if selectable and pressed, will trigger
    an event.
    """
    def __init__(self, x, y, w, text, events, events_types, selectable=True):
        super(Button, self).__init__(x, y, w, 1, selectable)
        self.text = text
        self.events = events
        self.events_types = events_types

    def display(self, console):
        func = display_text
        if self.focused:
            func = display_highlighted_text
        func(console, self.text, self.x, self.y)

    def enter(self):
        for idx, event in enumerate(self.events):
            event_type = self.events_types[idx]
            bus.bus.publish(event, event_type)
