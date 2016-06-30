import pandas as pd
from enum import Enum, IntEnum


class OptionType(Enum):
    Call = 0
    Put = 1


class Operation(IntEnum):
    Sell = -1
    Buy = 1


class OptionOperation(object):
    def __init__(self, option_type, operation, strike_price, premium):
        self.ConId = None
        self.option_type = option_type
        self.operation = operation
        self.strike_price = strike_price
        self.premium = premium

    @classmethod
    def from_ConId(cls, ConID, operation, premium, df_contracts):
        try:
            rigth = df_contracts.ix[ConID, 'Right']
        except KeyError:
            raise KeyError('The ConId does not exist in the contract JSON file.')

        if rigth == 'C':
            cls.option_type = OptionType.Call
        elif rigth == 'P':
            cls.option_type = OptionType.Put
        else:
            raise ValueError('The ConId is not an option.')

        cls.operation = operation
        cls.strike_price = df_contracts.ix[198003980, 'Strike']
        cls.premium = premium
        return cls


    def value_at(self, price):
        if self.option_type == OptionType.Call:
            value = - self.premium if price >= self.strike_price else (self.strike_price - self.premium - price)
        elif self.option_type == OptionType.Put:
            value = - self.premium if price <= self.strike_price else (price - self.strike_price - self.premium)
        return value * self.operation.value

