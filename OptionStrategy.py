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

    def value_at(self, price):
        if self.option_type == OptionType.Call:
            value = - self.premiun if price >= self.strike_price else (self.strike_price - self.premiun - price)
        elif self.option_type == OptionType.Put:
            value = - self.premiun if price <= self.strike_price else (price - self.strike_price - self.premiun)
        return value * self.operation.value
