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
from groggy.inputs.input import Inputs

NEW_STATE = 0


class InvalidTreeException(Exception):
    pass


class GameState(object):
    def __init__(self, state_tree, parent_state=None):
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
        """Actions are associated to a main action."""
        self.actions = state_tree.get('actions', {})

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
            self.navigator.set_char()
        return substate


class ScapeState(GameState):
    def __init__(self, state_tree, parent_state=None, scape=None):
        super(ScapeState, self).__init__(state_tree, parent_state)
        self.scape = scape
        """Sub actions can have a complement, the sub_object."""
        self.pauses_game = state_tree.get('pauses_game', True)
        """By default, every state pauses game but the main state."""

    def deactivate(self):
        """Actions to take when leaving state."""
        pass

    def activate(self):
        """Actions to take when entering state."""
        pass

    def dispatch_input_event(self, event_data):
        """React to a simple input. Very often, it will mean
        passing the input to the scape."""
        pass

    def dispatch_selection_event(self, event_data):
        """React to a "confirmation" event."""
        pass

    def receive(self, event):
        event_data = event.get('data')
        event_type = event.get('type')
        if event_type == bus.LEAVE_EVENT:
            self.check_for_previous_state()
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
        if not self.navigator.selection and self.parent_state is not None:
            bus.bus.publish(self.parent_state, bus.PREVIOUS_STATE)
            self.navigator.set_char()
            return True
        return False

    def display(self, console):
        pass

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
    def __init__(self, state_tree, root_component, parent_state=None,
                 data=None):
        super(MenuState, self).__init__(state_tree, parent_state)
        bus.bus.subscribe(self, bus.MENU_MODEL_EVENT)
        self.root_component = root_component
        self.set_data(data)

    def set_data(self, data):
        self.data = data
        self.root_component.set_data(data)

    def _check_for_previous_state(self, event_data):
        if event_data == Inputs.ESCAPE:
            bus.bus.publish(self.parent_state, bus.PREVIOUS_STATE)
            return True
        return False

    def deactivate(self):
        bus.bus.unsubscribe(self, bus.MENU_MODEL_EVENT)
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
        if event.get('type') == bus.MENU_MODEL_EVENT:
            self.receive_model_event(event_data)
        else:
            if not self._check_for_previous_state(event_data):
                self.root_component.receive(event_data)

    def display(self, console):
        self.root_component.display(console)

    def receive_model_event(self, event_data):
        pass

    def __str__(self):
        return "Menu"
