## Introduction
This standalone tool aims to faciliate data manulplations that are usually not intuitive to average Excel users and sometimes considered troublesome even to more advanced Excel users. Examples include table join and text aggregation, these operations are yet to be fully addressed in basic Excel functions.

This tool can work with 2 datasets at a time. The user copies data from a spreadsheet to this tool via the clipboard, without going through manual data import process at all. It can also read other tabular data formats, such as a table (non-image) shown on a webpage.

## Screenshot
It is not complicated to operate this tool in practice. Every functions are readily accessible on a user interface with a streamlined design. To start an operation, the first step is to copy the source data (including the column header), and then press Ctrl + V on either the left or the right dataset container on the main window. After the data shows up in the dataset container, press one of the the square button to run a specific operation.

![picture](/res/screenshot.png)

## Capabilities
This tools offers the following capilities:

| Operation | Outcome | Illustrative Example |
| :---------| :------ | :----------- |
| Profiling | Calculate basic statistics for every column in the selected dataset. For columns of numeric data type, mean and median are computed, and the graphical distribution of numeric values are plotted. For text columns, the distribution of top 5 items are displayed | ![picture](/res/example_run_profiling.png) |
| Left Join | Perform record matching in the same way as SQL left join. Alternatively, user can opt to fetch only the first match, which imitate the behavior of Excel's vlookup/xlookup function | ![picture](/res/example_run_join.png) |
| Aggregation | Equivalent to the aggregation functionality in SQL, this operation aggregrates numbers as well as texts | ![picture](/res/example_run_aggregation.png) |
| Fast Compare | Compare 2 datasets with the exact same layout and calculate the difference for columns selected by the user | ![picture](/res/example_run_compare_value.png) |
| Exception | Compare 2 datasets with the exact same layout, find out the records that are exclusive to each other | ![picture](/res/example_run_exception.png) |
| Connection | Connect related elements into groups. Related elements are represented by records in a 2-column dataset and each column contains one element that is related to the other. This operation scan through the entire dataset linking up all presented relationships by searching for common elements, and then divides the elements into distinctive groups. This is a convenient function for tasks such as identifying reachable nodes on a path, distinguishing groups of associated companies, etc. | ![picture](/res/example_run_connection.png) |


## Limitations
1. It is recommended to remove all formats before copying from a Excel spreadsheet. This is because the clipboard always copies displayed values but not underlying values. This behavior leads to incorrect data type or loss of precision, which may produce unintended results if not carefully inspected. For instance,

    | Underlying Value | Displayed Value |
    | :---------- | :------ |
    | 2.55 | 2.6 |
    | 0.901 | 90% |
    | 31-Jan-21 | 31-Jan |
    | 232,000,000,000 | 2.32e+11 |

2. While pasting the output to Excel, padding zero could be lost (e.g. "01" becomes "1") if column type in a worksheet is not formatted as "Text". To work-around, select the entire column in Excel and choose "Format Cells" and choose "Text".
3. To aviod system instability cause by low memory condition, a limitation on data size (maximum number of rows and columns) has been imposed as a prudent measure to prevent excessive large data from being read into memory. User can adjust the limits by pressing the 'setting' button in the main window. It should be noted that extending the limits beyond capacity could significantly degrade performance (impact varies on individual machines).


## Requirements
This python tool is designed to run with minimal dependencies. Neverthelsess, the pre-installation of a few standard libraries is required.
1. Python version 3.8
2. Pandas library
3. NumPy library


## File Structure
| Folder/File | Purpose |
| :---------- | :------ |
| res\ | image library folder |
| main.py | the main entry point of this tool |
| mod*.py | modules consisting of common classes and functions |
| operation.py | the specific module for all runnable operations |
| setting.py | the configuration file |
