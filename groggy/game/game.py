import logging
from logging.config import dictConfig

import libtcodpy as tcod

import groggy.events.bus as bus
from groggy.logging import LOG_CONFIG
from groggy.inputs.input import Inputs


dictConfig(LOG_CONFIG)
logger = logging.getLogger(__name__)


class StateSwitchingException(Exception):
    pass


class Game(object):
    """
    An abstraction to represent the whole game process.

    A Game should have:

    - Consoles, to display stuff.

    - A "world", or game model.

    - A "displayer" utility tool tasked with printing
      the consoles.

    - A state stack (see state doc for more about this)

    - The inputs manager (typically handled by Groggy itself).
    """
    def __init__(self, title, width, height, fps=60):
        self.width = width
        """Width of the main window"""
        self.height = height
        """Height of the main window"""

        tcod.console_init_root(self.width, self.height, title)
        self.consoles = self.initialize_consoles()
        """Consoles registered"""
        logger.info('Initialized %d consoles.' % len(self.consoles))
        self.initialize_world()
        logger.info('Initialized world')
        self.displayer = self.initialize_displayer()
        """Display utility"""
        logger.info('Displayer initialized')

        self.inputs = Inputs(bus.bus)
        bus.bus.subscribe(self, bus.GAME_EVENT)
        bus.bus.subscribe(self, bus.NEW_STATE)
        bus.bus.subscribe(self, bus.PREVIOUS_STATE)
        bus.bus.subscribe(self, bus.LEAVE_EVENT)

        self.state = None
        """The current state"""
        self.state_stack = []
        """All previous states, in the order they were entered"""

        self.continue_game = True
        self.setup_first_state()
        logger.info('First state initialized, really to run')

        self.fps = fps

    def initialize_consoles(self):
        """
        Setup the various consoles that will be used most often by the Game
        """
        raise NotImplementedError('initialize_consoles must be implemented')

    def initialize_world(self):
        """
        Setup the general world itself.
        """
        raise NotImplementedError('initialize_world must be implemented')

    def initialize_displayer(self):
        """
        Setup the Displayer.
        """
        raise NotImplementedError('initialize_displayer must be implemented')

    def setup_first_state(self):
        """
        Create the first state of the game
        """
        raise NotImplementedError('setup_first_state must be implemented')

    def model_tick(self):
        """
        Make the world progress one tick.
        """
        raise NotImplementedError('model_tick must be implemented')

    def build_state(self, tree):
        """
        Build the new state the game must be set into from its tree.
        """
        raise NotImplementedError('build_state must be implemented.')

    def display(self, blink):
        """
        Fill the consoles with various information.
        """
        pass

    def before_loop(self):
        """
        Actions to take before entering the loop.
        """
        pass

    def start_loop(self):
        """
        Main game loop.
        """
        self.before_loop()
        tcod.sys_set_fps(50)
        # Couting elapsed milliseconds
        counter = 0
        # Flag : should the cursor be blinking ?
        blink = False
        # Flag : should tick happen during this loop ?
        tick = False
        while self.continue_game:
            counter += tcod.sys_get_last_frame_length()
            if counter >= .4:
                blink = not blink
                tick = True
                counter = 0
            self.loop_content(tick, blink)
            tick = False

    def loop_content(self, tick, blink):
        if tick and not self.state.pauses_game:
            self.model_tick()
        self.displayer.call(blink, self.state, self.consoles)
        self.inputs.poll()

    def change_state(self, new_state):
        logger.info('Leaving old state %s' % self.state)
        if self.state is not None:
            # Remove the old state from input receiving
            bus.bus.unsubscribe(self.state, bus.INPUT_EVENT)
            bus.bus.unsubscribe(self.state, bus.AREA_SELECT)
            bus.bus.unsubscribe(self.state, bus.LEAVE_EVENT)
            self.state.deactivate()
        else:
            # This is the first state ever : it should be
            # put on the stack only once, this very time.
            self.state_stack.append(new_state)
        self.state = new_state
        logger.info('State is now %s' % self.state)
        # Add the new state to input receiving
        bus.bus.subscribe(self.state, bus.INPUT_EVENT)
        bus.bus.subscribe(self.state, bus.AREA_SELECT)
        bus.bus.subscribe(self.state, bus.LEAVE_EVENT)
        self.state.activate()

    def receive(self, event):
        event_data = event.get('data')
        if event.get('type', '') == bus.NEW_STATE:
            logger.info('Received new state event')
            new_state = self.build_state(event_data)
            if new_state is not None:
                self.state_stack.append(new_state)
                self.change_state(new_state)
        elif event.get('type', '') == bus.PREVIOUS_STATE:
            logger.info('Received previous state event')
            if event_data in self.state_stack:
                idx = self.state_stack.index(event_data)
                stale_states = self.state_stack[idx + 1:]
                for stale_state in stale_states:
                    stale_state.clean()
                self.state_stack = self.state_stack[:idx + 1]
                self.change_state(event_data)
            else:
                raise StateSwitchingException(
                    'State %s was not in the stack of previous states.'
                    % event_data
                )
            self.change_state(event_data)
        elif event_data == 'quit':
            self.continue_game = False
