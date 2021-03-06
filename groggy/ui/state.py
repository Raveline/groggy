"""
This module handles game states.
States are a core concept of the Groggy framework. A State is a situation
in a game, that determinates the result of inputs, the things to display,
and so on.

Game comes from one state to the other in the fashion of a stack.
E.g. : Main menu -> Main Game State -> A Game submenu, all those three
states will stack; if one is left, game will come back to the previous
state.

There are mainly two types of states:
    - GameStates are there to display a world, and handle interactions
    with this world. This typically means that a GameState should be able
    to build some Command pattern and send it through the event bus.
    - MenuStates handle the ugly world of windows, desktop-based ui, and so
    on.

States behaviour are dynamically build from "Trees", namely dictionaries.
This dictionnary would typically include the following information:
    - 'name' for the name of the state, used for debugging purposes.
    - If this is a substate, it probably has an 'action', namely a main
    action that will be used to build the related command. E.g., launching
    a spell in a typicall roguelike, putting an object somewhere in a
    management game, etc.
    - If this is more a "general state" (typically the main game state), it
    exposes an "actions" dictionnary (note the plural) that tells in what kind
    of substates one can enter. Note that those actions are supposed to be
    states, and if called, will launch the "NEW_STATE" event and stack a state.
    Changing state (and building the proper one) is a responsability of the
    Game class.
    - Finally, a "pauses_game" flag should tell if the game is paused when
    in this state or if real-time display should still be on.
    """
from groggy.events import bus

NEW_STATE = 0

NAVIGATING_STATE = 0
MENU_STATE = 1


class InvalidTreeException(Exception):
    pass


class GameState(object):
    def __init__(self, state_tree, state_type, parent_state=None):
        self.tree = state_tree
        """The stree definition of this state."""
        self.parent_state = parent_state
        """The previous state. If we leave this state, we'll come back
        to this parent state."""
        try:
            self.name = self.tree['name']
            """States must have a name, so it can be displayed"""
        except:
            raise InvalidTreeException('State defined by tree %s has no name.'
                                       % self.tree)
        """Scape states must provide a viewport."""
        self.action = self.tree.get('action', '')
        """The main action associated to this state."""
        self.actions = state_tree.get('actions', {})
        """Potential substates if any"""
        self.pauses_game = state_tree.get('pauses_game', True)
        """By default, every state pauses game but the main state."""
        self.state_type = state_type

    def is_scape_state(self):
        return self.state_type == NAVIGATING_STATE

    def receive(self, event):
        pass

    def pick_substate(self, event_data):
        """
        If the event_data is associated to a substate, return the substate.
        """
        substate = self.actions.get(event_data)
        if substate:
            bus.bus.publish(substate,
                            bus.NEW_STATE)
        return substate

    def activate(self):
        """Actions to take when entering state."""
        pass

    def deactivate(self):
        """Actions to take when leaving state."""
        pass

    def clean(self):
        """Actions to take when state should be destroyed."""
        pass

    def call_previous_state(self):
        bus.bus.publish(self.parent_state, bus.PREVIOUS_STATE)


class ViewportState(GameState):
    """
    This is a state that allow, amongst other features, manipulating
    a viewport. In other words, any state of the game where a part of
    the world is displayed and must scroll.
    """
    def __init__(self, state_tree, parent_state=None, viewport=None,
                 selection=None):
        super(ViewportState, self).__init__(state_tree, NAVIGATING_STATE,
                                            parent_state)
        self.viewport = viewport
        """The part of the world that is displayed."""
        self.selection = selection
        """The way "area" interaction with the world are represented.
        The selection will typically receive movement input.
        It might be the canonical '@', a crosshair, etc."""

    def handle_selection_move(self, event_data, keys=True):
        if keys:
            self.selection.receive_keys(event_data, self.viewport)
        else:
            self.selection.receive_mouse(event_data, self.viewport)

    def dispatch_input_event(self, event_data):
        """React to a simple input. Very often, it will mean
        passing the input to the scape, so this is the default
        behaviour, but you absolutely should override this if
        the player can do other things than moving."""
        self.handle_selection_move(event_data)

    def dispatch_selection_event(self, event_data):
        """React to a "confirmation" event."""
        pass

    def receive(self, event):
        event_data = event.get('data')
        event_type = event.get('type')
        if event_type == bus.LEAVE_EVENT:
            self.check_for_previous_state(event_data)
        if event_type == bus.MOUSE_MOVE_EVENT:
            self.handle_selection_move(event_data, False)
        if event_type == bus.INPUT_EVENT:
            self.dispatch_input_event(event_data)
        elif event_type == bus.AREA_SELECT:
            self.dispatch_selection_event(event_data)
            need_subobject = (bool(self.tree.get('submenu')) and
                              self.sub_object is None)
            if not need_subobject:
                self.send_command(event_data)
            elif need_subobject:
                keys = ['(' + k + ')' for k in self.tree.get('submenu').keys()]
                bus.bus.publish('Pick between ' + ', '.join(keys))

    def send_command(self, area):
        pass

    def check_for_previous_state(self, event_data):
        """
        Go to previous state if and only if :
            - There is no current selection in the scape
            - There is a parent state
        """
        if not self.selection.selected_area and self.parent_state is not None:
            self.call_previous_state()
            self.selection.set_char()
            return True
        elif self.selection.selected_area:
            self.selection.set_char()
            self.sub_object = None
        return False

    def __repr__(self):
        if self.sub_object_display:
            return "%s : %s" % (self.name, self.sub_object_display)
        else:
            return self.name

    def to_keys_array(self):
        """Used to feed the help menu."""
        to_return = []
        for k in self.actions.keys():
            to_return.append(k)
        for k in self.tree.get('submenu', {}).keys():
            to_return.append(k)
        return to_return

    def to_actions_dict(self):
        """Used to display the help menu.
        Should only be used on main menu."""
        to_return = {}
        for k, v in self.actions.iteritems():
            to_return[k] = {'key': k, 'name': v['name']}
        for v in self.tree.get('submenu', []):
            to_return[k] = {'key': k, 'name': v['display']}
        return to_return


class MenuState(GameState):
    '''
    A menu is a temporary state used by the player to make some choices,
    feed some data to the game or access them.

    Menu has its own console, and uses Components. Components are able to
    read data from a dictionary of data and, when they are updated, they
    will send a MENU_MODEL_EVENT to indicate there is a new value.

    Components are typically build using the module component_builder, so
    that component can be defined through a simple dictionary.

    To build the menu logic, you inherit this class, and implement your
    own receiver. The steps are as follow:

    - The model is always a dictionary (be careful, this means lots of
      bug will come from this dynamic but two-edged tool...).

    - Setting data for the components means that every component will
      translate the dict to its own display. A checkbox will look for
      a boolean value, an input box for a text, and so on.

    - When a component is updated by the player input, it will end up
      in the receive method of the MenuState. From this, the state can
      validate the input, take action, and finally reset the data if needed,
      to update the whole view.
    '''
    def __init__(self, state_tree, root_component, parent_state=None,
                 data=None):
        super(MenuState, self).__init__(state_tree, MENU_STATE, parent_state)
        self.root_component = root_component
        self.set_data(data)

    def set_data(self, data):
        self.data = data
        self.root_component.set_data(data)

    def check_for_previous_state(self, event_data):
        if not event_data:
            bus.bus.publish(self.parent_state, bus.PREVIOUS_STATE)
        return True

    def activate(self):
        bus.bus.subscribe(self, bus.MENU_MODEL_EVENT)
        self.root_component.enter_focus()

    def deactivate(self):
        bus.bus.unsubscribe(self, bus.MENU_MODEL_EVENT)

    def clean(self):
        self.root_component.deactivate()

    def update_data_dict(self, source, new):
        data = self.data
        path = source.split('.')
        for s in path[:-1]:
            data = data.get(s)
        data[path[-1]] = new
        return data

    def update_data(self, source, new):
        data = self.update_data_dict(self, source, new)
        self.set_data(data)

    def receive(self, event):
        event_data = event.get('data')
        event_type = event.get('type')
        if event_type == bus.MENU_MODEL_EVENT:
            self.receive_model_event(event_data)
        elif event_type == bus.MOUSE_MOVE_EVENT:
            x = event_data.get('x')
            y = event_data.get('y')
            for pos, item in self.to_positions().items():
                if ((x >= pos[0] and x <= pos[2]) and
                    (y >= pos[1] and y <= pos[3])):
                    self.root_component.update_directly_index(
                        set_directly=self.root_component.children.index(item))
                    # TODO : use same logic if the component is container
                    # So probably should be set lower in the logic ?
        elif event_type == bus.LEAVE_EVENT:
            self.check_for_previous_state(event_data)
        else:
            self.root_component.receive(event_data)

    def receive_model_event(self, event_data):
        pass

    def __str__(self):
        return "Menu"

    def to_positions(self):
        x_offset = self.root_component.x
        y_offset = self.root_component.y
        positions = {}
        for item in self.root_component.children:
            x = item.x + x_offset
            y = item.y + y_offset
            x2 = x + item.w
            y2 = y + item.h
            positions[(x, y, x2, y2)] = item
        return positions
