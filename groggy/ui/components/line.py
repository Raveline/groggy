import libtcodpy as tcod
from groggy.ui.components.component import Component


class Line(Component):
    """
    A simple horizontal line to separate areas.
    """
    def __init__(self, x, y, w):
        super(Line, self).__init__(x, y, w, 1)

    def display(self, console):
        tcod.console_hline(console, self.x, self.y, self.w)
