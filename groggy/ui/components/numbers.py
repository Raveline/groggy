from __future__ import division
import math
import libtcodpy as tcod
from groggy.utils.dict_path import read_path_dict
from groggy.ui.components.component import Component, ComponentException
from groggy.view.show_console import (
    display_highlighted_text, display_text, print_char
)


class MinimumMaximum(Component):
    """Abstract class for component with a current / minimum / maximum
    data model.
    Components should be able to read in a data dictionary a structure
    containing "minimum", "maximum" and "current".
    """
    def set_data(self, data):
        pertinent = read_path_dict(data, self.source)
        if pertinent:
            self.minimum = pertinent.get('minimum')
            self.maximum = pertinent.get('maximum')
            self.value = pertinent.get('current')
            self.step = pertinent.get('step')
        else:
            raise ComponentException('Data %s has no source key : %s.'
                                     % (str(data), self.source))

    def left(self, unit=1):
        self.value -= self.step * unit
        if self.value < self.minimum:
            self.value = self.minimum
        self.publish_change(self.value)

    def right(self, unit=1):
        self.value += self.step * unit
        if self.value > self.maximum:
            self.value = self.maximum
        self.publish_change(self.value)


class NumberPicker(MinimumMaximum):
    def __init__(self, x, y, source, selectable=True):
        super(NumberPicker, self).__init__(x, y, 15, 1, selectable)
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
    def __init__(self, x, y, w, source, selectable=True):
        super(Ruler, self).__init__(x, y, w, 1, selectable)
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
