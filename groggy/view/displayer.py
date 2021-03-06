'''
This module exposes a displayer class, tasked with transforming
the current model and state into a view.
The displayer should always be extended by client code.
'''

import libtcodpy as tcod


class Displayer(object):
    def __init__(self, model):
        self.model = model

    def display(self, blink, state, consoles):
        raise NotImplementedError('Display method must be implemented.')

    def call(self, blink, state, consoles):
        self.display(blink, state, consoles)
        for console in consoles.values():
            console.blit_on(0)
        tcod.console_flush()

    def clip_world(self, world, clip_box):
        clipped_y = world[clip_box.y:clip_box.y + clip_box.h]
        clipped = [t[clip_box.x:clip_box.x + clip_box.w] for t in clipped_y]
        return clipped
