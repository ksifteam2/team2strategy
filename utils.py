"""
    Utility gathered file
"""

import itertools
from collections import OrderedDict, Counter
from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys

sys.path.append("../")

INIT_BALANCE = 100000000
PRICE_FILE = "../data/weekly data.xlsx"
PRICE_DF = pd.read_excel(PRICE_FILE, index_col=0, skiprows=[1], parse_dates=[0])


class Pocket():
    def __init__(self, cash=0, stocks=Counter(), price_file=""):
        self.cash = cash
        self._stocks = stocks

    def balance(self, date):
        return self.cash + get_value_of_stocks(self.stocks, date)

    @property
    def stocks(self):
        return self._stocks

    @stocks.setter
    def stocks(self, stocks):
        self._stocks = stocks


def get_value_of_stocks(stocks, date, debug=False):
    if not type(stocks) is Counter:
        raise TypeError("Stocks should be type of Counter")
    price = PRICE_DF.iloc[PRICE_DF.index.get_loc(date, method='pad')]
    price = price.loc[list(stocks.keys())]
    cnt = pd.Series(dict(stocks))
    total_value = (price * cnt).dropna().sum()

    if debug:
        print(price)
        print(cnt)
    return total_value


def validation(order_items, date):
    """
    Validate only stocks whose price of the date.
    :param order_items:
    :param date:
    :return:
    """
    price = PRICE_DF.iloc[PRICE_DF.index.get_loc(date, method='pad')]
    return price.loc[order_items].dropna().index.values.tolist()

def order(pocket, order_items, date):
    order_items = validation(order_items, date)
    if type(order_items) is not Counter:
        print(order_items)
        print(pocket.balance(date))
        order_items = equal_price_counter(order_items, date, pocket.balance(date))
    print(order_items)
    pocket.cash += get_value_of_stocks(pocket.stocks, date)
    print("After Sell Cash : {}".format(pocket.cash))
    pocket.stocks = order_items
    pocket.cash -= get_value_of_stocks(order_items, date)
    print("After Buy Cash : {}".format(pocket.cash))

    print("\n"
          "Remaining stocks :{}\n"
          "Remaining Cash : {}\n"
          "Total Balance :{}".format(pocket.stocks, pocket.cash, pocket.balance(date)))


# def order_to_target(pocket, order_items, date):
#     if type(order_items) is not Counter:
#         order_items = convert_to_counter(order_items, date, pocket.balance(date))
#     pass


def equal_price_counter(ordered_items, date, balance):
    begin_price_of_items = PRICE_DF.iloc[PRICE_DF.index.get_loc(date, method='pad')][ordered_items]
    per_firm_value = balance // len(ordered_items)
    equal_balance = per_firm_value // begin_price_of_items
    equal_balance = equal_balance.dropna()
    return Counter(equal_balance.to_dict())


def make_year_esg_column(from_year=2011, to_year=2019, esg=('E', 'S', 'G')):
    return list(itertools.chain.from_iterable([list(zip([x] * len(esg), esg)) \
                                               for x in list(range(from_year, to_year))] \
                                              ))


def backtesting(back_obj, price_file, show_plot=False, save_file=None, benchmark='KOSPI', title="None", balance=INIT_BALANCE):
    """
    TODO : 1. 실제로 사는 것처럼 금액 바탕으로 계산하기. (not 단순산술평균), 2. Loss cut
    :param back_obj:
    :param price_file: Price File (Might be changed)
    :param save_file:
    :return:
    """
    back_obj = OrderedDict(sorted(back_obj.items(), key=lambda v: v))
    price_df = PRICE_DF
    init_date = list(back_obj.keys())[0][0]

    price_val = [INIT_BALANCE]
    date_axis = [init_date]

    pkt = Pocket(INIT_BALANCE)
    for period, firms in back_obj.items():
        print(period)
        firms = [x for x in firms if x in price_df[period[0]:period[1]].columns]

        sub_periods = PRICE_DF[period[0]:period[1]].index.values

        order(pkt, firms, period[0])            # This is ordering by equal trading has todo fix after!

        val_list = [pkt.balance(t) for t in sub_periods]

        price_val.extend(val_list)
        date_axis.extend(PRICE_DF[period[0]:period[1]].index.values)

    price_val = list(map(lambda x: (x / INIT_BALANCE) - 1, price_val))

    if show_plot:
        plt.title(title)
        plt.plot(date_axis, price_val, label="return")

        if save_file:
            plt.savefig(save_file)

        if benchmark == 'KOSPI':
            bench_df = pd.read_csv("./data/kospi_kosdaq_Equal.csv", index_col=0, parse_dates=[0])
            bench_df = bench_df[date_axis[0] : date_axis[-1]]
            bench_val = bench_df / bench_df.iloc[0] - 1
            plt.plot(bench_val, label="benchmark")

            # PLOT KOSPI plt.plot()
        plt.legend()
        plt.show()

def intersect_odict(fdict, tdict):
    assert fdict.keys() == tdict.keys(), "Two dict have to have same keys"

    for k, v in fdict.items():
        intersect = set(v).intersection(set(tdict[k]))
        fdict[k] = list(intersect)

    return fdict

if __name__ == "__main__":
    test_obj = {
        (datetime(2017, 10, 1), datetime(2018, 1, 1)): ['A000100','A000110'],
        (datetime(2018, 1, 1), datetime(2018, 6, 20)): ['A000110']
    }
    backtesting(test_obj, './data/closed price.csv', save_file="test.png", show_plot=False)
    pass
