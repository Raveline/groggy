from groggy.ui.components.component import Component, ComponentEvent
from groggy.events import bus


class ContainerComponent(Component):
    """An abstract class for containers that contain others."""
    def __init__(self, x, y, w=0, h=0, is_selectable=False, children=None):
        super(ContainerComponent, self).__init__(x, y, w, h, is_selectable)
        if children is None:
            children = []
        self.selected_index = 0
        self.set_children(children)

    def set_children(self, children):
        self.children = children
        self.selectable_children = [c for c in self.children
                                    if c.is_selectable]
        self.has_selectable = bool(self.selectable_children)

    def get_selected(self):
        if self.has_selectable:
            return self.selectable_children[self.selected_index]

    def receive(self, event_data):
        if not self.has_selectable:
            return
        if event_data == ComponentEvent.NEXT:
            self.update_selected_index(1)
        elif event_data == ComponentEvent.PREVIOUS:
            self.update_selected_index(-1)
        else:
            self.get_selected().receive(event_data)

    def update_selected_index(self, by):
        self.get_selected().leave_focus()
        self.selected_index += by
        if self.selected_index < 0:
            self.selected_index = 0
            self.leave_focus()
            self.send_previous()
        elif self.selected_index >= len(self.selectable_children):
            self.selected_index = len(self.selectable_children) - 1
            self.leave_focus()
            self.send_next()
        else:
            self.get_selected().enter_focus()

    def update(self, values):
        for child in self.children:
            child.update(values)

    def enter_focus(self):
        bus.bus.subscribe(self, bus.MENU_ACTION)
        selection = self.get_selected()
        if selection:
            selection.enter_focus()

    def leave_focus(self):
        self.get_selected().focused = False
        bus.bus.unsubscribe(self, bus.MENU_ACTION)
