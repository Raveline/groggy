from groggy.utils.geom import Frame
from groggy.inputs.input import Inputs
from groggy.events import bus
from itertools import cycle, chain


class Focus(object):
    """
    The abstract idea of something that is at the center of a Viewport.
    The focus also allow the player to know in what way he or she is
    interacting with the world.
    Note that Foci can be of various types, some being a single character,
    others being numerous, blinking characters (typically, when trying
    to designate an area on a map).
    """
    def __init__(self):
        self.block = False
        """Document this !"""
        self.set_char()

    def set_char(self, character=None):
        """
        Set the main character to display to let the player now
        what he or she is selecting.
        """
        self.finish_select()
        if character is None:
            character = 'X'
        self.character = character
        self.block = False

    def set_multi_char(self, characters, width, height):
        """
        Set the characters to display if there are numerous characters
        to be shown. (Only works with rectangular forms).
        """
        self.selection = Selection(self.getX(), self.getY(), self.getZ())
        self.selection.x2 = self.selection.x + width - 1
        self.selection.y2 = self.selection.y + height - 1
        self.character = list(chain(*characters))
        self.block = True

    def receive(self, message, viewport):
        """
        Handle movements of the frame depending on input.
        Also, handle selection (or leaving selection).
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
            viewport.center_move(self)
            if self.selection:
                self.move_select()

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

    def get_characters(self):
        return cycle(self.character)


class Selection(Frame):
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


class Crosshair(Focus):
    """
    A specific Scape that allows to move a crosshair in the world.
    """
    def __init__(self):
        super(Crosshair, self).__init__()
        # (int, int, int) for (x, y, z)
        self.crosshair = (0, 0, 0)
        self.selection = None

    def set_coords(self, selector):
        self.selection = None
        self.crosshair = (selector.getX(), selector.getY(), selector.getZ())

    def getX(self):
        return self.crosshair[0]

    def getY(self):
        return self.crosshair[1]

    def getZ(self):
        return self.crosshair[2]

    def change_frame(self, x, y):
        super(Crosshair, self).change_frame(x, y)
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
    def __init__(self, func_filler):
        super(Fillhair, self).__init__()
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
