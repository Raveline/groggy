from groggy.events import bus
from groggy.ui.components import (
    StaticText, TextBloc, RowsComponent, DynamicText, RootComponent,
    Button, Ruler, NumberPicker, Line, ComponentException, ListComponent,
    CheckboxComponent, TextInput
)


class UnknownComponentException(Exception):
    pass


class InvalidComponentException(Exception):
    pass


class MissingContextException(Exception):
    pass


def build_menu(context, menu_description, root=False):
    """
    Build a menu state.

    param context: A dict with context on the dispay
    type context: Dict
    param menu_description: The dict containing the menu description
    type menu_description : Dict
    """
    children = None
    if root:
        _, _, w, _ = read_dimensions(context, menu_description)
        context['parent_width'] = w
    if menu_description.get('children'):
        children = []
        for elem in menu_description['children']:
            children += (build_menu(context, elem))
    return build_component(context, menu_description, children, root)


def build_text_bloc(component_description, x, y, w, h, selectable):
    content = component_description.get('content', '')
    return TextBloc(x, y, w, content)


def build_static_text(component_description, x, y, w, h, selectable):
    content = component_description.get('content', '')
    return StaticText(x, y, content)


def build_rows(component_description, x, y, w, h, selectable):
    content = component_description.get('content')
    return RowsComponent(x, y, w, h, contents=content, selectable=selectable)


def build_line(component_description, x, y, w, h, selectable):
    return Line(x, y, w)


def build_text_input(component_description, x, y, w, h, selectable):
    text = component_description.get('default', None)
    source = component_description.get('source', None)
    return TextInput(x, y, w, text, source)


def build_dynamic_text(component_description, x, y, w, h, selectable):
    is_centered = component_description.get('centered', False)
    source = component_description.get('source', None)
    return DynamicText(x, y, is_centered, source)


def build_button(component_description, x, y, w, h, selectable):
    text = component_description.get('text')
    event = component_description.get('event')
    event_type = component_description.get('event_type')
    if selectable is None:
        selectable = True
    return Button(x, y, w, text, [event], [event_type], selectable)


def build_ruler(component_description, x, y, w, h, selectable):
    if selectable is None:
        selectable = True
    source = component_description.get('source')
    return Ruler(x, y, w, source, selectable=selectable)


def build_number_picker(component_description, x, y, w, h, selectable):
    if selectable is None:
        selectable = True
    source = component_description.get('source')
    return NumberPicker(x, y, source, selectable=selectable)


def build_list(component_description, x, y, w, h, selectable):
    source = component_description.get('source')
    if not source:
        raise InvalidComponentException(
            'List components should have a source !'
        )
    if selectable is None:
        selectable = True
    return ListComponent(x, y, w, h, source, selectable)


def build_checkbox(component_description, x, y, w, h, selectable):
    checked = component_description.get('checked', False)
    label = component_description.get('label')
    if selectable is None:
        selectable = True
    return CheckboxComponent(x, y, w, label, selectable, checked)


def build_component(context, comp_desc, children=None, root=False):
    component = None

    x, y, w, h = read_dimensions(context, comp_desc)
    if comp_desc.get('eat_line', True):
        context['last_y'] = y

    selectable = comp_desc.get('selectable', None)
    component_type = comp_desc.get('type')

    if root:
        title = comp_desc.get('title', '')
        component = RootComponent(x, y, w, h, title, children)
        return component

    if component_type == 'Foreach':
        return build_foreach(comp_desc, x, y, w, h, context)
    component_builder = BUILDERS.get(component_type)
    if not component_builder:
        raise UnknownComponentException(
            'Component of type %s is unknown' % component_type
        )
    else:
        component = component_builder(comp_desc, x, y, w, h, selectable)

    if children is not None:
        component.set_children(children)
    return [component]


def build_foreach(component_description, x, y, w, h, context):
    source = component_description.get('source').split('.')
    iterable = context
    for path in source:
        try:
            iterable = iterable[path]
        except:
            raise MissingContextException('Could not find key %s in context %s'
                                          % (path, context))
    components = []
    do_desc = component_description.get('do')
    for elem in iterable:
        for to_do in do_desc:
            source_builder = to_do.get('source_builder')
            if source_builder:
                to_do['source'] = '.'.join([str(elem), source_builder])
            else:
                to_do['source'] = str(elem)
                if to_do.get('type') == 'StaticText':
                    to_do['content'] = to_do['source']
            components += build_component(context, to_do)
    return components


def read_dimensions(context, tree):
    template = tree.get('template')
    if template:
        if template.startswith('centered'):
            # centered template with a padding
            try:
                padding = int(template[len('centered '):])
                padding_percent = padding / 100.0
            except ValueError:
                raise ComponentException('Centered template must be followed'
                                         ' by an integer giving the padding'
                                         ' percentage. E.g., "centered 10"')
            width = context.get('width')
            height = context.get('height')
            x = int(width * padding_percent)
            y = int(height * padding_percent)
            w = width - (2 * x)
            h = height - (2 * y)
    else:
        x = tree.get('x')
        y = tree.get('y', context.get('last_y', 0) + 1)
        w = tree.get('w', 0)
        if isinstance(w, str):
            # Width has been given in percentage. Convert.
            percent = int(w[:w.find('%')]) / 100.0
            parent_width = context.get('parent_width')
            w = int(percent * parent_width)
        h = tree.get('h', 0)
    return x, y, w, h


def make_text_box(x, y, w, h, title, text):
    tbc = TextBloc(1, 1, w - 1, text)
    return RootComponent(x, y, w, h, title, [tbc])


def make_question_box(x, y, w, h, title, text, from_state, events_yes,
                      events_types):
    """
    Build a question box with a "YES / NO" choice.

    Args:
        x (int): x pos of the box
        y (int): y pos of the box
        w (int): width of the box
        h (int): height of the box
        title (str): Title for the box
        text (str): A little (or long !) text to present the offered choice
        from_state (State): Where this box comes from, to be able to cancel
        event_yes (list): A list of events to fire if yes is picked
        event_type (list): Type of the events to fire if yes is picked

    Returns:
        RootComponent: The root component for a new menu state
    """
    tbc = TextBloc(1, 1, w - 2, text)
    yes = Button(1, h - 3, w - 2, 'Yes', events_yes, events_types)
    no = Button(1, h - 2, w - 2, 'No', [from_state], [bus.PREVIOUS_STATE])
    return RootComponent(x, y, w, h, title, [tbc, yes, no])


def make_choice_box(x, y, w, title, text, from_state, choices_strs,
                    choices_events, events_types):
    """
    Build a choice box with several choices and a "cancel" one.

    Args:
        x (int): x pos of the box
        y (int): y pos of the box
        w (int): width of the box
        h (int): height of the box
        title (str): Title for the box
        text (str): A little (or long !) text to present the offered choice
        from_state (State): Where this box comes from, to be able to cancel
        choices_strs (list): A list of text to display for each choices
        choices_events (list): A list of list of events to fire for
                               each choices.
        event_type (list): Type of the events to fire for each
                           choices.

    Returns:
        RootComponent: The root component for a new menu state
    """
    tbc = TextBloc(1, 1, w - 2, text)
    # TODO : we will have to know the size of this text if it's longer than
    # 2 lines !
    components = [tbc]
    number_of_answers = len(choices_strs)
    for idx, (string, event) in enumerate(zip(choices_strs, choices_events)):
        button = Button(1, 3 + idx, w - 2, string, event, events_types)
        components.append(button)
    cancel = Button(1, 3 + number_of_answers + 1, w - 2,
                    'Cancel', [from_state], [bus.PREVIOUS_STATE])
    components.append(cancel)
    # Height is : 2 drawing box line + 1 text (see todo) + 1 line between
    # text and choices + 1 line for cancel + 1 before + 1 after.
    height = number_of_answers + 7
    return RootComponent(x, y, w, height, title, components)


BUILDERS = {'TextBloc': build_text_bloc,
            'StaticText': build_static_text,
            'Checkbox': build_checkbox,
            'List': build_list,
            'RowsComponent': build_rows,
            'Line': build_line,
            'DynamicText': build_dynamic_text,
            'Input': build_text_input,
            'Ruler': build_ruler,
            'Button': build_button,
            'NumberPicker': build_number_picker}
