"""
A set of tools to handle the display of a viewport.
"""
from groggy.utils.geom import Frame


class Viewport(object):
    """
    The main object behind any kind of scrolling; "scrolling" is just
    displaying a viewport of a wider picture, and moving this viewport
    when needed.
    """
    def __init__(self, w, h, world_frame):
        self.frame = Frame(0, 0, w, h)
        """The size of this viewport."""
        self.world_frame = world_frame
        """The frame on which we will display a small port here."""
        self.centerX, self.centerY = self.get_center()

    def getX(self):
        return self.frame.x

    def getY(self):
        return self.frame.y

    def get_center(self):
        """
        Return the center coord of the frame.
        """
        return (self.frame.w // 2, self.frame.h // 2)

    def move_frame(self, x, y):
        """
        Direct way of moving the frame.
        It basically chances its x and y position, whilst ensuring it stays
        in the bound of the wider, world_frame.
        """
        self.frame.x += x
        self.frame.y += y
        self.frame.clip(self.world_frame)

    def center_move(self, focus):
        """
        Indirect way of moving the frame, from a focused object.
        A focused object should cause a frame movement if it leaves
        an area at the center of the screen.
        By default (this is the behaviour implemented here), this area
        is simple a tiny pixel at the center of the screen.
        """
        centerx = focus.getX()
        centery = focus.getY()
        # Below these X and Y, move to the left and to the top
        minx = self.frame.x + self.centerX
        miny = self.frame.y + self.centerY
        # Above these X and Y, move to the right and to the bottom
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

    def to_local(self):
        """
        ???
        """
        return self.global_to_local(self.getX(), self.getY())

    def global_to_local(self, x, y):
        """
        Given a x and y on the world frame, give their coordinates
        in the viewport frame.
        """
        return x - self.frame.x, y - self.frame.y
