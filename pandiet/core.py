#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This code is based on

https://www.kaggle.com/arjanso/reducing-dataframe-memory-size-by-65
https://www.kaggle.com/etremblay/fail-safe-parallel-memory-reduction/

import pandas as pd
from pandiet.core import Reducer

df = pd.read_csv('https://raw.githubusercontent.com/bundgus/pydata2parquet/master/Most-Recent-Cohorts-Scorecard-Elements.csv')
df_reduced = Reducer().reduce(df, verbose=False)
"""

import time, gc

# see https://github.com/fastai/fastbook/issues/382
from pandas.core.dtypes.common import (
    is_float_dtype,
    is_integer_dtype,
    is_object_dtype,
)

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from fastprogress import progress_bar

__all__ = ['Reducer']

def measure_time_mem(func):
    def wrapped_reduce(self, df, *args, **kwargs):
        # pre
        mem_usage_orig = df.memory_usage().sum() / self.memory_scale_factor
        start_time = time.time()
        # exec
        ret = func(self, df, *args, **kwargs)
        # post
        mem_usage_new = ret.memory_usage().sum() / self.memory_scale_factor
        end_time = time.time()
        print(f'reduced df from {mem_usage_orig:.4f} MB '
              f'to {mem_usage_new:.4f} MB '
              f'in {(end_time - start_time):.2f} seconds')
        gc.collect()
        return ret
    return wrapped_reduce


class Reducer:
    """
    Class that takes a dict of increasingly big numpy datatypes to transform
    the data of a pandas dataframe into, in order to save memory usage.
    """
    memory_scale_factor = 1024**2  # memory in MB

    def __init__(self, conv_table=None, use_categoricals=True, n_jobs=-1, use_null_int=True):
        """
        :param conv_table: dict with np.dtypes-strings as keys
        :param use_categoricals: Whether the new pandas dtype "Categoricals"
                shall be used
        :param n_jobs: Parallelization rate
        :param use_null_int: whether to use pd.Int*Dtype or pd.UInt*Dtype with NA value support or not
        """

        self.conversion_table = \
            conv_table or {'int': [np.int8, np.int16, np.int32, np.int64],
                           'uint': [np.uint8, np.uint16, np.uint32, np.uint64],
                           'float': [np.float32, ]}
        self.null_int = {   np.int8:  pd.Int8Dtype,
                            np.int16: pd.Int16Dtype,
                            np.int32: pd.Int32Dtype,
                            np.int64: pd.Int64Dtype,
                            np.uint8: pd.UInt8Dtype,
                            np.uint16:pd.UInt16Dtype,
                            np.uint32:pd.UInt32Dtype,
                            np.uint64:pd.UInt64Dtype}
        
        self.use_categoricals = use_categoricals
        self.n_jobs = n_jobs
        self.use_null_int = use_null_int

    def _type_candidates(self, k):
        for c in self.conversion_table[k]:
            i = np.iinfo(c) if 'int' in k else np.finfo(c)
            yield c, i

    @measure_time_mem
    def reduce(self, df, verbose=False):
        """Takes a dataframe and returns it with all data transformed to the
        smallest necessary types.

        :param df: pandas dataframe
        :param verbose: If True, outputs more information
        :return: pandas dataframe with reduced data types
        """
        ret_list = Parallel(n_jobs=self.n_jobs, max_nbytes=None)(progress_bar(list(delayed(self._reduce)
                                                (df[c], c, verbose) for c in df.columns)))

        del df
        gc.collect()
        return pd.concat(ret_list, axis=1)

    def _reduce(self, series, colname, verbose):
        try:
            isnull = False
            # skip NaNs
            if series.isnull().any():
                isnull = True
            # detect kind of type
            coltype = series.dtype
            if is_integer_dtype(coltype):
                conv_key = 'int' if series.min() < 0 else 'uint'
            elif is_float_dtype(coltype):
                conv_key = 'float'
                asint = series.fillna(0).astype(np.int64)
                result = (series - asint)
                result = np.abs(result.sum())
                if result < 0.01:
                    conv_key = 'int' if series.min() < 0 else 'uint'
            else:
                if is_object_dtype(coltype) and self.use_categoricals:
                    if len(series.unique()) / len(series) < 0.5:
                        if verbose: print(f'convert {colname} from {coltype} to categorical')
                        return series.astype('category')
                else:
                    if verbose: print(f'{colname} is {coltype} - Skip')
                    return series
            # find right candidate
            for cand, cand_info in self._type_candidates(conv_key):
                if series.max() <= cand_info.max and series.min() >= cand_info.min:
                    if verbose: print(f'convert {colname} from {coltype} to {cand}')
                    if isnull:
                        if self.use_null_int and conv_key != 'float':
                            return series.astype(self.null_int[cand]())
                        else:
                            return pd.to_numeric(series, downcast='float', errors='ignore')
                    else:
                        return series.astype(cand)

            # reaching this code is bad. Probably there are inf, or other high numbs
            print(f"WARNING: {colname} doesn't fit the grid with \nmax: {series.max()} and \nmin: {series.min()}")
            return pd.to_numeric(series, errors='ignore')
        except Exception as ex:
            print(f'Exception for {colname}: {ex}')
            import traceback
            traceback.print_exc()
            return series
