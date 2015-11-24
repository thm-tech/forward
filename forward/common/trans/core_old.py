# -*- encoding: utf-8 -*-

import re

__author__ = 'Mohanson'

BOOLEAN_STATES = {'1': True, 'yes': True, 'true': True, 'on': True,
                  '0': False, 'no': False, 'false': False, 'off': False}


class Error(Exception):
    pass


class MeanError(Error):
    def __init__(self, value, totype):
        self.value = value
        self.totype = totype

    def __str__(self):
        return '%s trans to %s failed!' % (self.value, self.totype)


def is_boolean(input):
    return True if input.lower() in BOOLEAN_STATES else False


def is_int(input):
    if input[0] == '-':
        input = input[1:]
    return True if input.isdigit() else False


def is_float(input):
    rule = re.compile('^-?\d+\.\d+$')
    return True if rule.match(input) else False


def to_boolean(input):
    if is_boolean(input):
        return BOOLEAN_STATES.get(input.lower())
    else:
        raise MeanError(input, 'Boolean')


def to_int(input):
    if is_int(input):
        return int(input)
    else:
        raise MeanError(input, 'Int')


def to_float(input):
    if is_float(input):
        return float(input)
    else:
        raise MeanError(input, 'Float')


def to_list(input, symbol=','):
    if input:
        if symbol in input:
            return [i.strip() for i in input.split(symbol) if not (i.isspace() or not i)]
        else:
            return [input]
    else:
        return []


def to_dict(input, symbol=';'):
    """
    input like "name=mohanson;age=21"
    """
    d = {}
    for i in input.split(symbol):
        d[i.split('=', 1)[0]] = i.split('=', 1)[1]
    return d


def dict_to_string(input, symbol=';'):
    dstring = symbol.join(["%s=%s" % (k, v) for k, v in input.items()])
    return dstring


def datetime_to_string(input):
    if input:
        return input.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return None