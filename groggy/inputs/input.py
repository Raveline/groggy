'''
This module exposes an input reader.
It uses its own special touches as constants, but the rest is coupled with
libtcodpy.

The use is pretty straightforward:
- Build the Input giving it the event bus.
- Call "poll" whenever you need the input polled.
- The event bus will propagate the event to the current input listener.
'''
import libtcodpy as tcod
import groggy.events.bus as bus_events


class Inputs(object):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4
    ENTER = 5
    ESCAPE = 6
    SPACE = 7
    F1 = 56
    F2 = 57
    F3 = 58
    F4 = 59
    F5 = 60
    F6 = 61
    F7 = 62
    F8 = 63
    F9 = 64
    F10 = 65
    F11 = 66
    F12 = 67
    END = 100
    BACKSPACE = 99

    def __init__(self, bus):
        '''
        Building the input reader simply requires to give the event bus
        so we can write inside.
        '''
        self.mouse = tcod.Mouse()
        self.mouse_x = None
        self.mouse_y = None
        self.mouse_moved = False
        self.lclick = False
        self.rclick = False
        self.key = tcod.Key()
        self.quit = False
        self.bus = bus

    def poll(self):
        '''
        Check key and mouse input.
        '''
        tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS | tcod.EVENT_MOUSE,
                                 self.key, self.mouse)
        self.poll_keys()
        self.poll_mouse()

    def poll_keys(self):
        '''
        Detected any kind of keys.
        Send a quit signal if escape is pressed. TODO: change this.
        Send a signal corresponding to the constants if it is a special key.
        Send the char itself if it is a letter (uppercase or not).
        '''
        input_value = keys.get(self.key.vk)
        if input_value:
            if input_value == Inputs.END:
                self.bus.publish('quit', bus_events.LEAVE_EVENT)
            elif input_value == Inputs.ESCAPE:
                self.bus.publish(None, bus_events.LEAVE_EVENT)
            elif input_value:
                self.bus.publish(input_value, bus_events.INPUT_EVENT)
        else:
            if self.key.c >= 63 and self.key.c <= 122:
                self.bus.publish(chr(self.key.c), bus_events.INPUT_EVENT)

    def poll_mouse(self):
        '''
        Currently not implemented.
        '''
        self.mouse_moved = False
        if self.mouse.x != self.mouse_x:
            self.mouse_x = self.mouse.x
            self.mouse_moved = True
        if self.mouse.y != self.mouse_y:
            self.mouse_y = self.mouse.y
            self.mouse_moved = True
        if self.mouse.lbutton and not self.lclick:
            self.lclick = True
            print('Left clik !')
        elif not self.mouse.lbutton and self.lclick:
            self.lclick = False
            print('No left click anymoare')
        if self.mouse.rbutton_pressed and not self.rclick:
            self.rclick = True
        elif not self.mouse.rbutton_pressed and self.rclick:
            self.lclick = False


# Mapping between libtcod and our own constants.
keys = {tcod.KEY_ESCAPE: Inputs.ESCAPE,
        tcod.KEY_UP: Inputs.UP,
        tcod.KEY_DOWN: Inputs.DOWN,
        tcod.KEY_LEFT: Inputs.LEFT,
        tcod.KEY_RIGHT: Inputs.RIGHT,
        tcod.KEY_ENTER: Inputs.ENTER,
        tcod.KEY_END: Inputs.END,
        tcod.KEY_SPACE: Inputs.SPACE,
        tcod.KEY_BACKSPACE: Inputs.BACKSPACE,
        tcod.KEY_F1: Inputs.F1,
        tcod.KEY_F2: Inputs.F2,
        tcod.KEY_F3: Inputs.F3,
        tcod.KEY_F4: Inputs.F4,
        tcod.KEY_F5: Inputs.F5,
        tcod.KEY_F6: Inputs.F6,
        tcod.KEY_F7: Inputs.F7,
        tcod.KEY_F8: Inputs.F8,
        tcod.KEY_F9: Inputs.F9,
        tcod.KEY_F10: Inputs.F10,
        tcod.KEY_F11: Inputs.F11,
        tcod.KEY_F12: Inputs.F12}
