# AMoI

The software calculates the Area Moment of Inertia (the second moment of area) and properties of the plane area.

Created for educational purposes.

This script is used to calculate area moments of inertia, where the area is given by a closed polygon along its perimeter. The program allows you to enter the coordinates of the closed polygon and calculates the moments of inertia to the principal axes, the coordinates of the center of gravity, and the radius of inertia. The result is displayed both in a graph and in a text output.

## Installation

The following commands are used on Windows. On Linux or macOS, use the corresponding commands specific to those systems and their settings (e.g. use `python3` instead of `python`, etc.).

Python 3.6 and higher must be installed (tested with version 3.12.2). You also need to install the packages `PyQt5`, `matplotlib` and `numpy` if they are not already installed with the command
```
pip install PyQt5 matplotlib numpy
```
The [requirements.txt](requirements.txt) file lists the versions of the packages with which the program was tested. It is therefore possible to use the alternative command 
```
pip install -r requirements.txt
```
Running the program from the command line
```
python AMoI.py
```
or building an executable program with the `pyinstaller` package, which is installed with the
```
pip install pyinstaller
```
The command to build the executable program can be
```
python -m PyInstaller --onefile AMoI.py
```

## Using the program

When you start the program, the main window opens:

![main window](images/fig1.png)

1. **Selecting the unit of length:**
Use the **Length unit** drop-down box to select the appropriate physical unit (mm, cm, m, in, ft), which will then be displayed in the graph and in the calculated values list.
2.	**Entering coordinates:**
Enter the coordinates of the closed polygon into the table. Enter each point of the polygon in a new row. The details of the entry are described below with a description of the buttons.
3.	**Coordinate table entry buttons:**
  - **Add Row**: Adds a new blank row to the table.
  - **Remove Selected Row**: Deletes the currently selected row. When selecting a larger area, removes only the last row.
  - **Clear Table**: Deletes the entire table.
  - **Paste from Clipboard**: Paste the coordinates copied to the clipboard. Assumes indented text format with columns separated by tabs or ";", i.e. the input data can be copied from Excel, Google Sheets, text editors, etc. The program checks the number of columns per line (must be 2) and replaces the decimal separator "," with ".".
4.	**Calculation:**
After entering the polygon coordinates, press the **Calculate** button. The program displays the results of the calculation in a text box and plots a graph of the polygon including the principal axes and moments of inertia. After pressing the button, it is verified that there are numerical values in the table and that the table contains at least 3 rows. If any of these conditions are not met, then the user is informed by an error message. 
5. **Save results:**
Press the **Save to CSV** button to save in the `results.csv` file.

## Examples

Enter the following coordinates:

![input data](images/fig2.png)

You can copy the input data from the [example01.csv](examples/example01.csv) file and paste it using the **Paste from Clipboard** button.

It is not necessary that the last point in the table is identical to the first point, the program algorithm closes the polygon.

After pressing the **Calculate** button, the graph window opens and the calculated values appear in the text window.

![graph window](images/fig3.png)
![text window](images/fig4.png)

If the input data is changed, the graph and output data will be overwritten after pressing the **Calculate** button.

The output data can be saved to the `results.csv` file by pressing the **Save to CSV** button. The format of the output file is identical to [example01.csv](examples/example01.csv).

It is also possible to specify a cross-section with a hole. In this case, it is best to specify several closed polygons in a row, so that the outer contour of the cross-section is entered counter-clockwise and the holes with a clockwise order of points as used in the [example02.csv](examples/example02.csv) and [example03.csv](examples/example03.csv) files.

![example02](images/fig5.png)
![example03](images/fig6.png)

