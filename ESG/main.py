"""
    Title   : Project ESGing
    Author  : Jiwoo Park, Misun Gong
    Date    : 2018.6.11
"""
# TODO 
# 0. Configs
# 1. Classification
# 2. Weight
# 3. Score ( Upper 75% )
# 4. Financial Filter
# - 레버리지: 자기자본 대비 부채 비율(총부채/자기자본) < 2
# - 유동성: 당좌비율((유동자산-재고자산)/유동부채 > 1)
# - PER: 주가이익비율(주가/주당순이익) > 1
# - PBR: 주가순자산비율(주가/주당순자산) > 1
# 5. Add Momentum


import sys

sys.path.append("../")
import utils
import pandas as pd
from collections import OrderedDict
from datetime import datetime
try:
    from financial_filter.financial_filter import *
except:
    pass
from copy import deepcopy

esg_weight = {'S': 150, 'A+': 120, 'A': 100, 'B': 90, 'B+': 95, 'C': 80, 'D': 70, 'B이하': 80}
year_weight = {2011: 1, 2012: 2, 2013: 3, 2014: 4, 2015: 5, 2016: 6, 2017: 7}
sector_weight = {'경기소비재': 3, '소재': 3, '산업재': 3, 'IT': 3, '금융': 3, '의료': 3, '유틸리티': 4, '통신서비스': 4, '필수소비재': 3, '에너지': 3}
ESG_SCORE = '../data/ESG_Grade.csv'
df = pd.read_csv(ESG_SCORE)

sector_code = '../data/firm_sector_code.csv'
code_df = pd.read_csv(sector_code)
ESG = {'지배구조': 'G', '사회': 'S', '환경': 'E', 'ESG등급': 'ESG'}

price_file = '../data/Adjusted Price_daily.csv'
price_df = pd.read_csv(price_file, index_col=0, parse_dates=[0])

FIRM_NAME = '기업명'

def init(df):
    """ Make ESG DataFrame
    Args:
        param1 : dataframe to arrange
    Rets:
        No return
    """
    for col in df[['ESG등급', '지배구조', '사회', '환경']]:
        df['score_' + ESG[col]] = df[col].dropna().map(lambda x: esg_weight[x])


    df["기업코드"] = list(map(lambda x: "A" + ("000000" + str(x))[-6:], df["기업코드"]))
    df = df.join(code_df.set_index('Firm'), on="기업코드")

    df.sort_values('산업명-대분류', inplace=True)
    df['산업명-대분류'].fillna('Not Classified', inplace=True)
    df = df.set_index(['산업명-대분류', '기업명', '기업코드'])

    multi_level_column = utils.make_year_esg_column()
    multi_level_column = pd.MultiIndex.from_tuples(multi_level_column)

    grouped_df = pd.DataFrame(index=df.index, columns=multi_level_column)
    for col in grouped_df:
        grouped_df[col] = df.loc[df['평가년도'] == col[0]]['score_' + col[1]]
    grouped_df = grouped_df[~grouped_df.index.duplicated(keep='first')]

    ret_df = normalize_score(grouped_df)
    ret_df = summary_normal_esg(ret_df)
    return ret_df


def normalize_score(df):
    """ Normalize ESG score with Min Max scoring
    """
    grouped = df.groupby(df.index.get_level_values(0))
    return (df - grouped.min()) / (grouped.max() - grouped.min())


def summary_normal_esg(df, _from=2011, _to=2019):
    """ Calculate normal esg score with given period, sector, and dataframe
    Args:
        param1 : dataframe (DataFrame)
        param2 : sector (string)
        param3 : from period (int)
        param4 : to period (int)
    """
    period = list(range(_from, _to))
    for year in period:
        df[str(year) + '_score'] = df[year].sum(axis=1)
    return df


def get_firm_benchmark_by_sector(df, year, limit):
    """ Get benchmark firm list from dataframe based upon ESG score sector by sector
    """
    ret_firms = []
    df['yearly_score'] = df[year].sum(axis=1)
    for name, grp in df.groupby('산업명-대분류'):
        ret = grp.sort_values('yearly_score', ascending=False)
        ret_firms.extend(ret.head(limit).index.get_level_values(2).values.tolist())
    return ret_firms


def get_firm_benchmark(df, from_year, to_year, limit=30):
    """ Get benchmark firm list from dataframe based upon ESG score with all
    """
    ret = OrderedDict()
    periods = range(from_year, to_year)

    for idx, period in enumerate(periods):
        if idx == 0:
            continue

        start_date = periods[idx - 1]
        end_date = periods[idx]

        year_firms = get_firm_benchmark_by_sector(df, start_date, limit)
        ret[(datetime(start_date, 1, 1), datetime(end_date, 1, 1))] = ret.get((datetime(start_date, 1, 1), datetime(end_date, 1, 1)), [])
        ret[(datetime(start_date, 1, 1), datetime(end_date, 1, 1))].extend(year_firms)
    return ret


def get_esg_momentum_one_period(df, year):
    """ Helper function of ESG Momentum
    """
    return df[df[str(year - 1) + '_score'] <= df[str(year) + '_score']]


def get_esg_momentum(df, from_year, to_year, with_bench=False):
    """ Get firm based upon firm ESG momentum
    """
    ret = OrderedDict()
    periods = range(from_year, to_year)

    for idx, year in enumerate(periods):
        if idx == 0:
            continue
        year_esg_momentum_firm = get_esg_momentum_one_period(df, year).index.get_level_values('기업코드')
        ret[(datetime(year, 1, 1), datetime(year + 1, 1, 1))] = year_esg_momentum_firm.values.tolist()

    if with_bench:
        bench_dict = get_firm_benchmark(df, from_year+1, to_year+1)
        return utils.intersect_odict(ret, bench_dict)
    return ret

ESG_DF = init(df)

if __name__ == "__main__":
    maindf = init(df)

    bm_list = get_firm_benchmark(maindf, 2015, 2020)
    mm_list = get_esg_momentum(maindf, 2014, 2019, True)
    # mm_list2 = deepcopy(mm_list)
    # for k, v in mm_list.items():
    #     print(k)
    #     print(len(v))
    # filtered = f_filter(mm_list2)
    # utils.backtesting(bm_list, price_file, show_plot=True, benchmark='KOSPI', title="ESG Benchmark")
    utils.backtesting(mm_list, price_file, show_plot=True, benchmark='KOSPI', title="Momentum Applied")
    # utils.backtesting(filtered, price_file, show_plot=True, benchmark='KOSPI', title="Momentum Applied + financial filter")
