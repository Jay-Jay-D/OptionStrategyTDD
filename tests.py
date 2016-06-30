import pandas as pd
import unittest
import pytest

from OptionStrategy import *

path_to_contracts_json = '/mnt/HDD200GB/Algorithmic Trading/OptionStrategy/testing_files/Contracts.json'
df_contracts = pd.read_json(path_to_contracts_json).dropna(axis=1, how='all').set_index('ConId')

option_valuation_test_cases = (("comment", "operation", "option_type", "expected_values_formula"),
                               [
                                   ('Buy a Call @150', 1, 0,
                                    '[-10 if price >= 150 else (150 - price - 10) for price in range(100, 200, 5)]'),
                                   ('Sell a Call @150', -1, 0,
                                    '[ 10 if price >= 150 else (price - 150 + 10) for price in range(100, 200, 5)]'),
                                   ('Buy a Put @150', 1, 1,
                                    '[-10 if price <= 150 else (price - 150 - 10) for price in range(100, 200, 5)]'),
                                   ('Sell a Put @150', -1, 1,
                                    '[ 10 if price <= 150 else (150 - price + 10) for price in range(100, 200, 5)]'),
                               ])


@pytest.mark.parametrize(*option_valuation_test_cases)
def test_options_are_correctly_evaluated(comment, operation, option_type, expected_values_formula):
    # Arrange
    actual_values = []
    expected_value = eval(expected_values_formula)
    operation = Operation(operation)
    option_type = OptionType(option_type)
    option = OptionOperation(option_type, operation, strike_price=150, premium=10)
    # Act
    for price in range(100, 200, 5):
        actual_values.append(option.value_at(price))
    # Assert
    assert expected_value == actual_values


def test_when_a_non_option_is_taken_using_ConId_then_throws_ValueError_exception():
    # Try to add a Future
    with pytest.raises(ValueError):
        option = OptionOperation.from_ConId(ConID=187532577, df_contracts=df_contracts,
                                            operation=Operation.Buy, premium=10)


def test_when_ConId_is_not_present_in_Contract_JSON_then_throws_KeyError_exception():
    with pytest.raises(KeyError):
        option = OptionOperation.from_ConId(ConID=198003981, df_contracts=df_contracts,
                                            operation=Operation.Buy, premium=10)


def test_when_an_option_is_taken_using_ConId_then_its_data_is_correctly_parsed():
    option = OptionOperation.from_ConId(ConID=198003980, df_contracts=df_contracts, operation=Operation.Buy, premium=10)

    assert option.option_type == OptionType.Put
    assert option.strike_price == 2070


class OptionStrategyTests(unittest.TestCase):
    def test_when_buy_a_new_option_then_strategy_is_updated(self):
        self.assertTrue(False)

    def test_when_sell_a_new_option_then_strategy_is_updated(self):
        self.assertTrue(False)

    def test_when_an_option_was_sold_and_bought_then_strategy_has_no_position(self):
        self.assertTrue(False)

    def test_when_an_option_was_bought_and_sold_then_strategy_has_no_position(self):
        self.assertTrue(False)

    def test_when_an_option_is_sold_two_times_ia_a_row_thrown_exception(self):
        self.assertTrue(False)

    def test_when_an_option_is_bought_two_times_ia_a_row_thrown_exception(self):
        self.assertTrue(False)
