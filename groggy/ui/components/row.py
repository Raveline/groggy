from groggy.ui.components.component import Component
from groggy.ui.components.container import ContainerComponent
from groggy.view.show_console import display_highlighted_text, display_text


class RowsComponent(ContainerComponent):
    """
    A series of components built as a line.
    """
    def __init__(self, x, y, w=0, h=0, selectable=False, contents=None):
        super(RowsComponent).__init__(x, y, w, h, selectable)
        if contents is None:
            contents = []
        self.contents = contents
        self.compute_widths()
        self.buid_rows()

    def compute_widths(self):
        lens = [(len(col) for col in row) for row in self.contents]
        self.widths = [max(sizes) for sizes in lens]

    def build_rows(self):
        for idx, c in enumerate(self.contents):
            self.children.append(ColumnedLine(self.x, self.y + idx,
                                              self.is_selectable,
                                              self.widths, c))

    def display(self, console):
        for c in self.children:
            c.display(console)


class ColumnedLine(Component):
    def __init__(self, x, y, is_selectable=False, widths=None, contents=None):
        if widths is None:
            widths = []
        if contents is None:
            contents = []
        super(ColumnedLine, self).__init__(x, y, sum(widths), 1, is_selectable)

    def display(self, console):
        current_x = self.x
        func = display_text
        if self.focused:
            func = display_highlighted_text
        for idx, elem in enumerate(self.contents):
            func(console, elem, current_x, self.y)
            current_x += self.widths[idx]
