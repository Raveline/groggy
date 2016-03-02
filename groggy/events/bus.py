'''
A fairly simple event bus implementation.
There is a global bus offered by default, but a new one,
that would not be global, can be created easily.

This bus does not store events. It dispatches them immediately.

Potential receivers should register through the "subscribe" method.

They should also unsubscribe when they are not to listen anymore through
the "unsubscribe" method.

A listener do not listen to every messages. It only listen to messages of
a given type. This type should be a constant.

If specific event types are required, I strongly suggest inheriting this class.

Events are simply a dictionary and an event_type. Senders are responsible for
giving the proper information.

When any piece of code wants to send an event, it simply calls the "publish"
method of the bus with the event and the event_type as parameters.
'''
import inspect
import logging
from collections import defaultdict


# Input management (0-10)
INPUT_EVENT = 0         # Input pressed
AREA_SELECT = 1         # Area was selected
PLAYER_ACTION = 2       # Any specific action from the player
MENU_ACTION = 3         # Event to handle user input in menu
LEAVE_EVENT = 4         # General idea of leaving typically by pressing Escape.
MOUSE_MOVE_EVENT = 5    # Mouse moved
MOUSE_CLICK_EVENT = 6   # Mouse was clicked

# Game state management (10-20)
NEW_STATE = 10          # Event to push a new game state
PREVIOUS_STATE = 11     # Event to request the previous game state
MENU_MODEL_EVENT = 12   # Event to handle model change in menu
FEEDBACK_EVENT = 13     # Simple feedback from the game (used for logs)

# Game specific events (100)
GAME_EVENT = 100          # General game-related event
WORLD_EVENT = 101         # General event worldwide


class Bus(object):
    EVENTS_NAMES = {INPUT_EVENT: 'Input event',
                    AREA_SELECT: 'Area select',
                    PLAYER_ACTION: 'Player action',
                    FEEDBACK_EVENT: 'Feedback event',
                    GAME_EVENT: 'Game event',
                    WORLD_EVENT: 'World event',
                    NEW_STATE: 'New state',
                    PREVIOUS_STATE: 'Previous state',
                    MENU_ACTION: 'Menu event',
                    MENU_MODEL_EVENT: 'Menu model event',
                    LEAVE_EVENT: 'Leave event',
                    WORLD_EVENT: 'World event'}

    def __init__(self):
        self.events = defaultdict(list)
        self.debug = False
        self.max_debug = False

    def activate_debug_mode(self, maximum=False, type_blacklist=None):
        """
        Set up the debug mode. Events will be logged to the event_debug.log
        file. A list of events not to be logged can be given in parameter.
        Setting the "maximum" flag will also log where the events came from.
        """
        self.debug = True
        self.max_debug = maximum
        self.logger = logging.getLogger('event_bus')
        handler = logging.FileHandler('event_debug.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        if self.max_debug:
            self.logger.setLevel(logging.DEBUG)
        self.type_blacklist = type_blacklist or []

    def subscribe(self, receiver, event_type):
        try:
            for x in event_type:
                self.__subscribe(receiver, x)
        except TypeError:
            self.__subscribe(receiver, event_type)

    def __subscribe(self, receiver, event_type):
        self.events[event_type].append(receiver)

    def unsubscribe(self, receiver, event_type):
        try:
            for x in event_type:
                self.__unsubscribe(receiver, x)
        except TypeError:
            self.__unsubscribe(receiver, event_type)

    def __unsubscribe(self, receiver, event_type):
        try:
            self.events.get(event_type).remove(receiver)
        except:
            self.publish("Trying to remove a receiver that was not subscribed")

    def publish(self, event, event_type=FEEDBACK_EVENT):
        '''
        Send an event for every listeners.
        '''
        event = {'type': event_type,
                 'data': event}
        if self.debug and event_type not in self.type_blacklist:
            self.logger.info(self.event_display(event))
            if self.max_debug:
                curframe = inspect.currentframe()
                calframe = inspect.getouterframes(curframe, 2)
                module = calframe[1][1]
                loc = calframe[1][2]
                method = calframe[1][3]
                self.logger.debug("Send by %s:%s (module %s)",
                                  method, loc, module)

        # For MENU EVENT, act in a stacky, LIFO way
        if event_type == MENU_ACTION:
            self.events.get(event_type)[-1].receive(event.get('data'))
        # In any other case, publish for every listener
        else:
            for receiver in self.events[event_type]:
                receiver.receive(event)

    def event_display(self, event):
        '''
        Return a proper string for a single event.
        '''
        return 'Event fired. Type %s - data : %s' % (
            self.EVENTS_NAMES.get(event['type'], 'unknown (%d)' % event['type']),
            event['data'])

    def __str__(self):
        '''
        Debugging utility: see who listens to what.
        '''
        representation = []
        for event_key, event_name in self.EVENTS_NAMES.items():
            representation.append(event_name)
            for subscriber in self.events[event_key]:
                representation.append('- %s' % repr(subscriber))
        return '\n'.join(representation)

# Beware, this is global
bus = Bus()
