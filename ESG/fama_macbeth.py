"""
Author : Jiwoo Park
Date   : 2018. 11. 21
Desc   : "Regression of ESG universe on financial factors"
"""

from ksif import *
from ksif import columns
from sklearn.linear_model import Lasso, Ridge
from sklearn.model_selection import train_test_split

import matplotlib.pyplot as plt
import pandas as pd

pd.options.display.max_rows = 999


pf = Portfolio()

pf = pd.pivot_table(pf, values="beta_3m", index=["date"], columns=["code"])
stocks = pd.read_csv("./Stocks.csv").iloc[:, -1].dropna().values[1:]
pf = pf[stocks].dropna()
print(pf.mean())
"""
universe = pd.read_csv("./data/benchmark.csv", index_col=0)
sample_univ = universe.iloc[1].values

SECTION = [columns.VALUE_FACTORS,
           columns.GROWTH_FACTORS, columns.PROFIT_FACTORS,
           columns.SAFETY_FACTORS]
NAME = ["VALUE", "GROWTH", "PROFIT", "SAFETY"]

sectors = {
    "VALUE" : columns.VALUE_FACTORS,
    "GROWTH" : columns.GROWTH_FACTORS,
    "PROFIT" : columns.PROFIT_FACTORS,
    "SAFETY" : columns.SAFETY_FACTORS,
    "MOMENTUM": columns.MOMENTUM_FACTORS
}
pf = pf.loc[(pf.date > "2013-08-01") & (pf.code.isin(sample_univ))]

lassoReg = Lasso(alpha=0.0005)
ridge = Ridge(alpha=0.5)

column = SECTION[0]
regdf = pf.groupby('code').mean()
regdf = regdf.dropna()
reg = lassoReg

# fig, axes= plt.subplots(2, 1)

for idx, (name, col) in enumerate(sectors.items()):
    y = regdf['return_6'].values
    X = regdf[col].values
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=1)
    reg.fit(regdf[col].values, regdf['return_1'].values)
    coef = pd.Series(reg.coef_, col).sort_values()
    # axes[idx // 2, idx % 2].bar(coef.index, coef.values)
    # axes[idx // 2, idx % 2].set_title("{}".format(name))
    plt.bar(coef.index, coef.values)
    plt.title(name)
    print(coef)
    # for tick in axes[idx // 2, idx % 2].get_xticklabels():
    #     tick.set_rotation(45)
    print(reg.score(X_test, y_test))
    plt.show()
"""
