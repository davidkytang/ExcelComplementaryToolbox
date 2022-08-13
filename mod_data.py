
# ------------------------------------------------------ #
# Data Objects
# ------------------------------------------------------ #

import setting
import mod_function as func
import mod_style as sty
import mod_validate as vald

import math
import numbers
import numpy as np
import os
import pandas as pd
import time
import tkinter as tk
import tkinter.ttk as ttk


class DataSource:
    """
    This object mainly serves as a storage for the original data read from clipboard.
    1. import contents from clipboard into dataframe.
    2. limit number of rows and columns imported.
    3. the import action is triggered by keyboard event (Ctrl+V) within the data previewer.
    """
    def __init__(self, parent, name, limit, mem, log):
        super().__init__()
        self.parent = parent
        self.name = name            # value is either 'a' or 'b'
        self.limit = limit
        self.mem = mem              # link to Memory Consumption Reader
        self.log = log              # link to Message Window
        self.df = pd.DataFrame()

    def reload(self, df=None, maxRow=None, maxCol=None):
        self.read_clipboard(df)
        self.restrict(maxRow, maxCol)
        self.mem.refresh(self.name, self.df)

    def read_clipboard(self, df=None):
        self.parent.waiting_message('show')
        if df is None:
            self.df = pd.read_clipboard(header=None, index_col=False, low_memory=False, sep='\t', quoting=3)
        else:
            # load sample dataset instead of Clipboard -> for testing purpose
            self.df = df.copy()
        self.parent.waiting_message('hide')
        # add prefix ('a' or 'b') to all columns
        self.df.columns = self.df.columns.map(lambda c: self.name + str(c))

    def restrict(self, maxRow, maxCol):
        maxRow = self.limit['maxRow'] if maxRow is None else maxRow
        maxCol = self.limit['maxCol'] if maxCol is None else maxCol
        # accommodate header row -> maxRow + 1
        maxRow += 1
        # display in Message Window the rows and columns truncated
        if self.df.shape[0] > maxRow:
            self.log.add("【Data {0}】Row limit reached. Data {0} was truncated to {1:,} lines.".format(self.name.upper(), maxRow-1), tag='important')
        if self.df.shape[1] > maxCol:
            self.log.add("【Data {0}】Column limit reached. Data {0} was truncated to {1:,} columns.".format(self.name.upper(), maxCol), tag='important')
        # truncate the dataset
        self.df = self.df.iloc[0:maxRow, 0:maxCol]
        # check empty after truncate took place
        if len(self.df) <= 1:
            raise Exception('Clipboard has no data.', 'w')
        else:
            self.log.add("【Data {}】{:,} rows {:,} columns read.".format(self.name.upper(), self.df.shape[0]-1, self.df.shape[1]))


class DataWork:
    """
    1. create an interim dataset from data source
    2. apply different treatment to each column depending on its role, in general case:
       key columns      -> key fields for table join and group-by operations, should to be cleansed and reformatted
       value columns    -> used by arithmetic operations, should be converted into numbers
       other columns    -> no processing required
    """
    def __init__(self):
        self.df = pd.DataFrame()
        # create variables -> to keep original column info
        self.origCol = {
            'id': [],                       # sequential id of the original field, e.g. [0, 1, 2]
            'name': [],                     # original header (as in the 1st data row), e.g. [name, type, amount]
            'mapping': dict(),              # [id]->[name] mappings, e.g. {[0: 'name', 1: 'type', 2: 'amount']}
            'key': [],                      # columns categorized as key type (id + prefix), e.g. [a0, a1]
            'num': []                       # columns categorized as numeric type (id + prefix), e.g. [a3, a4]
        }
        # create variables -> to assign columns into groups according to their roles
        self.colGrp = {
            'key': [],                      # key columns for table join / group-by
            'joinKey': [],                  # key columns after reformatting (create new column)
            'value': [],                    # numeric columns for arithmetic calculation
            'adjValue': [],                 # numeric columns after number conversion (create new column)
            'others': [],                   # other columns
            'uid': [],                      # row id (new data)
            'err': []                       # conversion error indicator (created new column)
        }

    def copy_df(self, df):
        self.df = df.copy()
        self.get_col_map()                  # note: get column name mapping based on 1st row
        self.pop_first_row()                # discard 1st row

    def get_col_map(self):
        self.origCol['id'] = self.df.columns.astype(str).tolist()
        self.origCol['name'] = self.df.iloc[0, :].astype(str).tolist()
        for c1, c2 in zip(self.origCol['id'], self.origCol['name']):
            self.origCol['mapping'][c1] = c2

    def pop_first_row(self):
        self.df.drop(self.df.head(1).index, axis=0, inplace=True)

    def set_column_roles(self, option, command):
        df = self.df
        side = df.columns[0][0:1]                                                   # value either 'a' or 'b'

        num = []
        key = []

        # (1) determine numeric columns
        if 'optDeltaColumns' in option:
            num = [side + str(id) for id in option['optDeltaColumns']]
            # if param['optDeltaColumns'] > 0 and (len(df.columns) >= 2):
            #     # Numeric columns are the rightmost n columns
            #     num = df.columns[-1 * param['optDeltaColumns']:].tolist()
        elif 'optAggNum' in option:
            num = [side + str(id) for id in option['optAggNum']]

        # (2) determine key columns
        if 'optJoinColumns' in option:
            columnIDs = func.bisect_list(option['optJoinColumns'], side)            # e.g. [0, 1, 2, 4]
            key = [side + str(id) for id in columnIDs]                              # e.g. [a0, a1, a2, a4]
        else:
            # (iii) remaining columns will be determined according to default setting
            if setting.restColumn[command] == 'key':
                key = list(set(df.columns) - set(num))
            elif setting.restColumn[command] == 'other':
                key = []

        # validate total number of key/numeric columns -> stop proceed if columns are over limit
        vald.validate_column_type_limit(side, numColumns=num, keyColumns=key)

        self.origCol['num'] = num
        self.origCol['key'] = key

    def generate_interim_fields(self, option, errorTracker, log):
        """
        transform key fields and numeric fields, and insert transformed data as new columns
        """
        df = self.df
        side = df.columns[0][0:1]

        # initialize tracking of conversion error
        errorTracker.begin_tracking(df)

        # initialize variable for column group assignment
        self.colGrp = {key: [] for key in self.colGrp}

        # iterate over every column, transform data, and assign each column to a group
        oldColumns = df.columns
        for oldColumn in oldColumns:
            # transform key columns
            if oldColumn in self.origCol['key']:
                newColumn = oldColumn + '_join_key'
                # convert entire column to string type
                df[newColumn] = df[oldColumn].astype('string')
                # transform values according to user instruction
                if option.get('optIgnoreCase') == 1:
                    df[newColumn] = df[newColumn].str.lower()
                if option.get('optTrim') == 1:
                    df[newColumn] = df[newColumn].str.strip()
                if option.get('optTrimZero') == 1:
                    df[newColumn] = df[newColumn].str.lstrip('0')
                if option.get('optPartialMatch', np.NAN) >= 1:
                    df[newColumn] = df[newColumn].str[0: option['optPartialMatch']]
                # assign column group
                self.colGrp['key'].append(oldColumn)
                self.colGrp['joinKey'].append(newColumn)
            # transform numeric columns
            elif oldColumn in self.origCol['num']:
                newColumn = oldColumn + '_value'
                # convert data into numeric type with custom function
                df[newColumn] = df[oldColumn].apply(func.to_val, optWipeComma=option.get('optWipeComma'))
                errorTracker.update_tracking(df[oldColumn], self.origCol['mapping'][oldColumn])
                # assign column group
                self.colGrp['value'].append(oldColumn)
                self.colGrp['adjValue'].append(newColumn)
            else:
                self.colGrp['others'].append(oldColumn)
        # end of iteration

        # insert sequential id for every row
        df.insert(0, side + '.uid', range(1, len(df)+1))
        self.colGrp['uid'].append(side + '.uid')

        # insert conversion error count for every row
        if len(self.origCol['num']) > 0:
            df.insert(1, side + '.err', errorTracker.failCount)
            self.colGrp['err'].append(side + '.err')


class Parameters(dict):
    """
    common parameters are stored in a dictionary and shared on a global scope
    """
    def __init__(self):
        super(Parameters, self).__init__()

    def set(self, dic):
        self.clear()
        self.update(dic)


class ConversionErrorTracker:
    """
    trace error occurred during numeric conversion
    """
    def __init__(self):
        # create a list that stores total error count for every single row
        self.failCount = []
        # create a dict that stores the original value that caused conversion error
        self.failSample = dict()

    def begin_tracking(self, df):
        func.to_val.failStatus = []                             # clear previous result
        self.failCount = [0] * len(df)                          # initialize variable (list size must match dataframe height)

    def update_tracking(self, column: pd.Series, colName):
        booleans = func.to_val.failStatus                       # error status for every row (success=False; failure=True)
        func.to_val.failStatus = []                             # clean up
        # accumulate the error count from every column
        self.failCount = [x + int(y) for x, y in zip(self.failCount, booleans)]
        # identify and retrieve values that caused conversion error
        selection = column[booleans].tolist()                   # select values from rows with conversion error
        sample = func.get_unique_item(selection, n=5)           # draw n samples out of the selected values
        if len(sample) > 0:
            self.failSample[colName] = sample                   # append samples (after de-duplication)

    def collect_sample(self):
        sample = self.failSample
        self.failSample = dict()                                # clear sample after collection is done
        return sample
