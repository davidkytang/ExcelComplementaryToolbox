## Introduction

## Screenshot
Main Window

## Capabilities

| Operation | Outcome | Illustrative Example |
| :---------| :------ | :----------- |
| Profiling | Calculate basic statistics for every column in the selected dataset. For columns of numeric data type, mean and median are displayed, and the distribution of numeric values are plotted. For text columns, the distribution of top 5 items are displayed | ![picture](/res/example_run_profiling.png) |
| Left Join | Perform record matching in the same way as SQL left join. Alternatively, user can opt to fetch only the first match, which imitate the behavior of Excel's vlookup/xlookup function | ![picture](/res/example_run_join.png) |
| Aggregation | Equivalent to the aggregation functionality in SQL, this operation aggregrates numbers as well as texts | ![picture](/res/example_run_aggregation.png) |
| Fast Compare | Compare 2 datasets with the exact same layout and generate a report of difference | ![picture](/res/example_run_compare_value.png) |
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

This python tool is designed to run with minimal dependencies, however, it still requires pre-installation of a few standard libraries.
1. Python 3.8
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
