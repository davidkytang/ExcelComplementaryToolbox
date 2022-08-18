# ExcelDataTool

**Introduction**

**Screenshot**
Main Window

**Capabilities**

| Operation | Outcome | Illustrative Example |
| :---------| :------ | :----------- |
| Profiling | Calculate basic statistics for every column in the selected dataset. For columns of numeric data type, mean and median are displayed, and the distribution of numeric values are plotted. For text columns, the distribution of top 5 items are displayed | ![picture](/res/example_run_profiling.png) |
| Left Join | Perform record matching in the same way as SQL left join. Alternatively, user can opt to fetch only the first match, which imitate the behavior of Excel's vlookup/xlookup function | ![picture](/res/example_run_join.png) |
| Aggregation | Equivalent to the aggregation functionality in SQL, this operation aggregrates numbers as well as texts | ![picture](/res/example_run_aggregation.png) |
| Fast Compare | Compare 2 datasets with the exact same layout and generate a report of difference | ![picture](/res/example_run_compare_value.png) |
| Exception | Compare 2 datasets with the exact same layout, find out the records that are exclusive to each other | ![picture](/res/example_run_exception.png) |
| Connection | Connect related elements into groups. Related elements are represented by records in a 2-column dataset and each column contains one element that is related to the other. This operation scan through the entire dataset linking up all presented relationships by searching for common elements, and then divides the elements into distinctive groups. This is a convenient function for tasks such as identifying reachable nodes on a path, distinguishing groups of associated companies, etc. | ![picture](/res/example_run_connection.png) |

**Limitation**

**Requirement**

**File Structure**

| Folder/File | Purpose |
| :---------- | :------ |
| res\ | image library folder |
| main.py | the main entry point of this tool |
| mod*.py | modules consisting of common classes and functions |
| operation.py | the specific module for all runnable operations |
| setting.py | the configuration file |
