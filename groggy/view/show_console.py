import libtcodpy as tcod
from tavern.world.objects.objects import Materials
from tavern.people.characters import Creature

materials_to_colors = {Materials.WOOD: tcod.darker_sepia}


def __get_color_scale(first, last, size):
    return tcod.color_gen_map([first, last], [0, size])


map_background_scale = __get_color_scale(tcod.dark_grey,
                                         tcod.darkest_grey, 200)
elvens_background_scale = __get_color_scale(tcod.lighter_green,
                                            tcod.darker_green, 20)
dwarvens_background_scale = __get_color_scale(tcod.lighter_yellow,
                                              tcod.darker_yellow, 20)
humans_background_scale = __get_color_scale(tcod.lighter_azure,
                                            tcod.darker_azure, 20)

race_to_scale = {Creature.ELVEN: elvens_background_scale,
                 Creature.DWARVES: dwarvens_background_scale,
                 Creature.HUMAN: humans_background_scale}


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


def display_creatures(console, creatures, func):
    """Display on the console a list of creatures whose coords will be
    put to local using the function given as parameter."""
    for c in creatures:
        x, y = func(c.x, c.y)
        if c.race == 0:
            color_front = tcod.white
        else:
            color_picker = race_to_scale[c.race]
            color_front = color_picker[c.level]
        color_back = tcod.console_get_char_background(console, x, y)
        to_display = c.char
        tcod.console_put_char_ex(console, x, y,
                                 to_display, color_front, color_back)


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


def tile_to_colors(tile):
    back = tcod.white
    if tile.wall:
        back = tcod.black
    if not tile.built:
        back = map_background_scale[int((tile.background + 1) * 100)]
    else:
        back = materials_to_colors.get(tile.material, back)
    return back


def tile_to_char(tile):
    if tile.wall and tile.tile_object is None:
        return '#'
    elif tile.tile_object is not None:
        return tile.tile_object.character
    else:
        return ' '
