from enum import Enum, IntEnum

import pandas as pd
from dateutil.parser import parse


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

    def profit_loos_at(self, price):
        value = 0
        for option in self.strategy_options:
            value += option.profit_loss_at(price)
        return value


class OptionOperation(object):
    # region Constructors
    def __init__(self, position, premium, option_type, strike_price, con_id=None, underlying_asset=None, multiplier=1,
                 quantity=1, expiry=None):
        # Option properties
        self.option_type = option_type  # right
        self.strike_price = strike_price
        self.ConId = con_id
        self.underlying_asset = underlying_asset
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
            option_type = OptionType.Call
        elif right == 'P':
            option_type = OptionType.Put
        else:
            raise ValueError('The ConId is not an option.')

        con_id = ConID
        strike_price = contracts.ix[ConID, 'Strike']
        underlying_asset = contracts.ix[ConID, 'Symbol']
        expiry = str(contracts.ix[ConID, 'Expiry'])
        multiplier = contracts.ix[ConID, 'Multiplier']
        premium = premium * quantity * multiplier
        return cls(position, premium, option_type, strike_price, con_id, underlying_asset, multiplier, quantity,
                   expiry)

    # endregion

    def __str__(self):
        expiry = parse(self.expiry).strftime('%B-%y')
        return ("{} {} {} {} {} {} at {}"
                .format(self.quantity, self.position.name, self.underlying_asset, expiry,
                        self.option_type.name, self.strike_price, self.premium))

    def profit_loss_at(self, price):
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

    def status_at(self, price):
        if ((self.option_type == OptionType.Call and price >= self.strike_price) or
                (self.option_type == OptionType.Put and price <= self.strike_price)):
            return OptionStatus.ITM
        else:
            return OptionStatus.OTM

    def intrinsic_value_at(self, price):
        if self.status_at(price) == OptionStatus.ITM:
            return abs(self.strike_price - price)
        else:
            return 0

    @property
    def is_Call(self):
        return self.option_type == OptionType.Call

    @property
    def is_Put(self):
        return self.option_type == OptionType.Put

    def is_ITM_at(self, price):
        return self.status_at(price)


if __name__ == '__main__':
    pass
