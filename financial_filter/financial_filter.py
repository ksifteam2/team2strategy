"""
Date    : 2018. 9. 2
Author  : Jiwoo Park
Desc    : Filtering firms by financial factor
"""
from datetime import datetime, timedelta
from ksif import *
import pandas as pd
from collections import OrderedDict

pf = Portfolio()

SECTOR = 'krx_sector'
CODE = 'code'
FIRM = "Firm"
FNSECTOR = "산업명-대분류"
E_P = 'e_p'

sector_file = '../data/firm_sector_code.csv'
sector_df = pd.read_csv(sector_file)

pf = pf.merge(sector_df[[FIRM, FNSECTOR]], left_on="code", right_on="Firm")


QUERY = "(e_p < e_p_crt)"
USECOLS = [CODE, E_P, 'e_p_crt']

HISTORIC_PERIOD = timedelta(90)


def _apply_financial_criteria(period, criteria, firms, query=QUERY):
    sampled_df = pf.loc[(pf.code.isin(firms)) & (pf.date > period[0] - HISTORIC_PERIOD) & (pf.date < period[1] - HISTORIC_PERIOD)]
    sampled_df = pd.merge(sampled_df, criteria.to_frame(), left_on=FNSECTOR, right_index=True, suffixes=('', '_crt'))
    expectation_of_factor = sampled_df.groupby(CODE).mean()
    return expectation_of_factor.query(query).index.values.tolist()


def _get_financial_criteria(period, factor=E_P):
    sampled_df = pf.loc[(pf.date > period[0] - HISTORIC_PERIOD) & (pf.date < period[1] - HISTORIC_PERIOD)]
    criteria = sampled_df.groupby(FNSECTOR)[factor].quantile(0.5)
    return criteria


def f_filter(back_obj, query=None):
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

    # for k, v in test_obj.items():
    #     # print(_get_financial_criteria(k))
    #     print(_apply_financial_criteria(k, _get_financial_criteria(k), v))

    # print(financial_filter(test_obj))
    print(f_filter(test_obj))
