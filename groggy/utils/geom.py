def manhattan(x, y, x2, y2):
    return abs((x2 - x) + (y2 - y))


class Frame(object):
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def contains(self, x, y):
        return x >= self.x and x <= self.x + self.w\
            and y >= self.y and y <= self.y + self.h

    def clip(self, other_frame):
        """Fit this frame in another, bigger one, making sure it doesn't
        "spill out".
        >>> f = Frame(0,0,20,20)
        >>> f2 = Frame(0,0,40,40)
        >>> f.clip(f2)
        >>> f.x
        0
        >>> f.y
        0
        >>> f.x = 25
        >>> f.y = 38
        >>> f.clip(f2)
        >>> f.x
        20
        >>> f.y
        20
        """
        max_x = other_frame.w - self.w
        max_y = other_frame.h - self.h
        if (self.x > max_x):
            self.x = max_x
        if (self.y > max_y):
            self.y = max_y
        if (self.x < other_frame.x):
            self.x = 0
        if (self.y < other_frame.y):
            self.y = 0
