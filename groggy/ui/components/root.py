import libtcodpy as tcod
from groggy.events import bus
from groggy.ui.components.container import ContainerComponent
from groggy.utils.tcod_wrapper import Console


class RootComponent(ContainerComponent):
    """A component with an attached console."""
    def __init__(self, x, y, w, h, title, children):
        super(RootComponent, self).__init__(x, y, w, h, False, children)
        self.console = Console(x, y, w, h)
        self.title = title

    def deactivate(self):
        bus.bus.unsubscribe(self, bus.MENU_ACTION)
        tcod.console_delete(self.console.console)

    def display(self, console):
        """
        Display a frame, a title and children components.
        Then blit on the console parameter.
        """
        tcod.console_clear(self.console.console)
        tcod.console_set_default_foreground(self.console.console,
                                            tcod.white)
        tcod.console_hline(self.console.console, 0, 0, self.console.w)
        tcod.console_hline(self.console.console, 0,
                           self.console.h - 1, self.console.w)
        tcod.console_vline(self.console.console, 0, 0, self.console.h)
        tcod.console_vline(self.console.console, self.console.w - 1,
                           0, self.console.h)
        tcod.console_print_ex(self.console.console, int(self.console.w / 2),
                              0, tcod.BKGND_SET, tcod.CENTER, self.title)
        for child in self.children:
            child.display(self.console.console)
        self.console.blit_on(console.console)

    def set_children(self, children):
        super(RootComponent, self).set_children(children)
        if len(self.selectable_children):
            self.selectable_children[0].enter_focus()

    def set_data(self, data):
        self.data = data
        for child in self.children:
            child.set_data(data)

    def update_selected_index(self, by):
        self.get_selected().leave_focus()
        self.selected_index += by
        if self.selected_index < 0:
            self.selected_index = len(self.selectable_children) - 1
        elif self.selected_index >= len(self.selectable_children):
            self.selected_index = 0
        self.get_selected().enter_focus()

    def __str__(self):
        return "RootComponent"
