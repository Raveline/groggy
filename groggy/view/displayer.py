'''
This module exposes a displayer class, tasked with transforming
the current model and state into a view.
The displayer should always be extended by client code.
'''


class Displayer(object):
    def __init__(self, model):
        self.model = model

    def call(self, blink, state, consoles):
        for console in consoles.values():
            console.blit_on(0)

    def clip_world(self, world, clip_box):
        clipped_y = world[clip_box.y:clip_box.y + clip_box.h]
        clipped = [t[clip_box.x:clip_box.x + clip_box.w] for t in clipped_y]
        return clipped
