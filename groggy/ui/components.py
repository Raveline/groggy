from __future__ import division

import math
import libtcodpy as tcod
from groggy.inputs.input import Inputs
from groggy.utils import bus
from groggy.utils.dict_path import read_path_dict
from groggy.utils.tcod_wrapper import Console
from groggy.view.show_console import display_highlighted_text, display_text
from groggy.view.show_console import print_char


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

    def left(self):
        pass

    def right(self):
        pass

    def enter(self):
        pass

    def send_next(self):
        bus.bus.publish(ComponentEvent.NEXT, bus.MENU_EVENT)

    def send_previous(self):
        bus.bus.publish(ComponentEvent.PREVIOUS, bus.MENU_EVENT)

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


class ContainerComponent(Component):
    """An abstract class for containers that contain others."""
    def __init__(self, x, y, w=0, h=0, is_selectable=False, children=None):
        super(ContainerComponent, self).__init__(x, y, w, h, is_selectable)
        if children is None:
            children = []
        self.selected_index = 0
        self.set_children(children)

    def set_children(self, children):
        self.children = children
        self.selectable_children = [c for c in self.children
                                    if c.is_selectable]

    def get_selected(self):
        return self.selectable_children[self.selected_index]

    def receive(self, event_data):
        if event_data == ComponentEvent.NEXT:
            self.update_selected_index(1)
        elif event_data == ComponentEvent.PREVIOUS:
            self.update_selected_index(-1)
        else:
            self.get_selected().receive(event_data)
            # We then reset the data setter, so that every
            # component is updated.
            self.set_data(self.data)

    def update_selected_index(self, by):
        self.get_selected().leave_focus()
        self.selected_index += by
        if self.selected_index < 0:
            self.selected_index = 0
            self.leave_focus()
            self.send_previous()
        elif self.selected_index >= len(self.selectable_children):
            self.selected_index = len(self.selectable_children) - 1
            self.leave_focus()
            self.send_next()
        else:
            self.get_selected().enter_focus()

    def update(self, values):
        for child in self.children:
            child.update(values)

    def enter_focus(self):
        bus.bus.subscribe(self, bus.MENU_EVENT)

    def leave_focus(self):
        bus.bus.unsubscribe(self, bus.MENU_EVENT)


class RootComponent(ContainerComponent):
    """A component with an attached console."""
    def __init__(self, x, y, w, h, title, children):
        super(RootComponent, self).__init__(x, y, w, h, False, children)
        self.console = Console(x, y, w, h)
        self.title = title
        bus.bus.subscribe(self, bus.MENU_EVENT)

    def deactivate(self):
        bus.bus.unsubscribe(self, bus.MENU_EVENT)
        tcod.console_delete(self.console.console)

    def display(self, console):
        """
        Display a frame, a title and children components.
        Then blit on the console parameter.
        """
        tcod.console_clear(self.console.console)
        tcod.console_set_default_foreground(self.console.console,
                                            tcod.white)
        tcod.console_hline(self.console.console, 0, 0, self.console.w)
        tcod.console_hline(self.console.console, 0,
                           self.console.h - 1, self.console.w)
        tcod.console_vline(self.console.console, 0, 0, self.console.h)
        tcod.console_vline(self.console.console, self.console.w - 1,
                           0, self.console.h)
        tcod.console_print_ex(self.console.console, int(self.console.w / 2),
                              0, tcod.BKGND_SET, tcod.CENTER, self.title)
        for child in self.children:
            child.display(self.console.console)
        self.console.blit_on(console)

    def set_children(self, children):
        super(RootComponent, self).set_children(children)
        if len(self.selectable_children):
            self.selectable_children[0].enter_focus()

    def set_data(self, data):
        self.data = data
        for child in self.children:
            child.set_data(data)

    def update_selected_index(self, by):
        self.get_selected().leave_focus()
        self.selected_index += by
        if self.selected_index < 0:
            self.selected_index = len(self.selectable_children) - 1
        elif self.selected_index >= len(self.selectable_children):
            self.selected_index = 0
        self.get_selected().enter_focus()

    def __str__(self):
        return "RootComponent"


class TextBloc(Component):
    def __init__(self, x, y, w, text):
        super(TextBloc, self).__init__(x, y, w)
        self.text = text

    def display(self, console):
        tcod.console_print_rect(console, self.x, self.y, self.w, 0, self.text)


class StaticText(Component):
    def __init__(self, x, y, text):
        super(StaticText, self).__init__(x, y)
        self.text = text

    def display(self, console):
        display_text(console, self.text, self.x, self.y)


class DynamicText(Component):
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


class RowsComponent(ContainerComponent):
    def __init__(self, x, y, w=0, h=0, is_selectable=False, contents=None):
        super(RowsComponent).__init__(x, y, w, h, is_selectable)
        if contents is None:
            contents = []
        self.contents = contents
        self.compute_widths()
        self.buid_rows()

    def compute_widths(self):
        lens = [(len(col) for col in row) for row in self.contents]
        self.widths = [max(sizes) for sizes in lens]

    def build_rows(self):
        for idx, c in enumerate(self.contents):
            self.children.append(ColumnedLine(self.x, self.y + idx,
                                              self.is_selectable,
                                              self.widths, c))

    def display(self, console):
        for c in self.children:
            c.display(console)


class ColumnedLine(Component):
    def __init__(self, x, y, is_selectable=False, widths=None, contents=None):
        if widths is None:
            widths = []
        if contents is None:
            contents = []
        super(ColumnedLine, self).__init__(x, y, sum(widths), 1, is_selectable)

    def display(self, console):
        current_x = self.x
        func = display_text
        if self.focused:
            func = display_highlighted_text
        for idx, elem in enumerate(self.contents):
            func(console, elem, current_x, self.y)
            current_x += self.widths[idx]


class Button(Component):
    def __init__(self, x, y, w, text, events, events_types):
        super(Button, self).__init__(x, y, w, 1, True)
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


class Line(Component):
    def __init__(self, x, y, w):
        super(Line, self).__init__(x, y, w, 1)

    def display(self, console):
        tcod.console_hline(console, self.x, self.y, self.w)


class MinimumMaximum(Component):
    """Abstract class for component with a current / minimum / maximum
    data model."""
    def set_data(self, data):
        pertinent = read_path_dict(data, self.source)
        if pertinent:
            self.minimum = pertinent.get('minimum')
            self.maximum = pertinent.get('maximum')
            self.value = pertinent.get('current')
        else:
            raise ComponentException('Data %s has no source key : %s.'
                                     % (str(data), self.source))

    def publish_change(self):
        bus.bus.publish({'source': self.source,
                         'new_value': self.value},
                        bus.MENU_MODEL_EVENT)

    def left(self, unit=1):
        self.value -= unit
        if self.value < self.minimum:
            self.value = self.minimum
        self.publish_change()

    def right(self, unit=1):
        self.value += unit
        if self.value > self.maximum:
            self.value = self.maximum
        self.publish_change()


class NumberPicker(MinimumMaximum):
    def __init__(self, x, y, source):
        super(NumberPicker, self).__init__(x, y, 15, 1, True)
        self.source = source

    def display(self, console):
        size_min = len(str(self.minimum))
        current_x = self.x
        if self.focused:
            func = display_highlighted_text
        else:
            func = display_text
        func(console, str(self.minimum), current_x, self.y)
        current_x += (size_min + 2)

        print_char(console, tcod.CHAR_ARROW_W, current_x, self.y,
                   tcod.white)

        current_x += 2

        func(console, str(self.value), current_x, self.y)

        current_x += (len(str(self.value)) + 2)

        print_char(console, tcod.CHAR_ARROW_E, current_x, self.y,
                   tcod.white)

        current_x += 2

        func(console, str(self.maximum), current_x, self.y)


class Ruler(MinimumMaximum):
    def __init__(self, x, y, w, source):
        super(Ruler, self).__init__(x, y, w, 1, True)
        self.source = source
        self.value = 0

    def display(self, console):
        size_min = len(str(self.minimum))
        size_max = len(str(self.maximum))
        ruler_width = self.w - (size_min + size_max)
        max2 = ruler_width
        min2 = size_min
        dividor = (self.maximum - self.minimum)

        if dividor != 0 and self.value > 0:
            pos = (max2 - min2) / dividor * (self.value - self.maximum) + max2
            pos = int(math.floor(pos))
        else:
            pos = 1

        if self.focused:
            front_color = tcod.green
        else:
            front_color = tcod.white
        display_text(console, str(self.minimum), self.x, self.y)
        display_text(console, str(self.maximum), self.w - size_max, self.y)
        begin_ruler = self.x + size_min
        end_ruler = min(begin_ruler + pos, ruler_width)
        for x in range(begin_ruler, end_ruler):
            tcod.console_put_char_ex(console, x, self.y,
                                     tcod.CHAR_BLOCK1, front_color, tcod.black)
