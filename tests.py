import pytest

from OptionStrategy import *

path_to_contracts_json = '/mnt/HDD200GB/Algorithmic Trading/OptionStrategy/testing_files/Contracts.json'
df_contracts = pd.read_json(path_to_contracts_json).dropna(axis=1, how='all').set_index('ConId')

option_valuation_test_cases = (("comment", "position", "option_type", "expected_values_formula"),
                               [
                                   ('Long a Call @150', 1, 0,
                                    '[-10 if price <= 150 else (price - 150 - 10) for price in range(100, 200, 5)]'),
                                   ('Short a Call @150', -1, 0,
                                    '[ 10 if price <= 150 else (150 - price + 10) for price in range(100, 200, 5)]'),
                                   ('Long a Put @150', 1, 1,
                                    '[-10 if price >= 150 else (150 - price - 10) for price in range(100, 200, 5)]'),
                                   ('Short a Put @150', -1, 1,
                                    '[ 10 if price >= 150 else (price - 150 + 10) for price in range(100, 200, 5)]'),
                               ])

option_status_test_cases = (("comment", "position", "option_type", "price", "correct_status"),
                            [
                                ('Call @150 ITM at 170', 1, 0, 170, 1),
                                ('Call @150 OTM at 120', 1, 0, 120, 0),
                                ('Put  @150 ITM at 120', 1, 1, 120, 1),
                                ('Put  @150 OTM at 160', 1, 1, 160, 0),

                            ])


@pytest.mark.parametrize(*option_valuation_test_cases)
def test_options_are_correctly_evaluated(comment, position, option_type, expected_values_formula):
    # Arrange
    actual_values = []
    expected_value = eval(expected_values_formula)
    position = Position(position)
    option_type = OptionType(option_type)
    option = OptionOperation(position=position, premium=10, option_type=option_type, strike_price=150)
    # Act
    for price in range(100, 200, 5):
        actual_values.append(option.value_at(price))
    # Assert
    assert expected_value == actual_values


@pytest.mark.parametrize(*option_status_test_cases)
def test_option_status_is_correctly_estimated(comment, position, option_type, price, correct_status):
    position = Position(position)
    option_type = OptionType(option_type)
    option = OptionOperation(position=position, premium=10, option_type=option_type, strike_price=150)

    assert option.status_at(price) == OptionStatus(correct_status)


def test_when_a_non_option_is_taken_using_ConId_then_throws_ValueError_exception():
    # Try to add a Future
    with pytest.raises(ValueError):
        option = OptionOperation.from_ConId(contracts=df_contracts, ConID=187532577,
                                            position=Position.Long, premium=10)


def test_when_ConId_is_not_present_in_Contract_JSON_then_throws_KeyError_exception():
    with pytest.raises(KeyError):
        option = OptionOperation.from_ConId(contracts=df_contracts, ConID=198003981,
                                            position=Position.Long, premium=10)


def test_when_an_option_is_taken_using_ConId_then_its_data_is_correctly_parsed():
    option = OptionOperation.from_ConId(contracts=df_contracts, ConID=198003980,
                                        position=Position.Long, premium=10)

    assert option.option_type == OptionType.Put
    assert option.strike_price == 2070
    assert option.ConId == 198003980
    assert option.underlying_asset == 'ES'
    assert option.expiry == '20160617'
    assert option.multiplier == 50


def test_when_option_is_not_instantiated_with_ConId_and_the_given_parameters_are_not_enough_to_pick_just_one_thrown_error():
    with pytest.raises(ValueError):
        option = OptionOperation.from_contract_description(df_contracts, position=Position.Long, premium=10,
                                                           option_type=OptionType.Put)


def test_when_option_is_correctly_instantiated_with_out_ConId_then_its_data_is_correctly_parsed():
    option = OptionOperation.from_contract_description(df_contracts, position=Position.Long, premium=10,
                                                       option_type=OptionType.Put, strike_price=2000)
    assert option.ConId == 198003948
    assert option.underlying_asset == 'ES'
    assert option.expiry == '20160617'
    assert option.multiplier == 50


def test_when_many_OptionOperation_is_added_to_OtpionStrategy_then_strategy_is_correctly_valued():
    # Arrange
    # Example source: http://www.theoptionsguide.com/iron-condor.aspx
    option_1 = OptionOperation(position=Position.Long, premium=50, option_type=OptionType.Put, strike_price=35,
                               multiplier=100)
    option_2 = OptionOperation(position=Position.Short, premium=100, option_type=OptionType.Put, strike_price=40,
                               multiplier=100)
    option_3 = OptionOperation(position=Position.Short, premium=100, option_type=OptionType.Call, strike_price=50,
                               multiplier=100)
    option_4 = OptionOperation(position=Position.Long, premium=50, option_type=OptionType.Call, strike_price=55,
                               multiplier=100)
    expected_strategy_valuation = [-400, -400, 100, 100, 100, -400, -400]

    # Act
    strategy = OptionStrategy()
    strategy.add(option_1)
    strategy.add(option_2)
    strategy.add(option_3)
    strategy.add(option_4)

    actual_strategy_valuation = strategy.evaluate_range(30, 60, 5)

    # Assert
    assert expected_strategy_valuation == actual_strategy_valuation

# class OptionStrategyTests(unittest.TestCase):
#     def test_when_buy_a_new_option_then_strategy_is_updated(self):
#         self.assertTrue(False)
#
#     def test_when_sell_a_new_option_then_strategy_is_updated(self):
#         self.assertTrue(False)
#
#     def test_when_an_option_was_sold_and_bought_then_strategy_has_no_position(self):
#         self.assertTrue(False)
#
#     def test_when_an_option_was_bought_and_sold_then_strategy_has_no_position(self):
#         self.assertTrue(False)
#
#     def test_when_an_option_is_sold_two_times_ia_a_row_thrown_exception(self):
#         self.assertTrue(False)
#
#     def test_when_an_option_is_bought_two_times_ia_a_row_thrown_exception(self):
#         self.assertTrue(False)
