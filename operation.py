
import setting
import mod_function as func
import mod_style as sty

import numpy as np
import pandas as pd
import sys
import tkinter as tk
import tkinter.ttk as ttk


def run_operation(parent, command, DataSourceA, DataSourceB, DataWorkA, DataWorkB, option):

    args = {'parent': parent,
            'DataSourceA': DataSourceA, 'DataSourceB': DataSourceB, 'DataWorkA': DataWorkA, 'DataWorkB': DataWorkB,
            'option': option}

    # the <try> block ensures those minor exceptions would not be muted by tkinter
    try:
        if command == 'run_aggregation':
            recordCount, popUpWindow = run_aggregation(**args)
        elif command == 'run_compare_value':
            recordCount, popUpWindow = run_compare_value(**args)
        elif command == 'run_exception':
            recordCount, popUpWindow = run_exception(**args)
        elif command == 'run_connection':
            recordCount, popUpWindow = run_connection(**args)
        elif command == 'run_join':
            recordCount, popUpWindow = run_join(**args)
        elif command == 'run_profiling':
            recordCount, popUpWindow = run_profiling(**args)
        return [recordCount, popUpWindow]
    except Exception as e:
        raise Exception(e)


def run_exception(parent, DataSourceA, DataSourceB, DataWorkA, DataWorkB, option):

    df1 = DataWorkA.df
    df2 = DataWorkB.df

    popUpWindow = 1

    # join dataset A and B
    df3 = pd.merge(df1, df2,
                   how='outer', sort=False,
                   left_on=DataWorkA.colGrp['joinKey'],
                   right_on=DataWorkB.colGrp['joinKey'],
                   indicator='which')

    # get result of join
    columnList_a = DataWorkA.colGrp['key']
    columnList_b = DataWorkB.colGrp['key']
    if option['optReturnUnique'] == 1:
        # get all unmatched items without duplication
        df4 = (df3
               .loc[df3['which'] == 'left_only', ['which'] + columnList_a]
               .drop_duplicates(subset=columnList_a)
               )
        df5 = (df3
               .loc[df3['which'] == 'right_only', ['which'] + columnList_b]
               .drop_duplicates(subset=columnList_b)
               )
    else:
        # get all unmatched items with duplication, and show original row id
        df4 = (df3
               .loc[df3['which'] == 'left_only', ['which', 'a.uid'] + columnList_a]
               .sort_values('a.uid')
               )
        df5 = (df3
               .loc[df3['which'] == 'right_only', ['which', 'b.uid'] + columnList_b]
               .sort_values('b.uid')
               )

    # create dual-named header
    header_1 = func.map_header(df4, {**DataWorkA.origCol['mapping'], **setting.customHeader})
    header_2 = func.map_header(df5, {**DataWorkB.origCol['mapping'], **setting.customHeader})
    header_f = func.dual_name_header(header_1, header_2)

    # align column names before concat
    df5.rename(columns=dict(zip(df5.columns, df4.columns)), inplace=True)    # overwritten by column names of df4

    # reformat header as dataframe
    header_f = pd.DataFrame([header_f], columns=df5.columns)

    # concat header and rows
    recordCount = len(df4) + len(df5)
    df6 = pd.concat([header_f, df4, df5], axis=0)

    # text replacement
    df6['which'] = df6['which'].map(lambda x: {'left_only': 'A not in B', 'right_only': 'B not in A'}.get(x, x))

    # copy result to clipboard
    df6.to_clipboard(excel=True, sep=None, index=False, header=False)

    return [recordCount, popUpWindow]


def run_compare_value(parent, DataSourceA, DataSourceB, DataWorkA, DataWorkB, option):

    df1 = DataWorkA.df
    df2 = DataWorkB.df

    popUpWindow = 1

    # aggregate all records in both datasets before comparison
    for side in ['a', 'b']:
        DataWork = DataWorkA if (side == 'a') else DataWorkB
        df = DataWorkA.df if (side == 'a') else DataWorkB.df
        # fill na with empty string (pandas groupby cannot handle missing value)
        df[DataWork.colGrp['joinKey']] = df[DataWork.colGrp['joinKey']].fillna('')
        # insert new numeric field to count no. of aggregated rows
        df[side + '.entry'] = 1
        agg_1 = {c: min for c in DataWork.colGrp['uid']}        # min(uid)      -> keep smallest id
        # apply aggregation function first() on text, e.g. 'APPLE', 'apple' (2 rows) will output 'APPLE' (1 row)
        agg_2 = {c: 'first' for c in DataWork.colGrp['key']}    # first(key)    -> retain first item only
        agg_3 = {c: sum for c in DataWork.colGrp['adjValue']}   # sum(adjValue) -> sum values
        agg_4 = {c: sum for c in DataWork.colGrp['err']}        # sum(x)        -> sum no. of error occurrence
        agg_5 = {side + '.entry': 'count'}                      # count(x)      -> count no. of aggregated rows
        agg_method = {**agg_1, **agg_2, **agg_3, **agg_4, **agg_5}
        # group by matching keys
        if side == 'a':
            df1 = df.groupby(DataWork.colGrp['joinKey']).agg(agg_method).reset_index()
        elif side == 'b':
            df2 = df.groupby(DataWork.colGrp['joinKey']).agg(agg_method).reset_index()

    # join dataset A and B
    df3 = pd.merge(df1, df2,
                   how='outer', sort=False,
                   left_on=DataWorkA.colGrp['joinKey'],
                   right_on=DataWorkB.colGrp['joinKey'],
                   indicator=False)

    # select wanted columns from result of join
    columnList = ['a.entry', 'b.entry'] + \
                 DataWorkA.colGrp['uid'] + DataWorkB.colGrp['uid'] + \
                 DataWorkA.colGrp['err'] + DataWorkB.colGrp['err'] + \
                 DataWorkA.colGrp['key'] + DataWorkB.colGrp['key'] + \
                 DataWorkA.colGrp['adjValue'] + DataWorkB.colGrp['adjValue']

    # extract columns into a new dataframe, and sort rows based on original sequence
    df4 = df3.loc[:, columnList].sort_values(['a.uid', 'b.uid'])
    df4 = df4.drop(columns=['a.uid', 'b.uid'])

    # coalesce key fields (a_*, b_*) and discard b_* afterwards
    for a, b in zip(DataWorkA.colGrp['key'], DataWorkB.colGrp['key']):
        df4[a] = df4[a].fillna(df4[b])
    df4 = df4.drop(columns=DataWorkB.colGrp['key'])

    # create indicator showing whether a row was aggregated
    df4.insert(0, 'dup', df4[['a.entry', 'b.entry']].
               apply(lambda x: 'Y' if (x['a.entry'] > 1 or x['b.entry'] > 1) else 'N', axis=1))
    df4 = df4.drop(columns=['a.entry', 'b.entry'])

    # create column showing the count of conversion errors
    df4.insert(1, 'err', df4[['a.err', 'b.err']].sum(axis=1))
    df4 = df4.drop(columns=['a.err', 'b.err'])

    # create comparison columns
    marking = dict()                # column markings (alphabetic letters)
    keep_col = []                   # for storing the names of columns to be kept in final result
    add_total = []                  # for storing the names of columns with control total
    # alphabetic letter list (A-Z, a-z) excluding symbols in between
    letters = [chr(letter) for letter in set(range(65, 123)).symmetric_difference(range(91, 97))]
    order = 0
    # compute delta figures
    for a, b in zip(DataWorkA.colGrp['adjValue'], DataWorkB.colGrp['adjValue']):
        # markings
        char = {'A': letters[order], 'B': letters[order + 1], 'C': letters[order + 2]}

        # amount to subtract from
        value_A = a
        marking[value_A] = '(' + char['A'] + ') '
        keep_col.append(value_A)
        add_total.append(value_A)

        # amount to be subtracted
        value_B = b
        marking[value_B] = '(' + char['B'] + ') '
        keep_col.append(value_B)
        add_total.append(value_B)

        # insert comparison (delta amount)
        colDelta = '({C}) = ({B}) - ({A})'.format(C=char['C'], B=char['B'], A=char['A'])  # column name
        df4[colDelta] = (df4[value_B]
                         .sub(df4[value_A], fill_value=0)                       # NaN treated as 0 in subtraction
                         .fillna(0)
                         )
        keep_col.append(colDelta)
        add_total.append(colDelta)

        # insert comparison (% change of delta)
        if option['optPercentChg'] == 1:
            colPercentChg = '({C}) / ({A})'.format(C=char['C'], A=char['A'])    # column name
            df4[colPercentChg] = (df4[colDelta]
                                  .div(df4[value_A].replace(0, np.NAN))         # prevent divide by 0
                                  .map('{:,.2%}'.format)                        # apply percentage format (type: str)
                                  .replace('nan%', 'N/A')                       # translation
                                  )
            keep_col.append(colPercentChg)

        # insert comparison (% change to total delta)
        if option['optChgVsTotal'] == 1:
            colChgvsTotal = '({C}) / sum({C})'.format(C=char['C'])              # column name
            sumDelta = df4[colDelta].sum()
            df4[colChgvsTotal] = (df4[colDelta]
                                  .div(sumDelta if abs(sumDelta) > 0 else np.NAN)
                                  .map('{:,.2%}'.format)                        # apply percentage format (type: str)
                                  .replace('nan%', 'N/A')                       # translation
                                  )
            keep_col.append(colChgvsTotal)

        # move ahead the letter list
        order += 3

    # make header
    header = func.map_header(df4, {**DataWorkA.origCol['mapping'], **DataWorkB.origCol['mapping'], **setting.customHeader})
    # add marking to header
    header = [marking.get(c, '') + h for h, c in zip(header, df4.columns)]
    # reformat header as dataframe
    header_f = pd.DataFrame([header], columns=df4.columns)

    # insert control total (optional)
    ctrl_total = pd.DataFrame()
    if option['optControlTotal'] == 1:
        ctrl_total = pd.DataFrame(
            [[''] * len(df4.columns)] * 2, columns=df4.columns  # blank dataframe [no. of columns] x [2 rows]
        )
        ctrl_total.iloc[-1, 0] = 'Control Total'
        for c in add_total:
            cid = df4.columns.get_loc(c)                        # get column position by name
            ctrl_total.iloc[-1, cid] = df4[c].sum()             # add column total at the bottom row

    # merge header, rows, and footer
    recordCount = len(df4)
    df4 = pd.concat([header_f, df4, ctrl_total], axis=0)

    # re-arrange column position
    columnList = ['dup', 'err'] + \
                 DataWorkA.colGrp['key'] + \
                 keep_col
    df4 = df4[columnList]

    # copy result to clipboard
    df4.to_clipboard(excel=True, sep=None, index=False, header=False)

    return [recordCount, popUpWindow]


def run_join(parent, DataSourceA, DataSourceB, DataWorkA, DataWorkB, option):

    df1 = DataWorkA.df
    df2 = DataWorkB.df

    popUpWindow = 1

    # get matching keys
    columnIDs = func.bisect_list(option['optJoinColumns'], 'a')
    joinKeyA = ['a' + str(cid) + '_join_key' for cid in columnIDs]

    columnIDs = func.bisect_list(option['optJoinColumns'], 'b')
    joinKeyB = ['b' + str(cid) + '_join_key' for cid in columnIDs]

    # join dataset A and B
    df3 = pd.merge(df1, df2,
                   how='left', sort=False,
                   left_on=joinKeyA,
                   right_on=joinKeyB,
                   indicator=False)

    # insert a new column to indicate multiple matches
    df3.insert(0, '*multiple match', df3['a.uid'].duplicated(keep=False).map({False: '', True: 'Y'}))

    # fetch only the first match (if user specified vLookup mode)
    if option['optJoinMode'] == 1:
        df3 = df3[~df3['a.uid'].duplicated(keep='first')]

    # select columns to output
    columnList = ['*multiple match'] + DataWorkA.origCol['id'] + DataWorkB.origCol['id']
    # disregard key columns in dataset B (key columns in dataset A contains the same values)
    columnList = [c for c in columnList if c not in DataWorkB.colGrp['key']]
    df3 = df3[columnList]

    # make header
    header = func.map_header(df3,
                             {**DataWorkA.origCol['mapping'], **DataWorkB.origCol['mapping'], **setting.customHeader})

    # reformat column header into DataFrame
    header = pd.DataFrame([header], columns=df3.columns)

    # merge header and rows
    recordCount = len(df3)
    df4 = pd.concat([header, df3], axis=0)

    # copy result to clipboard
    df4.to_clipboard(excel=True, sep=None, index=False, header=False)

    return [recordCount, popUpWindow]


def run_aggregation(parent, DataSourceA, DataSourceB, DataWorkA, DataWorkB, option):

    popUpWindow = 1

    # use the dataset selected by user
    if option['optDataSet'] == 0:
        side = 'a'
    else:
        side = 'b'
    DataWork = DataWorkA if (side == 'a') else DataWorkB
    df = DataWork.df

    df1 = df.copy()

    # user option - align letter case
    if option['optIgnoreCase'] == 1:
        func.df_align_case(df1, columns=DataWork.colGrp['others'])

    # user option - custom separator
    separator = option['optSeparator'] + ' '

    # fill n/a in advance because (1) groupby ignores record with n/a (2) text aggregation function cannot handle n/a
    df1[DataWork.colGrp['others']] = df1[DataWork.colGrp['others']].fillna('')

    # columns to apply text aggregation
    colText = [(side + str(idx)) for idx in option['optAggText']]
    # columns that will not apply aggregation
    colGroupBy = list(set(DataWork.colGrp['others']) - set(colText))

    # insert new numeric field to count no. of aggregated rows
    df1[side + '.entry'] = 1
    agg_1 = {side + '.entry': 'count'}                                  # count(x)      -> count no. of aggregated rows
    agg_2 = {c: min for c in DataWork.colGrp['uid']}                    # min(uid)      -> keep smallest id
    agg_3 = {c: sum for c in DataWork.colGrp['err']}                    # sum(x)        -> sum count of conversion error
    agg_4 = {c: sum for c in DataWork.colGrp['adjValue']}               # sum(adjValue) -> sum numeric values
    agg_5 = {c: (lambda x: separator.join(set(x))) for c in colText}    # text aggregation

    agg_method = {**agg_1, **agg_2, **agg_3, **agg_4, **agg_5}
    df2 = df1.groupby(colGroupBy).agg(agg_method).reset_index()

    # make header
    header = func.map_header(df2, {**DataWork.origCol['mapping'], **setting.customHeader})

    # reformat column header into dataframe
    header = pd.DataFrame([header], columns=df2.columns)

    # merge results
    recordCount = len(df2)
    df3 = pd.concat([header, df2], axis=0)

    # re-arrange columns by original position
    # original position is implied in column name (e.g. a2_value -> 2)
    columnList = [side + '.entry'] + \
                 ([side + '.err'] if (len(DataWork.colGrp['err']) > 0) else []) + \
                 sorted(DataWork.colGrp['others'] + DataWork.colGrp['adjValue'],
                        key=lambda x: int(x.lstrip(side).split('_')[0]))
    df3 = df3[columnList]

    # copy result to clipboard
    df3.to_clipboard(excel=True, sep=None, index=False, header=False)

    return [recordCount, popUpWindow]


def run_connection(parent, DataSourceA, DataSourceB, DataWorkA, DataWorkB, option):

    popUpWindow = 1

    # use the dataset selected by user
    if option['optDataSet'] == 0:
        side = 'a'
    else:
        side = 'b'
    DataWork = DataWorkA if (side == 'a') else DataWorkB
    df1 = DataWork.df.copy()

    # discard uid which will not be used
    df1.drop(columns=DataWork.colGrp['uid'], inplace=True)

    # get column name of the first 2 columns
    jk1 = DataWork.colGrp['joinKey'][0]
    jk2 = DataWork.colGrp['joinKey'][1]
    k1 = DataWork.colGrp['key'][0]
    k2 = DataWork.colGrp['key'][1]

    # create a dictionary in which each distinct element is mapped to a corresponding numeric ID
    # ... consolidate all relationships into one dataframe
    dfUnion = pd.concat([
        df1[[jk1, k1]].rename(columns={jk1: 'joinKey', k1: 'key'}),
        df1[[jk2, k2]].rename(columns={jk2: 'joinKey', k2: 'key'})
    ])
    # ... ensure unique relationships (each 'joinKey' cannot link to more than one 'key')
    dfDict = dfUnion.groupby('joinKey').agg({'key': 'first'}).reset_index()
    # ... create mapping dictionary
    uniqueID = range(len(dfDict))
    uniqueKey = dfDict['key']
    uniquejoinKey = dfDict['joinKey']
    mapping = dict(zip(uniquejoinKey, uniqueID))

    # insert the numeric ID column
    df1['uniqueID1'] = df1[jk1].map(mapping)
    df1['uniqueID2'] = df1[jk2].map(mapping)

    # create a full list of paired elements ([[a, b], [c, d], [e, f], ...])
    groups = pd.concat([df1['uniqueID1'], df1['uniqueID2']], axis=1).values.tolist()
    # insert an empty list at the end acting as a stopper, it tells the program to stop when all items have been iterated
    groups.append([])

    # outer loop - iterate through every pairs (e.g. [a, b], [c, d])
    for x in range(len(groups)):
        if groups[0]:                                   # proceed if not an empty list (stopper)
            subject_group = groups[0]
            removable = []

            pos = 0
            # inner loop - elements inside the current pair will be searched within all other pairs
            # (e.g. a in [a, b], a in [c, d], b in [a, b], b in [c, d], ...)
            for group in groups:
                for _id in subject_group:               # 'subject_group' will grow dynamically
                    if _id in group:                    # is it a common element?
                        subject_group = list(
                            set(subject_group + group)  # merge this pair into 'subject_group' if it is common
                        )
                        removable.append(pos)           # flagged this pair as redundant after the merge
                        break                           # jump to next pair
                pos += 1

            # move the current pair to bottom
            groups.append(subject_group)

            # remove redundant pairs to speed up subsequent loops
            if removable:
                for i in sorted(removable, reverse=True):  # important: items must be deleted starting from the bottom
                    del groups[i]

        # escape outer loop once the stopper has been encountered
        else:
            del groups[0]
            break

    # output the interim result
    group_no = []
    entity_name = []
    no = 1
    for group in groups:
        for _id in group:
            group_no.append(no)
            entity_name.append(_id)
        no += 1

    # retrieve the actual name by numeric ID
    mapping = dict(zip(uniqueID, uniqueKey))
    entity_name = [mapping[name] for name in entity_name]

    # reformat final result into dataframe
    df2 = pd.DataFrame(
        {
            'Group No.': group_no,
            'Member': entity_name
        }
    )

    # copy result to clipboard
    recordCount = len(df2)
    df2.to_clipboard(excel=True, sep=None, index=False, header=True)

    return [recordCount, popUpWindow]


# ------------------------------------------------------ #
# run profiling
# ------------------------------------------------------ #

def run_profiling(parent, DataSourceA, DataSourceB, DataWorkA, DataWorkB, option):

    popUpWindow = -1
    recordCount = -1

    DataSource = DataSourceA if option['optDataSet'] == 0 else DataSourceB
    Form = ProfilingForm(parent, DataSource, option)

    return [recordCount, popUpWindow]


class ProfilingForm(tk.Toplevel):

    # define visual element dimension
    chtWidth = 475
    chtHeight = 155
    thWidth = 210
    tdWidth = 100

    def __init__(self, parent, DataSource, option):
        tk.Toplevel.__init__(self, parent)

        # create modal form
        self.root = parent
        self.transient(parent)
        self.grab_set()

        # set modal form attribute
        self.left_x = parent.winfo_rootx()
        self.top_y = parent.winfo_rooty()
        self.geometry("{0}x{1}+{2}+{3}".format((65 + self.thWidth + self.chtWidth), 600, self.left_x + 100, self.top_y))
        self.title('Result')
        self.resizable(0, 0)

        # set variable reference
        self.option = option
        self.DataSource = DataSource

        # initialize a frame to accommodate all created visual objects
        self.inner_frame = tk.Frame()

        # show modal form
        self.make_window_scrollbar()
        self.cascade()

    def cascade(self):
        # insert caption
        self.canvas_top_caption = sty.Drawing(self.inner_frame)
        self.canvas_top_caption.draw_profiling_caption('Profiling Summary')
        self.canvas_top_caption.grid(row=0, column=0, columnspan=9, sticky='wn', padx=(10, 0), pady=(5, 20))

        # generate individual summary for all data fields
        for cid, c in enumerate(self.DataSource.df.columns):
            self.insert_stats(cid, c)

    def insert_stats(self, cid, c, oldStats=None, ctype=None):
        """
        :param oldStats: if specified, replace the already generated summary with a new one
        :param ctype: if specified, default column type is override by this value
        """
        df = self.DataSource.df

        # create new individual summary
        stats = DataFieldStats(self.inner_frame, self.option, df, cid, c, top=self, ctype=ctype)
        stats.grid(row=cid + 1, column=0)

        # destroy old summary (if exists) after new summary has been created
        if oldStats:
            oldStats.destroy()

    def make_window_scrollbar(self):
        # create the base frame
        super_frame = tk.Frame(self)
        super_frame.pack(fill='both', expand=1)

        # create Canvas on the base frame
        super_canvas = tk.Canvas(super_frame, bg='white', highlightthickness=0)
        super_canvas.pack(side='left', expand=1, fill='both')

        # attach scrollbar to Canvas
        form_scrollbar = ttk.Scrollbar(super_frame, orient='vertical', command=super_canvas.yview)
        form_scrollbar.pack(side='right', fill='y')

        # configure Canvas
        super_canvas.configure(yscrollcommand=form_scrollbar.set)
        super_canvas.bind("<Configure>", lambda e: super_canvas.configure(scrollregion=super_canvas.bbox("all")))

        # create an inner frame on Canvas
        inner_frame = tk.Frame(super_canvas, bg='white')

        # place inner frame inside Canvas window object
        super_canvas.create_window((0, 0), window=inner_frame, anchor="nw")

        # set reference to inner frame
        self.inner_frame = inner_frame


class DataFieldStats(tk.Frame):

    # get visual element dimension
    chtWidth = ProfilingForm.chtWidth
    chtHeight = ProfilingForm.chtHeight
    thWidth = ProfilingForm.thWidth
    tdWidth = ProfilingForm.tdWidth

    # set common style
    tdColor = '#F7F7F7'
    fillColor = ['#39E5FF', '#6FECFF', '#9BF2FF', '#C2F7FF', '#E9FCFF', '#D0EDF1']
    lineColor = '#69D6FF'
    bold = ('Arial', 9, 'bold')

    def __init__(self, parent, option, df, cid, c, top, ctype=''):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.df = df
        self.option = option
        self.c = c                              # column name
        self.cid = cid                          # column position
        self.top = top                          # parent modal form
        self.colTypeIn = ctype                  # column type specified by user that overrides aut-detected column type

        # initialize output variables
        self.df1 = pd.DataFrame()
        self.colType = ''                       # column type (auto-detected)
        self.fieldName = ''                     # column header
        self.nRecord = 0
        self.nMissing = 0
        self.value_counts = pd.Series(dtype='object')

        # miscellaneous
        self['bg'] = 'white'
        # workaround: in order to set tk.Label size in pixel, a blank image must be embedded in tk.label
        self.img = tk.PhotoImage()

        # transform data in column
        self.transform_column(c)

        # visualize data in column
        # --------------------------------------------------------------------------
        # left side - mean, missing value, etc.
        # --------------------------------------------------------------------------
        self.create_basic_stats(self.df1, c, self.cid, self.colType, self.fieldName,
                                self.value_counts, self.nMissing, self.nRecord)
        # --------------------------------------------------------------------------
        # right side - histogram, top 5, pie chart
        # --------------------------------------------------------------------------
        if self.colType == 'numeric':
            self.create_histogram(self.df1, c, self.cid, self.colType,
                                  self.value_counts, self.nMissing, self.nRecord)
        elif self.colType == 'text':
            self.create_pie_chart(self.df1, c, self.cid, self.colType,
                                  self.value_counts, self.nMissing, self.nRecord)

    def transform_column(self, c):
        # copy entire column into a new dataframe
        df1 = pd.DataFrame()
        df1[c] = self.df[c]

        # get column header and drop 1st row
        self.fieldName = str(df1.iloc[0, 0])[:50]  # trim name length
        df1.drop(index=df1.index[0], axis=0, inplace=True)

        # strip whitespaces if this user option is on
        if 'optIgnorePadding' in self.option:
            df1[c] = df1[c].apply(lambda x: x.strip() if isinstance(x, str) else x)

        # replace empty string with NaN
        df1 = df1.mask(df1 == '')
        # convert column type to numeric, however this only works if the column does not contain any string value
        df1 = df1.astype('float', errors='ignore')
        df1 = df1.convert_dtypes(convert_integer=True, convert_floating=True)

        # determine column type (numeric or text)
        if 'num' in str(self.colTypeIn).lower():                                # user specified numeric
            typ = 0
        elif 'text' in str(self.colTypeIn).lower():                             # user specified text
            typ = 1
        elif any([s in str(df1.dtypes[c]).lower() for s in ['int', 'float']]):  # auto-detected numeric
            typ = 0
        else:
            typ = 1                                                             # auto-detected text
        self.colType = ['numeric', 'text'][typ]

        # prepare the data according to column type
        if typ == 0:
            # force convert all value into number
            df1[c] = pd.to_numeric(df1[c], errors='coerce')
        else:
            # align letter case if case-insensitive option is on
            if self.option['optIgnoreCase'] == 1:
                func.df_align_case(df1, [c])

        # compute basic statistic
        self.nMissing = df1[c].isna().sum()                 # total N/A count
        self.nRecord = len(df1[c])                          # total record count
        self.value_counts = df1[c].value_counts()           # total distinct count (N/A excluded)

        self.df1 = df1

    def create_basic_stats(self, df1, colName, cid, colType, fieldName, value_counts, nMissing, nRecord):
        cells = dict()

        # create a frame to enclose data table
        frame = tk.Frame(self, background=self.tdColor)
        frame.grid(row=0, column=0, padx=10, pady=(0, 10), sticky='nw')

        # place data table caption
        tk.Label(frame, text=fieldName, bg='#009EFF', fg='white', image=self.img, compound='c',
                 font=self.bold, anchor='nw', width=self.thWidth, wraplength=self.thWidth - 10,
                 ).grid(row=0, column=0, columnspan=2, sticky='nw')

        # compute basic statistic
        # ... compute Mean and Median (for numeric column)
        if colType == 'numeric':
            cells['mean'] = ['Mean', str(func.format_by_significance(df1[colName].dropna().mean()))[:17], 'black']
            cells['median'] = ['Median', str(func.format_by_significance(df1[colName].dropna().median()))[:17], 'black']
        # ... compute Distinct Value frequency (for text column)
        elif colType == 'text':
            cells['distinct'] = ['Distinct Value', len(value_counts), 'black']
        # ... compute Missing Value frequency
        na_pct = (nMissing / nRecord) if nRecord != 0 else 0
        na_text = f"{na_pct:.0%}" + (f" ({nMissing})" if nMissing > 0 else "")
        na_color = 'red' if (nMissing > 0) else 'black'
        cells['Missing Value'] = ['Missing Value', na_text, na_color]

        # insert basic stats into data table
        cellstyle = {'width': self.tdWidth, 'bg': self.tdColor, 'image': self.img, 'compound': 'c', 'anchor': 'w'}
        for j, cell in enumerate(cells.values()):
            tk.Label(frame, **cellstyle,
                     text=cell[0], font=self.bold
                     ).grid(row=j+1, column=0, sticky='w')
            tk.Label(frame, **cellstyle,
                     text=cell[1], fg=cell[2]
                     ).grid(row=j+1, column=1, sticky='w')
        pos = j+2

        # create a toggle button to let user reload statistic in another data type
        # it calls a function from parent form that will destroy and re-create the current block of visualization
        # ... load background image for the button
        self.gallery = sty.Gallery()
        bg = self.gallery.get('button_xp')
        # ... toggle between alternative data type
        ctype = 'numeric' if (colType == 'text') else 'text'
        tk.Button(frame, text='To ' + ctype,
                  borderwidth=0, image=bg, compound='c',
                  background=self.tdColor, activebackground=self.tdColor,           # prevent color change upon click
                  command=lambda: self.top.insert_stats(cid, colName, self, ctype)
                  ).grid(row=pos, column=0, sticky='w', padx=2, pady=5)

    def create_histogram(self, df1, colName, cid, colType, value_counts, nMissing, nRecord):
        # histogram size
        topMargin = 15
        leftMargin = 50
        columnWidth = 40
        columnHeight = 100

        # create Canvas
        can = tk.Canvas(self, width=self.chtWidth, height=self.chtHeight, bg='white', highlightthickness=0)
        can.grid(row=0, column=1, pady=(0, 15))

        # histogram parameter
        cut = 10
        bins = []
        binLabels = []

        # calculate max, min
        upper = df1[colName].dropna().max()                 # drop NaN (could be resulted from pd.to_numeric)
        lower = df1[colName].dropna().min()
        # skip if max and min is missing
        if not {'<NA>', 'nan'}.intersection([str(upper), str(lower)]):
            if lower == upper:
                # if max == min all bins have identical value, the upper end value is extended to prevent error
                upper += 10

            # calculate bins
            chunk = (upper - lower) / cut
            bins = [lower + chunk * n for n in range(cut + 1)]
            bins[0] = lower                                 # lower end must equal original min
            bins[cut] = upper                               # upper end must equal original max
            # print(bins)

            # calculate frequency
            binLabels = list(range(cut))
            df1['binned'] = pd.cut(df1[colName], bins=bins, labels=binLabels, include_lowest=True)
            freq = df1['binned'].value_counts(sort=False)
            total = sum(freq)
            freq_pct = {k: (v / total if total != 0 else 0) for k, v in freq.items()}
            # print(binLabels)

            # ... Y-axis label
            for n in range(5):
                can.create_text(40, topMargin + n * 25,
                                text=str(columnHeight - n * 25) + '%', anchor='e', font=('Arial', 7))
            # ... X-axis label
            for n in range(len(bins)):
                can.create_text(leftMargin + columnWidth * n, 120,
                                text=func.round_by_size(bins[n], chunk, upper),
                                width=30, anchor='n', justify='c', font=('Arial', 8))  # "width" means "wraplength"
                                # width=40, angle=90, anchor='c', font=('Arial', 8))

            # ... bars
            for n in range(cut):
                if freq_pct[n] > 0:
                    can.create_rectangle(leftMargin + columnWidth * n,
                                         topMargin + columnHeight - (freq_pct[n] * columnHeight),
                                         (leftMargin + columnWidth) + columnWidth * n,
                                         topMargin + columnHeight,
                                         fill=self.fillColor[3], outline=self.lineColor, width=1)
            # ... bottom border
            y = topMargin + columnHeight
            can.create_line(leftMargin, y, leftMargin + (columnWidth * 10), y, fill='#69D6FF')

        else:
            pass

    def create_pie_chart(self, df1, colName, cid, colType, value_counts, nMissing, nRecord):
        # create Canvas
        can = tk.Canvas(self, bg='white', width=self.chtWidth, height=self.chtHeight,
                        highlightthickness=0)
        can.grid(row=0, column=1)

        # create frame
        frame = tk.Frame(self, bg='#DEE2E3')
        frame.grid(row=0, column=1, padx=10, pady=(0, 15), sticky='nw')

        # add missing count into value_counts
        value_counts_f = value_counts
        if nMissing > 0:
            if value_counts_f.get('') is None:
                value_counts_f[''] = nMissing          # if not exists, add new index (empty string)
            else:
                value_counts_f[''] += nMissing         # if already exists, increment

        # extract top 6 items
        top6 = dict(list(value_counts_f.items())[:6])

        # insert table header
        row = 0
        tk.Label(frame, font=self.bold, bg='white', fg='#6A6A6A', text='Rank', width=5).grid(
            row=row, column=0, padx=1, pady=1)
        tk.Label(frame, font=self.bold, bg='white', fg='#6A6A6A', text=' Top 5 Values', anchor='w', width=25).grid(
            row=row, column=1)
        tk.Label(frame, font=self.bold, bg='white', fg='#6A6A6A', text='Percent', width=7).grid(
            row=row, column=2, padx=1, pady=1)
        row += 1

        # create pie chart
        radius = self.chtHeight - 20
        accum = 0
        rank = 1
        for key, count in top6.items():
            # change item #6 into "others" here (did not modify dict directly as "others" might be an existing key in dict)
            if rank > 5:
                key = 'other than top ' + str(rank - 1)
                top5_sum = sum(list(value_counts_f.values)[:5])
                count = nRecord - top5_sum

            # insert row into table
            tk.Label(frame, text=rank, bg='white', width=5).grid(
                row=row, column=0, padx=1, pady=(0, 1))
            tk.Label(frame, text=' ' + str(key)[:25], anchor='w', bg='white', width=25).grid(
                row=row, column=1)
            tk.Label(frame, text="{:.0%}".format(count / nRecord), bg=self.fillColor[rank - 1], width=7).grid(
                row=row, column=2, padx=1)

            # insert pie slice
            can.create_arc((330, 10, 330 + radius, radius),
                           fill=self.fillColor[rank - 1], outline=self.fillColor[rank - 1],
                           start=89 + (359 * accum), extent=-359 * (count / nRecord))

            accum -= (count / nRecord)
            rank += 1
            row += 1

