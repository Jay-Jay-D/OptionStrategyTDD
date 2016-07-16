import pytest
import requests

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

option_intrinsic_value_test_cases = (("comment", "position", "option_type", "price", "intrinsic_value"),
                                     [
                                         ('Call @150 intrinsic value at 170', 1, 0, 170, 20),
                                         ('Call @150 intrinsic value at 120', 1, 0, 120, 0),
                                         ('Put  @150 intrinsic value at 120', 1, 1, 120, 30),
                                         ('Put  @150 intrinsic value at 160', 1, 1, 160, 0)
                                     ])


@pytest.mark.parametrize(*option_valuation_test_cases)
def test_options_profit_loss_is_correctly_evaluated(comment, position, option_type, expected_values_formula):
    # Arrange
    actual_values = []
    expected_value = eval(expected_values_formula)
    position = Position(position)
    option_type = OptionType(option_type)
    option = OptionOperation(position=position, premium=10, option_type=option_type, strike_price=150)
    # Act
    for price in range(100, 200, 5):
        actual_values.append(option.profit_loss_at(price))
    # Assert
    assert expected_value == actual_values


@pytest.mark.parametrize(*option_status_test_cases)
def test_option_status_is_correctly_estimated(comment, position, option_type, price, correct_status):
    position = Position(position)
    option_type = OptionType(option_type)
    option = OptionOperation(position=position, premium=10, option_type=option_type, strike_price=150)

    assert option.status_at(price) == OptionStatus(correct_status)


@pytest.mark.parametrize(*option_intrinsic_value_test_cases)
def testing_intrinsic_value_is_correctly_estimated(comment, position, option_type, price, intrinsic_value):
    position = Position(position)
    option_type = OptionType(option_type)
    option = OptionOperation(position=position, premium=10, option_type=option_type, strike_price=150)

    assert option.intrinsic_value_at(price) == intrinsic_value


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


def test_OptionOperation_string_representation():
    # Arrange
    option = OptionOperation.from_ConId(contracts=df_contracts, ConID=198003244,
                                        position=Position.Long, premium=1, quantity=2)
    expected_str = '2 Long ES June-16 Call 2070 at 100'
    # Act
    actual_str = str(option)
    # Assert
    assert actual_str == expected_str


def test_when_many_OptionOperation_is_added_to_OptionStrategy_then_strategy_is_correctly_valued():
    # Arrange
    # Example source: http://www.theoptionsguide.com/iron-condor.aspx
    option_1 = OptionOperation(position=Position.Long, premium=50, option_type=OptionType.Put, strike_price=35,
                               multiplier=100, con_id=1)
    option_2 = OptionOperation(position=Position.Short, premium=100, option_type=OptionType.Put, strike_price=40,
                               multiplier=100, con_id=2)
    option_3 = OptionOperation(position=Position.Short, premium=100, option_type=OptionType.Call, strike_price=50,
                               multiplier=100, con_id=3)
    option_4 = OptionOperation(position=Position.Long, premium=50, option_type=OptionType.Call, strike_price=55,
                               multiplier=100, con_id=4)
    expected_strategy_valuation = [-400, -400, 100, 100, 100, -400, -400]
    # Act
    strategy = OptionStrategy()
    strategy.add(option_1)
    strategy.add(option_2)
    strategy.add(option_3)
    strategy.add(option_4)

    actual_strategy_valuation = []
    for price in range(30, 65, 5):
        actual_strategy_valuation.append(strategy.profit_loss_at(price))
    # Assert
    assert expected_strategy_valuation == actual_strategy_valuation


def test_when_an_OptionOperation_with_out_ConId_is_added_then_throw_warning():
    option_1 = OptionOperation(position=Position.Long, premium=50, option_type=OptionType.Put, strike_price=35,
                               multiplier=100)
    strategy = OptionStrategy()
    with pytest.warns(UserWarning):
        strategy.add(option_1)


def test_when_an_option_is_traded_two_times_then_OptionStrategy_adds_in_the_same_OptionOperation():
    # Arrange
    option_1 = OptionOperation.from_ConId(contracts=df_contracts, ConID=198003244, premium=1,
                                          position=Position.Long, quantity=2)
    option_2 = OptionOperation.from_ConId(contracts=df_contracts, ConID=198003244, premium=1,
                                          position=Position.Long, quantity=1)
    # Act
    strategy = OptionStrategy()
    strategy.add(option_1)
    strategy.add(option_2)
    # Assert
    assert strategy.get_option_from_ConId(198003244).quantity == 3
    assert strategy.get_option_from_ConId(198003244).position == Position.Long


def test_when_an_option_position_changes_from_short_to_long_OptionOperation_is_adjusted():
    # Arrange
    option_1 = OptionOperation.from_ConId(contracts=df_contracts, ConID=198003244, premium=1,
                                          position=Position.Long, quantity=1)
    option_2 = OptionOperation.from_ConId(contracts=df_contracts, ConID=198003244, premium=1,
                                          position=Position.Short, quantity=2)
    option_3 = OptionOperation.from_ConId(contracts=df_contracts, ConID=198003244, premium=1,
                                          position=Position.Long, quantity=4)
    # Act
    strategy = OptionStrategy()
    strategy.add(option_1)
    strategy.add(option_2)
    # Assert
    assert strategy.get_option_from_ConId(198003244).quantity == 1
    assert strategy.get_option_from_ConId(198003244).position == Position.Short
    strategy.add(option_3)
    assert strategy.get_option_from_ConId(198003244).quantity == 3
    assert strategy.get_option_from_ConId(198003244).position == Position.Long


def test_when_an_option_position_changes_from_long_to_short_OptionOperation_is_adjusted():
    # Arrange
    option_1 = OptionOperation.from_ConId(contracts=df_contracts, ConID=198003244, premium=1,
                                          position=Position.Short, quantity=1)
    option_2 = OptionOperation.from_ConId(contracts=df_contracts, ConID=198003244, premium=1,
                                          position=Position.Long, quantity=2)
    option_3 = OptionOperation.from_ConId(contracts=df_contracts, ConID=198003244, premium=1,
                                          position=Position.Short, quantity=5)
    # Act
    strategy = OptionStrategy()
    strategy.add(option_1)
    strategy.add(option_2)
    # Assert
    assert strategy.get_option_from_ConId(198003244).quantity == 1
    assert strategy.get_option_from_ConId(198003244).position == Position.Long
    strategy.add(option_3)
    assert strategy.get_option_from_ConId(198003244).quantity == 4
    assert strategy.get_option_from_ConId(198003244).position == Position.Short


def test_when_an_option_is_no_longer_taken_then_StrategyOptions_throws_KeyError_when_ConID_is_called():
    # Arrange
    option_1 = OptionOperation.from_ConId(contracts=df_contracts, ConID=198003244, premium=1,
                                          position=Position.Long, quantity=1)
    option_2 = OptionOperation.from_ConId(contracts=df_contracts, ConID=198003244, premium=1,
                                          position=Position.Short, quantity=1)
    # Act
    strategy = OptionStrategy()
    strategy.add(option_1)
    strategy.add(option_2)
    # Assert
    with pytest.raises(KeyError):
        strategy.get_option_from_ConId(198003244)


def test_strategy_string_representation():
    # Arrange
    con_ids = [198003954, 198003965]
    strategy = OptionStrategy()
    for con_id in con_ids:
        strategy.add(OptionOperation.from_ConId(df_contracts, ConID=con_id, position=Position.Long, premium=2))
    expexted_str = "1 Long ES June-16 Put 2010 at 100\n1 Long ES June-16 Put 2030 at 100"
    # Act
    actual_str = str(strategy)
    # Assert
    assert expexted_str == actual_str


def test_generate_strategy_strike_price_range():
    # Arrange
    con_ids = [198003954, 198003980]
    strategy = OptionStrategy()
    for con_id in con_ids:
        strategy.add(OptionOperation.from_ConId(df_contracts, ConID=con_id, position=Position.Long, premium=2))
    expected_range = [2010, 2070]
    # Act
    strategy_strike_range = strategy._get_strike_range()
    # Assert
    assert strategy_strike_range == expected_range


def test_generate_strategy_strike_price_range_when_there_is_one_option():
    # Arrange
    con_ids = [198003214]
    strategy = OptionStrategy()
    for con_id in con_ids:
        strategy.add(OptionOperation.from_ConId(df_contracts, ConID=con_id, position=Position.Long, premium=2))
    expected_range = [2000, 2000]
    # Act
    strategy_strike_range = strategy._get_strike_range()
    # Assert
    assert strategy_strike_range == expected_range


@pytest.mark.skip('Wait until I have some response about the Plotly folders.')
def test_send_strategy_to_plotly():
    # Arrange
    user = 'jjdambrosio'
    plotly_folder = 'OptionStrategy'
    options_plot_name = 'IronCondor_options'
    strategy_plot_name = 'IronCondor_strategy'
    # https://api.plot.ly/v2/files#lookup
    options_plot_url = 'https://api.plot.ly/v2/files/lookup?user={}&path=/{}/{}'.format(user, plotly_folder,
                                                                                        options_plot_name)
    strategy_plot_url = 'https://api.plot.ly/v2/files/lookup?user={}&path=/{}/{}'.format(user, plotly_folder,
                                                                                         strategy_plot_name)
    strategy = OptionStrategy('IronCondor')
    option_operations = {198003954: 1, 198003965: -1, 215521192: -1, 198003244: 1}
    for con_id in option_operations:
        option = OptionOperation.from_ConId(contracts=df_contracts, ConID=con_id,
                                            position=Position(option_operations[con_id]), premium=1)
        strategy.add(option)
    # Act
    strategy.plot(plotly_folder='OptionStrategy')
    r = requests.get(options_plot_url)
    assert r.ok == True
    r = requests.get(strategy_plot_url)
    assert r.ok == True
