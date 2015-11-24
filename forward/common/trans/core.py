# -*- encoding: utf-8 -*-

__author__ = 'Mohanson'

BOOLEAN_STATES = {'1': True, 'yes': True, 'true': True, 'on': True,
                  '0': False, 'no': False, 'false': False, 'off': False}


def str_to_list(input, symbol=','):
    if symbol in input:
        return [i.strip() for i in input.split(symbol) if not (i.isspace() or not i)]
    else:
        return [input]


def str_to_boolean(input):
    return BOOLEAN_STATES.get(input.lower())


def str_to_dict(input, symbol=';'):
    d = {}
    for i in input.split(symbol):
        d[i.split('=', 1)[0]] = i.split('=', 1)[1]
    return d


def dict_to_str(input, symbol=';'):
    dstring = symbol.join(["%s=%s" % (k, v) for k, v in input.items()])
    return dstring