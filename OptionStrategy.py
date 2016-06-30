import pandas as pd
from enum import Enum, IntEnum


class OptionType(Enum):
    Call = 0
    Put = 1


class OptionStatus(IntEnum):
    OTM = 0
    ITM = 1


class Operation(IntEnum):
    Sell = -1
    Buy = 1


class OptionOperation(object):
    def __init__(self, operation, premium, option_type, strike_price):
        self.operation = operation
        self.premium = premium
        self.option_type = option_type
        self.strike_price = strike_price
        self.ConId = None
        self.underlying_asset = None

    @classmethod
    def from_contract_description(cls, contracts: pd.DataFrame, operation, premium, option_type=None, strike_price=None,
                                  underlying_asset=None):
        cls.operation = operation
        cls.premium = premium
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
            return cls.from_ConId(contracts, selected_contract.index[0], option_type, premium)

    @classmethod
    def from_ConId(cls, contracts: pd.DataFrame, ConID, operation, premium):
        try:
            rigth = contracts.ix[ConID, 'Right']
        except KeyError:
            raise KeyError('The ConId does not exist in the contract JSON file.')

        if rigth == 'C':
            cls.option_type = OptionType.Call
        elif rigth == 'P':
            cls.option_type = OptionType.Put
        else:
            raise ValueError('The ConId is not an option.')

        cls.ConId = ConID
        cls.operation = operation
        cls.strike_price = contracts.ix[ConID, 'Strike']
        cls.premium = premium
        cls.underlying_asset = contracts.ix[ConID, 'Symbol']
        return cls

    def value_at(self, price):
        if self.option_type == OptionType.Call:
            value = - self.premium if price >= self.strike_price else (self.strike_price - self.premium - price)
        elif self.option_type == OptionType.Put:
            value = - self.premium if price <= self.strike_price else (price - self.strike_price - self.premium)
        return value * self.operation.value

    def status_at(self, price):
        if self.value_at(price) >= 0: return OptionStatus.ITM
        else: return OptionStatus.OTM
