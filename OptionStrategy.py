from enum import Enum, IntEnum

import pandas as pd


class OptionType(Enum):
    Call = 0
    Put = 1


class OptionStatus(IntEnum):
    OTM = 0
    ITM = 1


class Position(IntEnum):
    Short = -1
    Long = 1


class OptionStrategy(object):
    def __init__(self):
        self.strategy_options = []

    def add(self, option):
        self.strategy_options.append(option)

    def evaluate_range(self, start, end, step=5):
        valuation = []
        for price in range(start, end + step, step):
            value = 0
            for option in self.strategy_options:
                value += option.value_at(price)
            valuation.append(value)
        return valuation


class OptionOperation(object):
    def __init__(self, position, premium, option_type, strike_price, multiplier=1, quantity=1, expiry=None):
        # Option properties
        self.option_type = option_type  # right
        self.strike_price = strike_price
        self.ConId = None
        self.underlying_asset = None  # symbol
        self.multiplier = multiplier
        self.expiry = expiry
        # Operation properties
        self.position = position
        self.premium = premium
        self.quantity = quantity

    @classmethod
    def from_contract_description(cls, contracts: pd.DataFrame, position, premium, option_type=None,
                                  strike_price=None, underlying_asset=None, expiry=None, quantity=1):
        queries = []

        if option_type is not None:
            if option_type == OptionType.Call:
                queries.append("Right=='C'")
            elif option_type == OptionType.Put:
                queries.append("Right=='P'")

        if strike_price is not None:
            queries.append("Strike==" + str(strike_price))

        if underlying_asset is not None:
            queries.append("Symbol=='{}'".format(underlying_asset))

        if expiry is not None:
            queries.append("Symbol=='{}'".format(expiry))

        query = None
        for q in queries:
            if query is None:
                query = q
            else:
                query = query + " and " + q

        selected_contract = contracts.query(query)
        if selected_contract.shape[0] > 1:
            raise ValueError()
        else:
            return cls.from_ConId(contracts, selected_contract.index[0], position, premium, quantity)

    @classmethod
    def from_ConId(cls, contracts: pd.DataFrame, ConID, position, premium, quantity=1):
        try:
            right = contracts.ix[ConID, 'Right']
        except KeyError:
            raise KeyError('The ConId does not exist in the contract JSON file.')

        if right == 'C':
            cls.option_type = OptionType.Call
        elif right == 'P':
            cls.option_type = OptionType.Put
        else:
            raise ValueError('The ConId is not an option.')

        cls.ConId = ConID
        cls.position = position
        cls.strike_price = contracts.ix[ConID, 'Strike']
        cls.premium = premium
        cls.underlying_asset = contracts.ix[ConID, 'Symbol']
        cls.expiry = str(contracts.ix[ConID, 'Expiry'])
        cls.multiplier = contracts.ix[ConID, 'Multiplier']
        return cls

    def value_at(self, price):
        if self.option_type == OptionType.Call:
            if price <= self.strike_price:
                value = - self.premium
            else:
                value = (price - self.strike_price) * self.multiplier - self.premium
        elif self.option_type == OptionType.Put:
            if price >= self.strike_price:
                value = - self.premium
            else:
                value = (self.strike_price - price) * self.multiplier - self.premium
        return value * self.position.value * self.quantity

    def intrinsic_value_at(self, price):
        return max(self.value_at(price), 0)

    def status_at(self, price):
        if ((self.option_type == OptionType.Call and price >= self.strike_price) or
                (self.option_type == OptionType.Put and price <= self.strike_price)):
            return OptionStatus.ITM
        else:
            return OptionStatus.OTM
