
import numbers
import tkinter

import numpy as np
import tkinter.messagebox as messagebox         # messagebox method has to be separately import


def bisect_list(data: list, side):
    """
    split a list in the middle and return either half depending on criteria
    :return: a list
    """
    items = []
    cut = int(len(data)/2)
    if side == 'a' or side == 0:
        items = data[0: cut]
    elif side == 'b' or side == 1:
        items = data[cut:]
    return items


def get_unique_item(data: list, n):
    """
    # turn a list into a set and draw N items from it
    :return: a set
    """
    items = []
    for d in set(data):
        items.append(d)
        if len(items) >= n:
            break
    return items


def map_header(df, dictMap):
    """
    get header mapping in dictMap and if no matching then use column label instead
    """
    # match portion before an underscore (e.g. column name "a3_joining_key" -> "a3")
    header = [dictMap.get(str(c).split('_')[0], str(c).split('_')[0]) for c in df.columns]
    # match portion after a dot (e.g. column name "a.uid" - > "uid")
    header = [dictMap.get(str(h).split('.')[len(str(h).split('.'))-1], str(h)) for h in header]
    return header


def dual_name_header(header_1, header_2):
    """
    combine column headers from both dataframes
    """
    header = []
    for s1, s2 in zip(header_1, header_2):
        header.append(s1 + ' / ' + s2 if (s1.lower() != s2.lower()) else s1)
    return header


# ------------------------------------------------------ #
# Data Conversion / Transform
# ------------------------------------------------------ #

def df_align_case(df, columns):
    """
    this function align letter case for every distinct values in a column, it finds all distinct values and overwrites
    all of them using the 1st value in that group, for instance, an 'apple' group will be transformed from
    ['apple', 'Apple', 'APPLE'] into ['apple', 'apple', 'apple'], the purpose of this function is to preserve the
    original letter case arrangement of certain data such as company name and address in which letter case affects
    readability and carries meaning, on the flip side, it slows down the program and impact overall performance
    :return: null - this function directly modify the linked dataframe
    """
    for c in columns:
        # convert entire column to string type
        df_case = df[[c]].astype('string')
        # copy the whole column in lower case
        df_case['low'] = df_case[c].str.lower()
        # make flag 1 -> 1st element in distinct group = True
        df_case['1st'] = ~df_case['low'].duplicated(keep='first')
        # make flag 2 -> duplications = True
        df_case['dup'] = df_case['low'].duplicated(keep=False)
        # put 1st value of each distinct group into a dictionary,
        # except those with duplication flag is False, since those values are already unique
        first = df_case[['low', c]].loc[(df_case['1st']) & (df_case['dup'])]
        first = dict(zip(first['low'].to_list(), first[c].to_list()))
        # apply map function to every distinct group
        df_case['after'] = df_case[c]
        df_case.loc[df_case['dup'], 'after'] = df_case.loc[df_case['dup'], 'low'].map(first)
        df[c] = df_case['after']


def to_val(var, optWipeComma):
    """
    1. convert input variable into float number
    2. this function retains a static variable (list) to keep count of unsuccessful conversion
    :return: float number (if success) or NaN (if failed)
    """
    # initialize variable (False = success; True = failed)
    boolFailure = False
    # explicit number, no conversion
    if isinstance(var, numbers.Number):
        var2 = var
    else:
        non_number = var
        # user option - treat comma (,) as thousand separator
        if optWipeComma == 1:
            non_number = str(non_number).replace(',', '')
        # convert automatically with the float() function
        # note: float() also removes whitespace and new line, therefore strip() is not required here
        try:
            var2 = float(non_number)
        except ValueError:
            # output NaN if the value is not convertible
            var2 = np.NAN
            # tag conversion as a failure; however if original value is an empty string, tag conversion as a success
            boolFailure = True if str(var).strip() != '' else False
    # write success/failure into the list
    to_val.failStatus.append(boolFailure)
    return var2


# ------------------------------------------------------ #
# Interface
# ------------------------------------------------------ #

def alert(e: Exception):
    message = str(e.args[0])
    # second argument determines message style, if argument not provided, default is an error message
    severity = str(e.args[1]) if (len(e.args) >= 2) else 'e'
    if severity == 'e':
        return messagebox.showerror('Error', message)
    elif severity == 'i':
        return messagebox.showinfo('Notification', message)
    elif severity == 'w':
        return messagebox.showwarning('Please Retry', message)


def centered_window(root: tkinter.Tk, width, height):
    # calculate x, y coordinates of the centered position
    x = int((root.winfo_screenwidth()/2) - (width/2))
    y = int((root.winfo_screenheight()/2) - (height/2))
    return '{0}x{1}+{2}+{3}'.format(width, height, x, y)


# ------------------------------------------------------ #
# Customized Number Formatting
# ------------------------------------------------------ #

def round_by_size(number, chunk, upper):
    number_abs = abs(number)
    # determine the number of decimal places
    digits = len(str(round(abs(upper) / abs(chunk)))) if upper != 0 else 0      # e.g. 10,000/10 = 1,000 --> 4 digits
    decimal = max(digits - 2, 0)
    decimal = min(decimal, 4)
    # display more decimal for smaller numbers
    decimal += 4 if (0.0 < number_abs < 1.0) else 0
    # specify none decimal place for integers (decimal = 0 still gives 9.00; decimal = None gives 9)
    decimal = decimal if (decimal != 0) else None
    # debug >> print(number_abs, upper, chunk)

    # abbreviate large numbers depending on size
    formatted = round(number, decimal)
    if number_abs >= 1000000:
        for unit, threshold in {'T': 1000000000000, 'B': 1000000000, 'M': 1000000}.items():
            if number_abs >= threshold:
                formatted = "{0}{1}".format(round(number / threshold, decimal), unit)
    elif number_abs >= 99999:
        formatted = "{0}{1}".format(round(number / 1000, decimal), 'K')
    elif number_abs >= 1:
        formatted = round(number, decimal)
    return formatted


def format_by_significance(number):
    if str(number) not in ['<NA>', 'nan']:              # check if dataframe.mean() returns 'NAType'
        number_abs = abs(number)
        rounded = 0
        if (number - int(number)) == 0:                 # for full integer
            rounded = f"{number:.0f}"
        elif number_abs >= 1000000:                     # for big number
            rounded = f"{number:.1f}"
        else:                                           # for small number
            for i in range(15):
                if number_abs >= 1/(10 ** i):
                    digit = 2 + i
                    rounded = f"{number:.{digit}f}"
                    break
    else:
        rounded = None
    return rounded
