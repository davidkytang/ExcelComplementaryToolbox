
import setting
import mod_function as func


def validate_source(operation, DataSourceA, DataSourceB):
    """
    raise exception if validation conditions were not satisfied
    :return: null
    """
    colCountA = len(DataSourceA.df.columns)
    colCountB = len(DataSourceB.df.columns)

    # check min column requirement
    if operation in ['run_profiling', 'run_aggregation', 'run_connection']:

        if (colCountA == 0) and (colCountB == 0):
            raise Exception('Dataset A and B are both empty.', 'w')

        if not (colCountA >= 2 or colCountB >= 2):
            raise Exception('Dataset has to contain at least 2 columns.', 'w')

    else:

        if (colCountA == 0) or (colCountB == 0):
            raise Exception('This operation requires data in both Dataset A and B.', 'w')

        if not (colCountA >= 2 and colCountB >= 2):
            raise Exception('Dataset has to contain at least 2 columns.', 'w')

        if operation in ['run_exception']:
            if not (colCountA == colCountB):
                raise Exception('Number of columns in A and B have to be equal.', 'w')


def validate_user_option(command, options, DataSourceA, DataSourceB):
    """
    validate user options and return which rule was breached
    :return: A list of warning messages in order of occurrence
    """
    warnings = []

    selDataSet = options.get('optDataSet')
    colNameA = DataSourceA.df.iloc[0, :].tolist() if len(DataSourceA.df) > 0 else []
    colNameB = DataSourceB.df.iloc[0, :].tolist() if len(DataSourceB.df) > 0 else []

    # validate dataset layout
    if command == 'run_connection':
        if len([colNameA, colNameB][selDataSet]) != 2:
            warnings.append('The Connection operation requires exactly 2 columns in the dataset.')

    elif command == 'run_compare_value':
        if len(colNameA) != len(colNameB):
            warnings.append('The 2 datasets have to be in exact same layout in order to compare.')

    # validate user options
    for option, value in options.items():

        if option == 'optDataSet':
            # check inadequate columns in target dataset
            if value == 0:
                if len(colNameA) == 0:
                    warnings.append('Dataset A has no data yet.')
                elif len(colNameA) < 2:
                    warnings.append('To proceed, at least 2 columns is required in this dataset.')
            elif value == 1:
                if len(colNameB) == 0:
                    warnings.append('Dataset B has no data yet.')
                elif len(colNameB) < 2:
                    warnings.append('To proceed, at least 2 columns is required in this dataset.')

        elif option == 'optJoinColumns':
            colKeyA = func.bisect_list(value, 'a')
            colKeyB = func.bisect_list(value, 'b')

            # check invalid selection
            if sum(colKeyA + colKeyB) == 0:
                warnings.append('To continue, please select at least 1 pair of matching keys.')

            # check duplicated selection
            sideA = ['A', colKeyA, colNameA]
            sideB = ['B', colKeyB, colNameB]
            for side, colKey, colName in [sideA, sideB]:
                for keyID in colKey:
                    if keyID != 0 and colKey.count(keyID) > 1:
                        warnings.append('Duplicated keys "' + colName[keyID-1] + '" were selected in Dataset ' + side + '.')
                        break

            # check mismatched key pairs
            name = ''
            for a, b in zip(colKeyA, colKeyB):
                if a > 0 and b == 0:
                    name = colNameA[a - 1]
                elif a == 0 and b > 0:
                    name = colNameB[b - 1]

                if name != '':
                    warnings.append('All selected keys must be in pairs (missing pairing field: "' + name + '").')
                    break

        elif option == 'optDeltaColumns':
            selectedIndex = value

            # filter out 0 which represents an unselected value
            nonZero = [idx for idx in selectedIndex if (idx != 0)]

            if len(colNameA) < 2 or len(colNameB) < 2:
                warnings.append('At least 2 data columns are required for this operation.')

            if sum(selectedIndex) == 0:
                warnings.append('To continue, please select at least 1 numeric data field.')

            if len(nonZero) != len(set(nonZero)):
                warnings.append('Duplicated columns were selected.')

            if len(colNameA) == len(set(nonZero)):
                warnings.append('Cannot use all columns for comparison. Please remove one of your selected columns.')

        elif option in ['optAggNum', 'optAggText']:
            # items selected for optAggNum and optAggText are mutually exclusive
            selectedIndex = options.get('optAggNum', []) + options.get('optAggText', [])

            # filter out 0 which represents an unselected value
            nonZero = [idx for idx in selectedIndex if (idx != 0)]

            # get column name of the target dataset
            colName = [colNameA, colNameB][selDataSet]

            if len(colName) < 2:
                warnings.append('At least 2 data columns are required for this operation.')

            if sum(selectedIndex) == 0:
                warnings.append('To continue, please select at least 1 data field.')

            if len(nonZero) != len(set(nonZero)):
                warnings.append('Duplicated columns were selected.')

            if len(colName) == len(set(nonZero)):
                warnings.append('Cannot apply aggregation on all columns. Please remove one of your selected columns.')

    return warnings


def validate_column_type_limit(side, numColumns, keyColumns):
    """
    check whether the maximum number of columns for a specific type exceeded limit
    :return: null
    """
    limit = setting.limits['maxKeyCol']
    if len(keyColumns) > limit:
        raise Exception(('Total no. of Key columns exceeded current limit.'
                        + '\n\nPlease reduce the columns in dataset {} or you could adjust the limit in \'Setting\'.'
                        + '\n\n(maximum: {}  current: {})').
                        format(side.upper(), limit, len(keyColumns)), 'w')

    limit = setting.limits['maxNumCol']
    if len(numColumns) > limit:
        raise Exception(('Total no. of Numeric columns exceeded current limit.'
                        + '\n\nPlease reduce the columns in dataset {} or you could adjust the limit in \'Setting\'.'
                        + '\n\n(maximum: {}  current: {})').
                        format(side.upper(), limit, len(numColumns)), 'w')

