
# ------------------------------------------------------ #
# user option list
# ------------------------------------------------------ #
operationParam = {
    'run_profiling':
        {
            'optDataSet': 0,
            'optIgnoreCase': 1,
            'optIgnorePadding': 1
        },
    'run_aggregation':
        {
            'optDataSet': 0,
            'optAggText': [0]*5, 'optAggNum': [0]*5,
            'optSeparator': 1, 'optIgnoreCase': 1
        },
    'run_compare_value':
        {
            'optDeltaColumns': [0]*10,
            'optIgnoreCase': 1, 'optTrim': 1, 'optTrimZero': 0,
            'optWipeComma': 0,
            'optPercentChg': 0, 'optChgVsTotal': 0, 'optControlTotal': 1
        },
    'run_join':
        {
            'optJoinColumns': [0]*5,
            'optIgnoreCase': 1, 'optTrim': 1, 'optTrimZero': 0,
            'optJoinMode': 0
        },
    'run_exception':
        {
            'optIgnoreCase': 1, 'optTrim': 1, 'optTrimZero': 0,
            'optReturnUnique': 1,
        },
    'run_connection':
        {
            'optDataSet': 0, 'optIgnoreCase': 1, 'optTrim': 1
        }
    # 'optPartialMatch': 15
}

# ------------------------------------------------------ #
#  user option description
# ------------------------------------------------------ #
optDesc = {
    'optJoinColumns': 'Specify corresponding linking keys : ',
    'optDeltaColumns': 'Specify numeric columns to be compared between 2 datasets : ',
    'optIgnoreCase': 'Ignore case (case-insensitive)',
    'optJoinMode': 'SQL-mode (keep multiple match) | VLookup-mode (only fetch 1st matched record from Data B despite multiple match)',
    'optDataSet': 'Dataset A | Dataset B',
    'optAggNum': 'Apply summation function to selected columns (up to 5 columns): ',
    'optAggText': 'Apply text aggregation to selected columns (up to 5 columns): ',
    'optSeparator': 'Select text separator',
    'optTrim': 'Remove leading and trailing whitespaces',
    'optIgnorePadding': 'Ignore leading and trailing whitespaces',
    'optTrimZero': 'Remove leading zeros',
    'optPartialMatch': 'Match by first X characters',
    'optWipeComma': 'Parse comma-separated value to number (treat comma as thousand separator)',
    'optReturnUnique': 'Return unique combinations only',
    'optPercentChg': 'Calculate percent of increase / decrease',
    'optChgVsTotal': 'Calculate percent of increase / decrease relative to total change',
    'optControlTotal': 'Include control total'
}

# ------------------------------------------------------ #
# limit settings - updatable by user
# ------------------------------------------------------ #
limits = {
    'maxRow': 100000,   'maxRowInit': 100000,
    'maxCol': 50,       'maxColInit': 50,
    'maxKeyCol': 20,    'maxKeyColInit': 20,
    'maxNumCol': 10,    'maxNumColInit': 10
}

# ------------------------------------------------------ #
# text displayed on button and caption bar
# ------------------------------------------------------ #
alias = {
    'run_aggregation': 'Aggregation',
    'run_compare_value': 'Fast Compare',
    'run_exception': 'Exception',
    'run_connection': 'Connection',
    'run_join': 'Left Join',
    'run_profiling': 'Profiling'
}

# ------------------------------------------------------ #
# customised field remarks
# ------------------------------------------------------ #
customHeader = {
    'entry': '*row count (rows with identical values are combined into one single row, this data field shows the number of rows combined.)',
    'err': '*errors in conversion (the number of values that cannot to be converted to numeric values)',
    'dup': '*aggregation (identical items appeared more than once are aggregated by SUM function)',
    'uid': '*original row number',
    'which': '*dataset'
}


# ------------------------------------------------------ #
# misc parameter
# ------------------------------------------------------ #
# control the behavior of Datawork.set_column_roles()
restColumn = {
    'run_aggregation': 'other',
    'run_compare_value': 'key',
    'run_exception': 'key',
    'run_connection': 'key',
    'run_join': 'other',
    'run_profiling': 'other'
}

sepList = [',', ';', '|', ' ']

img_path = 'res/'
