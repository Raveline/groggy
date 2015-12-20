"""
A simple informer console, used to display logs though this implementation
is rather simple and only provide one line.
"""
from groggy.view.show_console import display_text


class Informer(object):
    def __init__(self, console):
        self.console = console
        self.text = ''

    def receive(self, event):
        self.text = event.get('data')

    def display(self):
        display_text(self.console.console, self.text, 0, 1)

    def __repr__(self):
        return "Feedback"
