from typing import Union
from eda_report.univariate import CategoricalStats, DatetimeStats, NumericStats


UnivariateStat = Union[CategoricalStats, DatetimeStats, NumericStats]
