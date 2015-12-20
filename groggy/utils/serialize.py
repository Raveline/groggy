import struct
import json
from zlib import compress

# Temporary format for save format :
# Tavern
from tavern.people.characters import Patron
from tavern.people.employees import Publican, Employee
from tavern.people.tasks.tasks import Walking
from tavern.people.tasks.tasks_employees import (
    ServeMealTask, DeliverTask, CreateMeal, Serving,
    TakeOrder, PrepareFood)


class Serializer(object):
    def serialize(self, world):
        self.world = world
        serialized_dict = self.serialize_tavern(world)
        as_json = json.dumps(serialized_dict)
        compressed = compress(as_json)
        with open('save', 'w') as f:
            f.write(compressed)

    def serialize_tavern(self, tavern):
        return {
            'map': self.serialize_tavern_map(tavern.tavern_map),
            'store': self.serialize_tavern_store(tavern.store),
            'cash': struct.pack('Q', tavern.cash),
            'creatures': [self.serialize_creature(c)
                          for c in tavern.creatures]
        }

    def serialize_tavern_map(self, tavern_map):
        tiles = []
        for tz in tavern_map.tiles:
            current_z = []
            tiles.append(current_z)
            for ty in tz:
                current_y = []
                current_z.append(current_y)
                for tile in ty:
                    current_y.append(self.serialize_tile(tile))
        return {'width': tavern_map.width,
                'height': tavern_map.height,
                'tiles': tiles,
                'entry_points': tavern_map.entry_points,
                'used_services': tavern_map.used_services,
                'available_services': tavern_map.available_services,
                'employee_tasks': self.serialize_task_list(tavern_map.employee_tasks)}

    def serialize_task_list(self, task_list):
        to_return = []
        for func, content in task_list.iteritems():
            tasks = []
            for pos, task in content:
                tasks.append({'position': pos,
                              'task': self.serialize_task(task)})
            to_return.append({'nature': func,
                              'tasks': tasks})
        return to_return

    def serialize_tavern_store(self, store):
        return {'cells': store.cells,
                'store': store.store}

    def serialize_creature(self, creature):
        base_dict = {'character': creature.char,
                     'level': creature.level,
                     'x': creature.x,
                     'y': creature.y,
                     'z': creature.z,
                     'activity_list': [self.serialize_task(t)
                                       for t in creature.activity_list],
                     'race': creature.race,
                     'current_activity': self.serialize_task(
                         creature.current_activity)}
        if isinstance(creature, Patron):
            base_dict['type'] = 'Patron'
            base_dict['money'] = creature.money
            base_dict['has_a_drink'] = creature.has_a_drink
            base_dict['class'] = creature.creature_class
            base_dict['needs'] = self.serialize_needs(creature.needs)
        elif isinstance(creature, Employee):
            base_dict['functions'] = creature.functions
            base_dict['type'] = 'Employee'
        elif isinstance(creature, Publican):
            base_dict['type'] = 'Publican'
        return base_dict

    def serialize_needs(self, needs):
        return {'thirst': needs.thirst,
                'hunger': needs.hunger,
                'gamble': needs.gamble,
                'sleep': needs.sleep}

    def serialize_task(self, task):
        if not task:
            return 'None'
        base_dict = {'tick_time': task.tick_time,
                     'length': task.length,
                     'failed': task.failed,
                     'finished': task.finished,
                     'type': task.__class__.__name__}
        if isinstance(task, Walking):
            base_dict['dest'] = task.dest
            base_dict['tick_time'] = 0
        elif isinstance(task, Serving):
            base_dict['nature'] = task.nature
            base_dict['pos'] = task.pos
            base_dict['constant'] = task.constant
        elif isinstance(task, TakeOrder):
            base_dict['creature'] = self.creature_by_index(task.creature)
        elif isinstance(task, PrepareFood):
            base_dict['meal'] = task.meal
            base_dict['recipient'] = self.creature_by_index(task.creature)
        elif isinstance(task, CreateMeal)\
            or isinstance(task, DeliverTask)\
                or isinstance(task, ServeMealTask):
            base_dict['meal'] = task.meal
            base_dict['recipient'] = self.creature_by_index(task.recipient)
        return base_dict

    def serialize_object(self, obj):
        return {'name': obj.name,
                'blocks': obj.blocks,
                'character': obj.character,
                'function': obj.function}

    def serialize_tile(self, tile):
        tile_object = None
        if tile.tile_object:
            tile_object = self.serialize_object(tile.tile_object)
        return {'x': tile.x,
                'y': tile.y,
                'z': tile.z,
                'wall': tile.wall,
                'built': tile.built,
                'object': tile_object}
