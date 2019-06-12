from collections import OrderedDict


def safeget(dct, *keys):
    for key in keys:
        try:
            dct = dct[key]
        except KeyError:
            return None
    return dct


def count_key(dct, key):
    val = dct.get(key)
    if val:
        dct[key] += 1
    else:
        dct[key] = 1
    return dct


def sort_dict_by_value(dct, reverse=True):
    return OrderedDict(sorted(dct.items(), key=lambda kv: kv[1], reverse=reverse))
