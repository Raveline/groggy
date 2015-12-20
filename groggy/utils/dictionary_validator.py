class NotProperTypeException(Exception):
    pass


class MissingPropertyException(Exception):
    pass


class DictionaryValidator(object):
    def __init__(self, validators):
        self.validators = validators

    def validate(self, dictionary):
        for validator in self.validators:
            validator(dictionary)


class MemberValidator(object):
    def __init__(self, name, clazz, mandatory=True):
        self.name = name
        self.clazz = clazz
        self.mandatory = mandatory

    def validate(self, dictionary):
        """
        >>> mv = MemberValidator('test', int)
        >>> mv.validate({'test_fail':3})
        >>> mv.validate({'test':False})
        >>> mv.validate({'test':0})
        True
        """
        if self.name in dictionary:
            value = dictionary[self.name]
            if not isinstance(value, self.clazz):
                raise NotProperTypeException('%s is not of class %s'
                                             % (dictionary, self.clazz))
        elif self.mandatory:
            raise MissingPropertyException('%s is missing property %s'
                                           % (dictionary, self.name))
