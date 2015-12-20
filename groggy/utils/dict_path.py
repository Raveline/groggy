def read_path_dict(dic, key):
    """Read a "path-like" dict, thus translating "sub.one.two" into
    dict.get("sub").get("one").get("two")
    """
    key = key.split('.')
    current = dic
    for elem in key[:-1]:
        current = dic.get(elem)
    return current[key[-1]]
