import numpy as np
from enum import Enum, IntEnum


class OptionType(Enum):
    Call = 0
    Put = 1


class Operation(IntEnum):
    Sell = -1
    Buy = 1


class OptionOperation(object):
    def __init__(self, option_type, operation, strike_price, premiun):
        self.option_type = option_type
        self.operation = operation
        self.strike_price = strike_price
        self.premiun = premiun


def value_call(option, price):
    value = - option.premiun if price >= option.strike_price else (option.strike_price - option.premiun - price)
    return value * option.operation.value


def value_put(option, price):
    value = - option.premiun if price <= option.strike_price else (price - option.strike_price - option.premiun)
    return value * option.operation.value


def value_option(option, price):
    value = np.nan
    if option.option_type == OptionType.Call:
        value = value_call(option, price)
    elif option.option_type == OptionType.Put:
        value = value_put(option, price)
    return value
