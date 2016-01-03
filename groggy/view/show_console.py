import libtcodpy as tcod


def display_text(console, text, x=0, y=0):
    tcod.console_print_ex(console, x, y,
                          tcod.BKGND_SET, tcod.LEFT, text)


def display_highlighted_text(console, text, x=0, y=0, bg=tcod.white,
                             fg=tcod.black):
    previous_back = tcod.console_get_default_background(console)
    previous_fore = tcod.console_get_default_foreground(console)
    tcod.console_set_default_background(console, bg)
    tcod.console_set_default_foreground(console, fg)
    tcod.console_print_ex(console, x, y, tcod.BKGND_SET, tcod.LEFT, text)
    tcod.console_set_default_background(console, previous_back)
    tcod.console_set_default_foreground(console, previous_fore)


def print_char(console, char, x, y, foreground):
    tcod.console_put_char_ex(console, x, y, char, tcod.black, foreground)
