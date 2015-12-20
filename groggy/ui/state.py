"""
This module handles game states.
States are a core concept of the Groggy framework. A State is a situation
in a game, that determinates the result of inputs, the things to display,
and so on.

States are dynamically build from "Trees", namely dictionaries.

Game comes from one state to the other in the fashion of a stack.
E.g. : Main menu -> Main Game State -> A Game submenu, all those three
states will stack; if one is left, game will come back to the previous
state.
"""
from groggy.utils import bus
from groggy.utils.dict_path import read_path_dict
from groggy.ui.component_builder import make_questionbox
from groggy.inputs.input import Inputs

NEW_STATE = 0


class GameState(object):
    def __init__(self, state_tree, navigator=None, parent_state=None):
        self.tree = state_tree
        """The stree definition of this state."""
        self.parent_state = parent_state
        """The previous state. If we leave this state, we'll come back
        to this parent state."""
        self.navigator = navigator
        """Game states must provide a viewport."""
        self.name = self.tree.get('name', '')
        """States must have a name, so it can be displayed"""
        self.action = self.tree.get('action', '')
        """Actions are associated to a main action."""
        self.actions = state_tree.get('actions')
        """And provide access to sub-actions."""
        self.sub_object = None
        """Sub actions can have a complement, the sub_object."""
        self.sub_object_display = None
        """This sub_object should also have a way to be displayed."""
        self.pauses_game = state_tree.get('pauses_game', True)
        """By default, every state pauses game but the main state."""

    def deactivate(self):
        pass

    def activate(self):
        self.sub_object = None

    def change_sub_object_display(self):
        if not isinstance(self.sub_object, int):
            if self.sub_object.is_multi_tile():
                self.navigator.set_multi_char(self.sub_object.character,
                                              self.sub_object.width,
                                              self.sub_object.height)
            else:
                self.navigator.set_char(self.sub_object.character)

    def receive(self, event):
        def pick_substate(event_data):
            if self.actions:
                substate = self.actions.get(event_data)
                if substate:
                    bus.bus.publish(substate,
                                    bus.NEW_STATE)
                    self.navigator.set_char()
                return substate

        def pick_subobject(event_data):
            subobject = self.tree.get('submenu', {}).get(event_data)
            if subobject:
                self.sub_object = subobject.get('subobject')
                self.sub_object_display = subobject.get('display')
                self.change_sub_object_display()

            return subobject

        def check_pause(event_data):
            if event_data == Inputs.SPACE:
                self.pauses_game = not self.pauses_game

        event_data = event.get('data')
        if (event.get('type') == bus.INPUT_EVENT):
            if not (pick_substate(event_data) or
                    pick_subobject(event_data) or
                    check_pause(event_data) or
                    self._check_for_previous_state(event_data))\
                    and self.navigator:
                self.navigator.receive(event_data)
        elif (event.get('type') == bus.AREA_SELECT):
            need_subobject = (bool(self.tree.get('submenu')) and
                              self.sub_object is None)
            if not need_subobject:
                self.send_command(event_data)
            elif need_subobject:
                keys = ['(' + k + ')' for k in self.tree.get('submenu').keys()]
                bus.bus.publish('Pick between ' + ', '.join(keys))

    def send_command(self, area):
        if self.action == Actions.BUILD:
            command = BuildCommand(area)
        elif self.action == Actions.PUT:
            command = PutCommand(area, self.sub_object)
            self.change_sub_object_display()
        elif self.action == Actions.ROOMS:
            command = RoomCommand(area, self.sub_object)
        if command is not None:
            bus.bus.publish({'command': command}, bus.WORLD_EVENT)

    def _check_for_previous_state(self, event_data):
        """
        Go to previous state if and only if :
            - The escape key has been hit
            - There is no current selection in the navigator
            - There is a parent state
        """
        if event_data == Inputs.ESCAPE and\
            not self.navigator.selection and\
                self.parent_state is not None:
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
        super(MenuState, self).__init__(state_tree, None, parent_state)
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
