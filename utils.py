"""
    Utility gathered file
"""

import itertools
from collections import OrderedDict
from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def make_year_esg_column(from_year=2011, to_year=2019, esg=('E', 'S', 'G')):
    return list(itertools.chain.from_iterable([list(zip([x] * len(esg), esg)) \
                                               for x in list(range(from_year, to_year))] \
                                              ))


def backtesting(back_obj, price_file, save_file=None, benchmark='KOSPI'):
    """
    :param back_obj:
    :param price_file: Price File (Might be changed)
    :param save_file:
    :return:
    """
    back_obj = OrderedDict(sorted(back_obj.items(), key=lambda v: v))
    price_df = pd.read_csv(price_file, header=[0, 1], encoding='euc-kr', parse_dates=[0], index_col=0)

    price_val = []
    date_axis = []
    ret_val = []

    init_ret = 1
    for period, firms in back_obj.items():
        firms = [x for x in firms if x in price_df[period[0]:period[1]].columns]
        try:
            price_of_firm = price_df[period[0]:period[1]][firms]

            firm_rets = (price_of_firm / price_of_firm.iloc[0]).mean(axis=1) * init_ret - 1
            ret_val.extend(firm_rets)

            init_ret = firm_rets.iloc[-1] + 1

            avg_price = price_of_firm.apply(np.average, axis=1)
            price_val.extend(avg_price)

            date_axis.extend(price_df[period[0]:period[1]].index.values)

        except Exception as e:
            print(e)
    for x,y in zip(date_axis, ret_val):
        print(x, y)
    plt.plot(date_axis, ret_val, label="return")

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
        (datetime(2017, 10, 1), datetime(2018, 1, 1)): ['A000020', 'A000030'],
        (datetime(2018, 1, 1), datetime(2018, 6, 20)): ['A000020', 'A000030']
    }
    # backtesting(test_obj, './data/closed price.csv', save_file="test.png")
    d1 = {'a':[1, 2, 3], 'b':[3,4,5],'c':[10, 20, 25]}
    d2 = {'a':[1,3,5], 'b':[3,6,4], 'c':[10, 30, 20]}
    d1 = OrderedDict(sorted(d1.items(), key=lambda x: x[0]))
    d2 = OrderedDict(sorted(d2.items(), key=lambda x: x[0]))
    print(intersect_odict(d1, d2))

