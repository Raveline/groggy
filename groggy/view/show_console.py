import libtcodpy as tcod

def display(grid, console):
    for y in range(60):
        for x in range(80):
            tile = grid[y][x]
            char = tile_to_char(tile)
            back = tile_to_colors(tile)
            tcod.console_put_char_ex(console, x, y, char, tcod.white, back)


def print_selection(console, receiver):
    display_list = receiver.get_selected_tiles()
    characters = receiver.get_characters()
    for (char, (x, y, _)) in zip(characters, display_list):
        x_, y_ = receiver.global_to_local(x, y)
        print_char(console, char, x_, y_, tcod.yellow)


def display_text(console, text, x=0, y=0):
    tcod.console_print_ex(console, x, y,
                          tcod.BKGND_SET, tcod.LEFT, text)


def display_highlighted_text(console, text, x=0, y=0):
    previous_back = tcod.console_get_default_background(console)
    previous_fore = tcod.console_get_default_foreground(console)
    tcod.console_set_default_background(console, tcod.white)
    tcod.console_set_default_foreground(console, tcod.black)
    tcod.console_print_ex(console, x, y, tcod.BKGND_SET, tcod.LEFT, text)
    tcod.console_set_default_background(console, previous_back)
    tcod.console_set_default_foreground(console, previous_fore)


def print_char(console, char, x, y, foreground):
    tcod.console_put_char_ex(console, x, y, char, tcod.black, foreground)
