import libtcodpy as tcod
import groggy.utils.bus as bus
from groggy.inputs.input import Inputs
from groggy.viewport.scape import Crosshair, Fillhair, Selection
from groggy.utils.tcod_wrapper import Console
from groggy.utils.geom import Frame
from groggy.view.show_console import display, print_selection, display_text
from groggy.view.show_console import display_creatures
from groggy.ui.state import GameState
from groggy.ui.component_builder import build_menu


class Game(object):
    """
    An abstraction to represent the whole game process.
    """
    def __init__(self, title, width, height, fps=60):
        tcod.console_init_root(width, height, TITLE)
        self.initialize_consoles(width, height)

        self.inputs = Inputs(bus.bus)
        bus.bus.subscribe(self, bus.GAME_EVENT)
        bus.bus.subscribe(self, bus.NEW_STATE)
        bus.bus.subscribe(self, bus.PREVIOUS_STATE)

        self.state = None
        self.continue_game = True
        self.setup_first_state()

        self.fps = fps

    def initialize_consoles(self, width, height):
        """
        Setup the various consoles that will be used most often by the Game
        """
        raise NotImplementedError('initialize_consoles must be implemented')

    def initialize_world(self):
        """
        Setup the general world itself.
        """
        raise NotImplementedError('initialize_world must be implemented')

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

    def display(self):
        """
        Fill the consoles with various information.
        """
        raise NotImplementedError('display must be implemented.')

    def loop(self):
        """
        Main game loop.
        """
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
            if tick and not self.state.pauses_game:
                model_tick(self)
            self.display(blink)
            self.state.display(0)
            self.inputs.poll()
            tcod.console_flush()
            tick = False

    def change_state(self, new_state):
        if self.state is not None:
            # Remove the old state from input receiving
            bus.bus.unsubscribe(self.state, bus.INPUT_EVENT)
            bus.bus.unsubscribe(self.state, bus.AREA_SELECT)
            self.state.deactivate()
        self.state = new_state
        # Add the new state to input receiving
        bus.bus.subscribe(self.state, bus.INPUT_EVENT)
        bus.bus.subscribe(self.state, bus.AREA_SELECT)
        self.state.activate()

    def receive(self, event):
        event_data = event.get('data')
        if event.get('type', '') == bus.NEW_STATE:
            new_state = self.build_state(event_data)
            if new_state is not None:
                self.change_state(new_state)
        elif event.get('type', '') == bus.PREVIOUS_STATE:
            self.change_state(event_data)
        elif event_data == 'quit':
            self.continue_game = False
