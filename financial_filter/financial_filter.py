"""
Date    : 2018. 9. 2
Author  : Jiwoo Park
Desc    : Filtering firms by financial factor
"""
from datetime import datetime
from ksif import *
import pandas as pd
from collections import OrderedDict

pf = Portfolio()

querys = ['trading_volume_ratio > 0.02', 'market_cap > 100000']
query = " & ".join(querys)
SECTOR = 'krx_sector'
CODE = 'code'
E_P = 'e_p'

MIN_MKTCAP = 10000000
MIN_TRADING_VAL_RATIO = 0.01

QUERY = "(e_p > e_p_crt) & (mktcap > {}) & (trading_volume_ratio > {})".format(MIN_MKTCAP, MIN_TRADING_VAL_RATIO)
USECOLS = [CODE, SECTOR, E_P, 'e_p_crt']

def _apply_financial_criteria(period, criteria, firms):
    sampled_df = pf.loc[(pf.code.isin(firms)) & (pf.date > period[0]) & (pf.date < period[1])]
    sampled_df = pd.merge(sampled_df, criteria.to_frame(), left_on=SECTOR, right_index=True, suffixes=('', '_crt'))
    print(sampled_df[E_P] > sampled_df['e_p_crt'])
    df_after_query = sampled_df.query(QUERY)
    return df_after_query[USECOLS]


def _get_financial_criteria(period, factor=E_P):
    sampled_df = pf.loc[(pf.date > period[0]) & (pf.date < period[1])]
    return sampled_df.groupby(SECTOR)[factor].quantile(0.5)


def financial_filter(back_obj, query=None):
    """
    Filtering back object with query
    :param back_obj:
    :param query:
    :return:
    """
    for period, firms in back_obj.items():
        criteria = _get_financial_criteria(period)
        back_obj[period] = _apply_financial_criteria(period, criteria, firms)

    return back_obj


if __name__ == "__main__":
    flist1 = ['A000020', 'A001020', 'A000332', 'A000443']
    flist2 = ['A000220', 'A001120', 'A001332', 'A004443']
    test_obj = OrderedDict({
        (datetime(2011, 1, 1), datetime(2011, 4, 1)) : flist1,
        (datetime(2011, 4, 1), datetime(2011, 7, 1)) : flist2
    })

    for k, v in test_obj.items():
        print(_apply_financial_criteria(k, _get_financial_criteria(k), v))
