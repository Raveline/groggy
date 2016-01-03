class InvalidPathException(Exception):
    pass


def read_path_dict(dic, key):
    """Read a "path-like" dict, thus translating "sub.one.two" into
    dict.get("sub").get("one").get("two")
    """
    key_elements = key.split('.')
    current = dic
    if current is None:
        raise InvalidPathException('Received an empty dictionary when'
                                   'looking for key %s' % key)
    for elem in key_elements[:-1]:
        current = current.get(elem)
        if current is None:
            raise InvalidPathException(
                'Path was %s. Could not find key %s in dict %s.'
                % (key, elem, dic)
            )
    if key_elements is None:
        raise InvalidPathException(
            'Key is incorrect : %s. Started with %s to be found in %s'
            % (key_elements, key, dic)
        )
    return current[key_elements[-1]]
