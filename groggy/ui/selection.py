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
    to designate an selected_area on a map).
    This class should be extended to fit your need, or you can use some
    of the extension given in this module, like Crosshair or Filler.
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
        self.selected_area = Selection(self.getX(), self.getY(), self.getZ())
        self.selected_area.x2 = self.selected_area.x + width - 1
        self.selected_area.y2 = self.selected_area.y + height - 1
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
            if self.selected_area:
                selected_area = self.selected_area
                self.finish_select()
                bus.bus.publish(selected_area, bus.AREA_SELECT)
            else:
                self.enter_select()
        if message == Inputs.ESCAPE:
            self.finish_select()
        if movx != 0 or movy != 0:
            self.move(movx, movy)
            self.clip_move(viewport.world_frame)
            if self.selected_area:
                self.move_select()
            viewport.center_move(self)

    def move(self, dx, dy):
        pass

    def clip_move(self, frame):
        """
        Make sure the selection do not go out of the frame.
        """
        raise NotImplementedError

    def enter_select(self):
        self.selected_area = Selection(self.getX(), self.getY(), self.getZ())

    def move_select(self):
        if self.block:
            self.selected_area.translate_to(self.getX(), self.getY())
        else:
            self.selected_area.extends_to(self.getX(), self.getY())

    def finish_select(self):
        self.selected_area = None

    def set_coords(self, selector):
        pass

    def get_characters(self):
        return cycle(self.character)


class Selection(Frame):
    """
    A representation of an selected_area selected in the world.
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
        self.selected_area = None

    def set_coords(self, selector):
        self.selected_area = None
        self.crosshair = (selector.getX(), selector.getY(), selector.getZ())

    def getX(self):
        return self.crosshair[0]

    def getY(self):
        return self.crosshair[1]

    def getZ(self):
        return self.crosshair[2]

    def move(self, dx, dy):
        self.crosshair = (self.getX() + dx, self.getY() + dy, self.getZ())

    def clip_move(self, frame):
        newx = self.crosshair[0]
        newy = self.crosshair[1]
        if self.getX() < 0:
            newx = 0
        elif self.getX() > frame.w - 1:
            newx = frame.w - 1
        if self.getY() < 0:
            newy = 0
        elif self.getY() > frame.h - 1:
            newy = frame.w - 1
        self.crosshair = (newx, newy, self.getZ())

    def rect_to_local(self):
        return (self.selected_area.x - self.scape.frame.x,
                self.selected_area.y - self.scape.frame.y,
                self.selected_area.x2 - self.scape.frame.x,
                self.selected_area.y2 - self.scape.frame.y)

    def get_selected_tiles(self):
        if self.selected_area:
            return self.selected_area.to_list_of_tiles()
        else:
            return [(self.getX(), self.getY(), self.getZ())]


class Fillhair(Crosshair):
    """
    A specific Crosshair that allow to show a "filled" location
    in the world.
    """
    def __init__(self, func_filler):
        super(Fillhair, self).__init__()
        self.selected_area = []
        self.func_filler = func_filler

    def rect_to_local(self):
        return (self.selected_area.x - self.scape.frame.x,
                self.selected_area.y - self.scape.frame.y,
                self.selected_area.x2 - self.scape.frame.x,
                self.selected_area.y2 - self.scape.frame.y)

    def set_selected(self):
        self.selected_area = self.func_filler(
            (self.getX(), self.getY(), self.getZ())
        )

    def enter_select(self):
        self.set_selected()

    def get_selected_tiles(self):
        if self.selected_area:
            return self.selected_area
        else:
            return super(Fillhair, self).get_selected_tiles()

    def move_select(self):
        pass

    def finish_select(self):
        self.selected_area = []
