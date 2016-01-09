from groggy.inputs.input import Inputs
from groggy.events import bus


class ComponentException(Exception):
    pass


class ComponentEvent(object):
    PREVIOUS = 'previous'
    NEXT = 'next'


class Component(object):
    """
    An abstract class for ui & menu components
    """
    def __init__(self, x, y, w=0, h=0, is_selectable=False):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.is_selectable = is_selectable
        self.focused = False

    def set_data(self, data):
        pass

    def receive(self, event_data):
        if event_data == Inputs.UP:
            self.update_selected_index(-1)
        elif event_data == Inputs.DOWN:
            self.update_selected_index(1)
        elif event_data == Inputs.LEFT:
            self.left()
        elif event_data == Inputs.RIGHT:
            self.right()
        elif event_data == Inputs.ENTER:
            self.enter()
        elif event_data == Inputs.BACKSPACE:
            self.backspace()
        elif event_data == Inputs.SPACE:
            self.letter(' ')
        elif ord(event_data) >= 63 and ord(event_data) <= 122:
            self.letter(event_data)

    def left(self):
        pass

    def right(self):
        pass

    def enter(self):
        pass

    def backspace(self):
        pass

    def letter(self, c):
        pass

    def send_next(self):
        bus.bus.publish(ComponentEvent.NEXT, bus.MENU_ACTION)

    def send_previous(self):
        bus.bus.publish(ComponentEvent.PREVIOUS, bus.MENU_ACTION)

    def update_selected_index(self, by):
        self.leave_focus()
        if by > 0:
            self.send_next()
        else:
            self.send_previous()

    def enter_focus(self):
        """Receiving focus."""
        self.focused = True

    def leave_focus(self):
        """Losing focus."""
        self.focused = False
