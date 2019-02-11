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

HISTORIC_PERIOD = timedelta(90)

FACTORS = columns.COMPANY_FACTORS

def _apply_financial_criteria(period, criteria, firms, query):
    sampled_df = pf.loc[(pf.code.isin(firms)) & (pf.date > period[0] - HISTORIC_PERIOD) & (pf.date < period[1] - HISTORIC_PERIOD)]
    sampled_df = pd.merge(sampled_df, criteria, left_on=FNSECTOR, right_index=True, suffixes=('', '_crt'))
    expectation_of_factor = sampled_df.groupby(CODE).mean()
    return expectation_of_factor.query(query).index.values.tolist()


def _get_financial_criteria(period, factor=E_P, crt=[0.0, 0.5]):
    pf.date = pd.to_datetime(pf.date)
    sampled_df = pf.loc[(pf.date > period[0] - HISTORIC_PERIOD) & (pf.date < period[1] - HISTORIC_PERIOD)]
    criteria = sampled_df.groupby(FNSECTOR)[factor].quantile(crt)
    criteria = criteria.unstack()
    # print(criteria)
    criteria = criteria.rename(columns={crt[0]: 'left_crt', crt[1]: 'right_crt'})
    return criteria


def f_filter(back_obj, factor=E_P, query=None, crt=[0.0, 0.5]):
    """
    Filtering back object with query
    :param back_obj:
    :param query:
    :return:
    """

    for period, firms in back_obj.items():
        criteria = _get_financial_criteria(period, factor, crt)
        back_obj[period] = _apply_financial_criteria(period, criteria, firms, query)

    return back_obj


if __name__ == "__main__":
    flist1 = ['A000020', 'A001020', 'A000332', 'A000443']
    flist2 = ['A000220', 'A001120', 'A001332', 'A004443']
    test_obj = OrderedDict({
        (datetime(2011, 1, 1), datetime(2011, 4, 1)) : flist1,
        (datetime(2011, 4, 1), datetime(2011, 7, 1)) : flist2
    })


    # print(financial_filter(test_obj))
    # print(f_filter(test_obj, query="e_p > left_crt & e_p < right_crt", crt=[0.0, 0.3]))
