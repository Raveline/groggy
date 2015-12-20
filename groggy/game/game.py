import libtcodpy as tcod
import tavern.utils.bus as bus
from tavern.inputs.input import Inputs
from tavern.receivers.navigators import Crosshair, Fillhair, Selection
from tavern.utils.tcod_wrapper import Console
from tavern.utils.geom import Frame
from tavern.view.show_console import display, print_selection, display_text
from tavern.view.show_console import display_creatures
from tavern.ui.state import (GameState, MenuState, ExamineMenu,
                             PricesMenuState, BuyMenuState, HelpMenuState)
from tavern.ui.component_builder import build_menu
from tavern.ui.informer import Informer
from tavern.ui.status import Status
from tavern.world.customers import Customers
from tavern.world.actions import door, counter, chair, oven, work_station
from tavern.world.map_commands import BuildCommand, PutCommand, RoomCommand
from tavern.world.context import Context
from tavern.world.world import Tavern
from tavern.world.actions import action_tree
from tavern.world import actions


MAP_WIDTH = 200
MAP_HEIGHT = 200

TITLE = 'The Tavern'


def main():
    game = Game()
    game.loop()


class Game(object):
    def __init__(self):
        self.context = Context()
        width = self.context.width
        height = self.context.height
        tcod.console_init_root(width, height, TITLE)
        self.status_console = Console(0, 0, width, 1)
        self.world_console = Console(0, 1, width, height - 3)
        self.text_console = Console(0, height - 2, width, 2)
        self.inputs = Inputs(bus.bus)

        self.tavern = Tavern(MAP_WIDTH, MAP_HEIGHT)
        bus.bus.subscribe(self.tavern, bus.WORLD_EVENT)
        bus.bus.subscribe(self.tavern, bus.CUSTOMER_EVENT)
        self.customers = Customers(self.tavern)

        self.informer = Informer(self.text_console)
        bus.bus.subscribe(self.informer, bus.FEEDBACK_EVENT)

        self.status = Status(self.status_console)
        bus.bus.subscribe(self.status, bus.STATUS_EVENT)

        self.world_frame = Frame(0, 0, MAP_WIDTH, MAP_HEIGHT)
        self.cross = Crosshair(width, height, self.world_frame)
        self.filler = Fillhair(width, height, self.world_frame,
                               self.tavern.tavern_map.fill_from)
        self.state = None
        self.change_state(GameState(action_tree, self.cross))
        bus.bus.subscribe(self, bus.GAME_EVENT)
        bus.bus.subscribe(self, bus.NEW_STATE)
        bus.bus.subscribe(self, bus.PREVIOUS_STATE)

        self.receiver = self.cross
        self.continue_game = True

    def display_background(self):
        display(self.clip_world(self.tavern.tavern_map.tiles[0],
                                self.receiver.scape.frame),
                self.world_console.console)

    def display_characters(self):
        display_list = [crea for crea in self.tavern.creatures
                        if self.receiver.scape.frame.contains(crea.x, crea.y)]
        display_creatures(self.world_console.console, display_list,
                          self.cross.global_to_local)

    def display_text(self):
        tcod.console_clear(self.text_console.console)
        self.informer.display()

    def display_navigation(self, blink):
        if self.state.navigator:
            if not blink:
                print_selection(self.world_console.console,
                                self.state.navigator)
            cre = self.get_selected_customer()
            if cre:
                self.describe_creature(cre)
            else:
                self.describe_area()

    def loop(self):
        tcod.sys_set_fps(50)
        # Couting elapsed milliseconds
        counter = 0
        # Flag : should the cursor be blinking ?
        blink = False
        # Flag : should tick happen during this loop ?
        tick = False
        # ONLY FOR TESTING PURPOSE, REMOVE
        self.test_bootstrap()
        while self.continue_game:
            counter += tcod.sys_get_last_frame_length()
            if counter >= .4:
                blink = not blink
                tick = True
                counter = 0
            if tick and not self.state.pauses_game:
                self.tavern.tick()
                self.customers.tick()
            self.display_background()
            self.display_characters()
            self.display_status()
            self.display_text()
            self.display_navigation(blink)
            self.inputs.poll()
            self.world_console.blit_on(0)
            self.text_console.blit_on(0)
            self.status_console.blit_on(0)
            self.state.display(0)
            tcod.console_flush()
            tick = False

    def display_status(self):
        self.status.pause = self.state.pauses_game
        self.status.money = self.tavern.cash
        self.status.current_state = str(self.state)
        self.status.display()

    def get_selected_customer(self):
        return self.tavern.creature_at(self.state.navigator.getX(),
                                       self.state.navigator.getY(),
                                       0)

    def __build_menu_state(self, tree):
        context = self.context.to_context_dict()
        clazz = MenuState
        data = self.tavern
        menu_type = tree.get('menu_type')
        if menu_type == 'BuyMenu':
            clazz = BuyMenuState
        elif menu_type == 'PricesMenu':
            clazz = PricesMenuState
        elif menu_type == 'Help':
            clazz = HelpMenuState
            data = self.state
            context['state'] = self.state.to_keys_array()
        elif menu_type == 'ExamineMenu':
            examined = self.get_selected_customer()
            if examined and examined.examinable:
                clazz = ExamineMenu
                data = examined
            else:
                return None
        root_component = build_menu(context, tree.get('content'), True)
        return clazz({}, root_component, self.state, data)

    def build_state(self, tree):
        if tree.get('type', '') == 'menu':
            return self.__build_menu_state(tree)
        elif tree.get('type', '') == 'box':
            return MenuState({}, tree.get('box'), self.state)
        else:
            if tree.get('selector', actions.CROSSHAIR) == actions.CROSSHAIR:
                navigator = self.cross
            elif tree.get('selector', actions.FILLER) == actions.FILLER:
                navigator = self.filler
            navigator.set_coords(self.state.navigator)
            return GameState(tree, navigator, self.state)

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

    def describe_area(self):
        x, y = self.state.navigator.getX(), self.state.navigator.getY()
        pos = (x, y, self.state.navigator.getZ())
        tile = self.tavern.tavern_map[pos]
        text = "(%d, %d) - %s" % (x, y, tile.describe())
        display_text(self.text_console.console, text, 0, 0)

    def describe_creature(self, c):
        display_text(self.text_console.console, str(c), 0, 0)

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

    def clip_world(self, tiles, clip_box):
        clipped_y = tiles[clip_box.y:clip_box.y + clip_box.h]
        clipped = [t[clip_box.x:clip_box.x + clip_box.w] for t in clipped_y]
        return clipped

    def __repr__(self):
        return "Main"

if __name__ == "__main__":
    main()
