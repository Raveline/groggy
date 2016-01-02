"""
A set of tools to handle the display of a viewport.
"""
from itertools import cycle, chain
from groggy.utils.geom import Frame
from groggy.inputs.input import Inputs
from groggy.events import bus


class Scape(object):
    """
    A simple abstraction of the movement of a frame in a given, wider,
    world_frame.
    It also handles picking a given element in the frame or a selection
    of element in the frame.
    """
    def __init__(self, w, h, world_frame):
        self.frame = Frame(0, 0, w, h)
        """The size of the scape."""
        self.world_frame = world_frame
        """The size of the world this scape displays a small part of."""
        self.block = False
        self.compute_focus()
        self.set_char()

    def set_char(self, character=None):
        """
        Set the main character to display if the focus of
        this scape has to be shown.
        """
        self.finish_select()
        if character is None:
            character = 'x'
        self.character = character
        self.block = False

    def set_multi_char(self, characters, width, height):
        """
        Set the characters to display in the focus if many characters
        need to be shown.
        """
        self.selection = Selection(self.getX(), self.getY(), self.getZ())
        self.selection.x2 = self.selection.x + width - 1
        self.selection.y2 = self.selection.y + height - 1
        self.character = list(chain(*characters))
        self.block = True

    def compute_focus(self):
        """
        Compute the center of the scape.
        """
        self.focusX = self.frame.w / 2
        self.focusY = self.frame.h / 2

    def receive(self, message):
        """
        Handle movements of the frame depending on input.
        """
        movy = 0
        movx = 0
        if message == Inputs.UP:
            movy = -1
        if message == Inputs.DOWN:
            movy = 1
        if message == Inputs.LEFT:
            movx = -1
        if message == Inputs.RIGHT:
            movx = 1
        # Handling selection
        if message == Inputs.ENTER:
            if self.selection:
                selection = self.selection
                self.finish_select()
                bus.bus.publish(selection, bus.AREA_SELECT)
            else:
                self.enter_select()
        if message == Inputs.ESCAPE:
            self.finish_select()
        if movx != 0 or movy != 0:
            self.change_frame(movx, movy)
            if self.selection:
                self.move_select()

    def change_frame(self, x, y):
        """
        If we moved, we must rebuild our frame.
        """
        self.frame.x += x
        self.frame.y += y
        self.frame.clip(self.world_frame)

    def change_focus(self, center):
        centerx = center.getX()
        centery = center.getY()
        minx = self.frame.x + self.focusX
        miny = self.frame.y + self.focusY
        maxx = minx
        maxy = miny
        if centerx < minx:
            self.frame.x -= (minx - centerx)
        if centery < miny:
            self.frame.y -= (miny - centery)
        if centerx > maxx:
            self.frame.x += (centerx - maxx)
        if centery > maxy:
            self.frame.y += (centery - maxy)
        self.frame.clip(self.world_frame)

    def enter_select(self):
        self.selection = Selection(self.getX(), self.getY(), self.getZ())

    def move_select(self):
        if self.block:
            self.selection.translate_to(self.getX(), self.getY())
        else:
            self.selection.extends_to(self.getX(), self.getY())

    def finish_select(self):
        self.selection = None

    def set_coords(self, selector):
        pass

    def to_local(self):
        return self.global_to_local(self.getX(), self.getY())

    def global_to_local(self, x, y):
        return x - self.scape.frame.x, y - self.scape.frame.y

    def get_characters(self):
        return cycle(self.character)


class Selection(object):
    """
    A representation of an area selected in the world.
    """
    def __init__(self, x, y, z):
        self.initial_x = x
        self.initial_y = y
        self.x = x
        self.y = y
        self.z = z
        self.x2 = x
        self.y2 = y

    def extends_to(self, x, y):
        if x < self.initial_x:
            self.x = x
            self.x2 = self.initial_x
        else:
            self.x = self.initial_x
            self.x2 = x
        if y < self.initial_y:
            self.y = y
            self.y2 = self.initial_y
        else:
            self.y = self.initial_y
            self.y2 = y

    def translate_to(self, x, y):
        w = self.x2 - self.x
        h = self.y2 - self.y
        self.x = x
        self.y = y
        self.x2 = x + w
        self.y2 = y + h

    def to_rect(self):
        return {'x': self.x,
                'y': self.y,
                'z': self.z,
                'x2': self.x2,
                'y2': self.y2}

    def to_list_of_tiles(self):
        return [(x, y, self.z) for y in range(self.y, self.y2 + 1)
                for x in range(self.x, self.x2 + 1)]

    def __str__(self):
        return 'Z: %d, x : %d, y : %d, x2 : %d, y2 : %d'\
            % (self.z, self.x, self.y, self.x2, self.y2)


class Crosshair(Scape):
    """
    A specific Scape that allows to move a crosshair in the world.
    """
    def __init__(self, w, h, world_frame):
        super(Crosshair, self).__init__(w, h, world_frame)
        # (int, int, int) for (x, y, z)
        self.crosshair = (0, 0, 0)
        self.scape = Scape(w, h, world_frame)
        self.world_frame = world_frame
        self.compute_maximum()
        self.selection = None

    def set_coords(self, selector):
        self.selection = None
        self.crosshair = (selector.getX(), selector.getY(), selector.getZ())

    def compute_maximum(self):
        self.maxX = self.world_frame.w - (self.scape.frame.w / 2)
        self.maxY = self.world_frame.h - (self.scape.frame.h / 2)

    def receive(self, message):
        super(Crosshair, self).receive(message)

    def getX(self):
        return self.crosshair[0]

    def getY(self):
        return self.crosshair[1]

    def getZ(self):
        return self.crosshair[2]

    def change_frame(self, x, y):
        self.crosshair = (self.getX() + x, self.getY() + y, self.getZ())
        self.scape.change_focus(self)

    def rect_to_local(self):
        return (self.selection.x - self.scape.frame.x,
                self.selection.y - self.scape.frame.y,
                self.selection.x2 - self.scape.frame.x,
                self.selection.y2 - self.scape.frame.y)

    def get_selected_tiles(self):
        if self.selection:
            return self.selection.to_list_of_tiles()
        else:
            return [(self.getX(), self.getY(), self.getZ())]


class Fillhair(Crosshair):
    """
    A specific Crosshair that allow to show a "filled" location
    in the world.
    """
    def __init__(self, w, h, world_frame, func_filler):
        super(Fillhair, self).__init__(w, h, world_frame)
        self.selection = []
        self.func_filler = func_filler

    def rect_to_local(self):
        return (self.selection.x - self.scape.frame.x,
                self.selection.y - self.scape.frame.y,
                self.selection.x2 - self.scape.frame.x,
                self.selection.y2 - self.scape.frame.y)

    def set_selected(self):
        self.selection = self.func_filler((self.getX(), self.getY(), self.getZ()))

    def enter_select(self):
        self.set_selected()

    def get_selected_tiles(self):
        if self.selection:
            return self.selection
        else:
            return super(Fillhair, self).get_selected_tiles()

    def move_select(self):
        pass

    def finish_select(self):
        self.selection = []
