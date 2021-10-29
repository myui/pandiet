# pandiet
[![PyPI Latest Release](https://img.shields.io/pypi/v/pandiet.svg)](https://pypi.org/project/pandiet/)

A library to reduce memory consumption of Pandas Dataframes

# Installation

```sh
pip install pandiet
```

# Usage

```python
import pandas as pd
from pandiet import Reducer         # supported from v0.1.2
# from pandiet.core import Reducer

df = pd.read_csv('https://raw.githubusercontent.com/bundgus/pydata2parquet/master/Most-Recent-Cohorts-Scorecard-Elements.csv')
df_reduced = Reducer().reduce(df, verbose=True)
```
