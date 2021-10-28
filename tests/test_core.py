import pandas as pd
from pandiet.core import Reducer

def test_reducer():
  df = pd.read_csv('https://raw.githubusercontent.com/bundgus/pydata2parquet/master/Most-Recent-Cohorts-Scorecard-Elements.csv')
  df_reduced = Reducer().reduce(df, verbose=False)
  assert df_reduced.memory_usage().sum() < df.memory_usage().sum()
