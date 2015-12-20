from dictionary_validator import DictionaryValidator
from dictionary_validator import MemberValidator

state_tree = DictionaryValidator([MemberValidator('name', str, False),
                                  MemberValidator('action', int, False),
                                  MemberValidator('submenu', dict, True)])
