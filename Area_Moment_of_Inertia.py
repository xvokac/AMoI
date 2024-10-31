from PyQt5.QtWidgets import QApplication, QComboBox, QTextEdit, QMessageBox, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem
import sys
import matplotlib.pyplot as plt
import math
import numpy as np
from datetime import datetime
import csv
import re


# Function for ArcTan2
def arctan2(y, x):
    pi = np.pi
    pi_2 = np.pi / 2

    if x > 0:
        return np.arctan(y / x)
    elif x < 0:
        return np.arctan(y / x) + pi * np.sign(y)
    elif x == 0:
        return pi_2 * np.sign(y)

# Function for converting a number to engineering notation
def to_engineering_notation(value):
    if value == 0:
        return "0.00e+00"
    
    exponent = int(math.floor(math.log10(abs(value)) // 3 * 3))  # Ensures the exponent is a multiple of 3
    mantissa = value / (10 ** exponent)
    return f"{mantissa:.3f}e{exponent:+03d}"

# Calculation of cross-sectional area and centroid
def cal_area_centrum(x,y):
    A = 0
    xT = 0
    yT = 0
    # Calculate area and centroid
    for i in range(len(x) - 1):
        A += (x[i] * y[i + 1] - x[i + 1] * y[i]) / 2
        xT += (x[i] + x[i + 1]) * (x[i] * y[i + 1] - x[i + 1] * y[i])
        yT += (y[i] + y[i + 1]) * (x[i] * y[i + 1] - x[i + 1] * y[i])
    xC = xT / (6 * A)
    yC = yT / (6 * A)
    return A, xC, yC

def cal_MoI(x,y):
    # Calculate moments of inertia relative to the x- and y-axes
    Ix = 0
    Iy = 0
    Ixy = 0
    for i in range(len(x) - 1):
        Ix += ((y[i]**2 + y[i] * y[i + 1] + y[i + 1]**2) * (x[i] * y[i + 1] - x[i + 1] * y[i])) / 12
        Iy += ((x[i]**2 + x[i] * x[i + 1] + x[i + 1]**2) * (x[i] * y[i + 1] - x[i + 1] * y[i])) / 12
        Ixy += -((y[i] - y[i + 1]) * (3 * x[i]**2 * y[i] + x[i]**2 * y[i + 1] + x[i + 1]**2 * y[i] + 
                                      3 * x[i + 1]**2 * y[i + 1] + 2 * x[i] * x[i + 1] * y[i] + 
                                      2 * x[i] * x[i + 1] * y[i + 1])) / 24
    return Ix, Iy, Ixy

def cal_cetr_MoI(Ix, Iy, Ixy):
    # Angle of the principal axes
    if Ixy == 0:
        alpha = 0
    else:
        alpha = 0.5 * arctan2(2 * Ixy, Iy - Ix)
    
    # Principal moments of inertia
    IxC = Ix * np.cos(alpha)**2 + Iy * np.sin(alpha)**2 - Ixy * np.sin(2 * alpha)
    IyC = Ix * np.sin(alpha)**2 + Iy * np.cos(alpha)**2 + Ixy * np.sin(2 * alpha)
    return IxC, IyC, alpha


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()

        # Set window title
        self.setWindowTitle("Area Moment of Inertia")

        # Layout for selecting length units
        length_unit_layout = QHBoxLayout()

        # Add label for length unit
        self.unit_label = QLabel("Length Unit:")
        length_unit_layout.addWidget(self.unit_label)

        # Add combobox for selecting length units
        self.unit_combobox = QComboBox()
        self.unit_combobox.addItems(["mm", "cm", "m", "in", "ft"])
        length_unit_layout.addWidget(self.unit_combobox)

        # Add length unit layout to main layout
        self.layout.addLayout(length_unit_layout)

        # Label above the table
        self.label = QLabel("Table of coordinates (X, Y) of a closed polygon oriented counterclockwise:")
        self.layout.addWidget(self.label)

        # Table for coordinates
        self.table = QTableWidget(0, 2)  # 0 rows, 2 columns (X, Y)
        self.table.setHorizontalHeaderLabels(["X", "Y"])
        self.layout.addWidget(self.table)


        # Button to add a row
        self.add_row_button = QPushButton("Add Row")
        self.add_row_button.clicked.connect(self.add_row)
        self.layout.addWidget(self.add_row_button)

        # Horizontal layout for control buttons
        control_layout = QHBoxLayout()  


        # Button to delete selected row
        self.remove_row_button = QPushButton("Remove Selected Row")
        self.remove_row_button.clicked.connect(self.remove_selected_row)
        control_layout.addWidget(self.remove_row_button)

        # Button to clear the table
        self.clear_button = QPushButton("Clear Table")
        self.clear_button.clicked.connect(self.clear)
        control_layout.addWidget(self.clear_button)

        # Button to paste data from clipboard
        self.paste_button = QPushButton("Paste from Clipboard")
        self.paste_button.clicked.connect(self.paste_from_clipboard)
        control_layout.addWidget(self.paste_button)

        # Add control layout to main layout
        self.layout.addLayout(control_layout)  

        # Button for performing the calculation
        self.calculate_button = QPushButton("Calculate")
        self.calculate_button.clicked.connect(self.calculate)
        self.layout.addWidget(self.calculate_button)

        # Add output text field
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.layout.addWidget(self.output_text)

        # Button to save results to CSV
        self.save_button = QPushButton("Save to CSV")
        self.save_button.clicked.connect(self.save_to_csv)
        self.layout.addWidget(self.save_button)

        # Set main layout
        self.setLayout(self.layout)

    def add_row(self):
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)

        # Examples for adding data to cells (you can leave them blank)
        self.table.setItem(row_position, 0, QTableWidgetItem("0"))
        self.table.setItem(row_position, 1, QTableWidgetItem("0"))

    def remove_selected_row(self):
        """Removes the selected row"""
        selected_row = self.table.currentRow()  # Get the currently selected row
        if selected_row >= 0:
            self.table.removeRow(selected_row)

    def clear(self):
        # Clear the table before inserting new data
        self.table.setRowCount(0)

    def paste_from_clipboard(self):
        clipboard = QApplication.clipboard()
        data = clipboard.text()  # Get text data from the clipboard (CSV format)

        # Split data by rows and filter out empty rows
        rows = [row for row in data.split('\n') if row.strip()]  # Ignores empty rows

        for row_data in rows:
            columns = re.split(r'[\t;]', row_data)  # Split into columns using tabs or ;

            # Verify correct number of columns
            if len(columns) < 2:
                QMessageBox.warning(self, "Error", "Each row must contain two values (X and Y).")
                continue  # Skip rows with an incorrect number of values

            # Add a new row to the table
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)

            for column_position, cell_data in enumerate(columns[:2]):  # Only first two columns
                # Replace comma with dot if needed
                cell_data = cell_data.replace(",", ".").strip()
                if cell_data:  # Ensures empty values aren't inserted
                    self.table.setItem(row_position, column_position, QTableWidgetItem(cell_data))
                else:
                    self.table.setItem(row_position, column_position, QTableWidgetItem("0"))  # Replace empty cells with zero

    def append_output(self, text):
        """Function for adding text to the output field."""
        self.output_text.append(text)

    def get_selected_unit(self):
        """Function for retrieving the currently selected unit."""
        return self.unit_combobox.currentText()
    

    def calculate(self):

        # Close any previous plot window if it exists
        plt.close('all')
        # Clear the output field before new calculation
        self.output_text.clear()

        """Checks if values in the table are numbers and performs the calculation"""
        num_rows = self.table.rowCount()

        x_values = []
        y_values = []
        
        if num_rows < 3:
            # If there are too few points, show a warning
            QMessageBox.warning(self, "Error", "The minimum number of rows is 3.")
            return

        # Iterate over all cells in the table
        for row in range(num_rows):
            try:
                x_item = self.table.item(row, 0).text()
                y_item = self.table.item(row, 1).text()

                # Check if items are numbers
                x_value = float(x_item)
                y_value = float(y_item)

                x_values.append(x_value)
                y_values.append(y_value)

            except ValueError:
                # If not a number, show a warning
                QMessageBox.warning(self, "Error", f"Row {row + 1}: Values must be numbers.")
                return
        
        # Close the polygon if it is not already closed
        if x_values[0] != x_values[num_rows-1] or y_values[0] != y_values[num_rows-1]:
            x_values = np.append(x_values, x_values[0])
            y_values = np.append(y_values, y_values[0])
       

        """
        Perform moment of inertia calculations
        """
        # Cross-sectional area and centroid coordinates
        A, xC, yC = cal_area_centrum(x_values, y_values)
        # Moments of inertia relative to the x- and y-axes where the coordinates are specified
        Ix, Iy, Ixy = cal_MoI(x_values, y_values)

        # Calculate centroidal moments of inertia - axes parallel to the original coordinate system
        Ix = Ix - A * yC**2  # Using the parallel axis theorem
        Iy = Iy - A * xC**2
        Ixy = Ixy - A * xC * yC

        # Calculate principal central moments of inertia
        IxC, IyC, alpha = cal_cetr_MoI(Ix, Iy, Ixy)

        # Radii of gyration
        ixc = np.sqrt(IxC / A)
        iyc = np.sqrt(IyC / A)

        """
        ############################################################
        # Plotting in a graph
        """

        selected_unit = self.get_selected_unit()

        # Length of coordinate axis arrows - estimate optimal size
        arrow_length = np.max([np.abs(np.max(x_values)-np.mean(x_values)), np.abs(np.min(x_values)-np.mean(x_values)),
                       np.abs(np.max(y_values)-np.mean(y_values)), np.abs(np.min(y_values)-np.mean(y_values)) ]) 

        # Arrow components for x- and y-axes
        arrow_x_dx = arrow_length * np.cos(alpha)  # x-direction component
        arrow_x_dy = arrow_length * np.sin(alpha)  # y-direction component

        arrow_y_dx = -arrow_length * np.sin(alpha)  # Orthogonal y-direction component
        arrow_y_dy = arrow_length * np.cos(alpha)   # Orthogonal y-direction component
        
        # Parameters for inertia ellipse
        # Generate ellipse points
        t = np.linspace(0, 2 * np.pi, 100)  # Parametric angle
        
        # Parametric representation of the ellipse (at origin)
        x_ellipse = iyc * np.cos(t)
        y_ellipse = ixc * np.sin(t)

        # Rotate ellipse by angle alpha
        x_rot = xC + (x_ellipse * np.cos(alpha) - y_ellipse * np.sin(alpha))
        y_rot = yC + (x_ellipse * np.sin(alpha) + y_ellipse * np.cos(alpha))
       
        # Plot the graph
        plt.plot(x_values, y_values, '-o', label='Closed polygon')  # Line with points
        plt.fill(x_values, y_values, 'b', alpha=0.2)  # Fill closed area
        
        # Plot axes (arrows) at (xC, yC)
        plt.quiver(xC, yC, arrow_x_dx, arrow_x_dy, angles='xy', scale_units='xy', scale=1, color='r', label="Axis $x_c$")  # X-axis
        plt.quiver(xC, yC, arrow_y_dx, arrow_y_dy, angles='xy', scale_units='xy', scale=1, color='g', label="Axis $y_c$")  # Y-axis
        
        # Plot the inertia ellipse
        plt.plot(x_rot, y_rot, label="Inertia ellipse", color='b')
        
        # Plot ellipse center
        plt.plot(xC, yC, 'bo', label="Centroid")
        
        # Graph settings
        plt.title("Cross-section")
        plt.xlabel(f"$X$ [{selected_unit}]")
        plt.ylabel(f"$Y$ [{selected_unit}]")
        plt.legend()
        plt.grid(True)
        plt.axis('equal')  # Preserve axis ratio for correct display

        plt.show()

        now = datetime.now()  # Get current date and time
        date_time_str = now.strftime("%d-%m-%Y %H:%M:%S")

        """
        # Print calculation results #################################################
        """
        self.append_output(f'##### Moment of Inertia Calculation ({date_time_str}) #####')
        self.append_output('# Cross-section defined by closed polygon:')
        self.append_output(f'X [{selected_unit}]\tY [{selected_unit}]')
        for row in range(num_rows):
            self.append_output(f'{x_values[row]}\t{y_values[row]}')
        self.append_output('# Calculation results:')
        self.append_output(f'Cross-sectional area\t\tA =\t{to_engineering_notation(A)}\t{selected_unit}^2')
        self.append_output(f'Centroid X-coordinate\t\tX_C =\t{to_engineering_notation(xC)}\t{selected_unit}')
        self.append_output(f'Centroid Y-coordinate\t\tY_C =\t{to_engineering_notation(yC)}\t{selected_unit}')
        self.append_output(f'Moment of inertia about centroidal axis\tI_x =\t{to_engineering_notation(Ix)}\t{selected_unit}^4')
        self.append_output(f'Moment of inertia about centroidal axis\tI_y =\t{to_engineering_notation(Iy)}\t{selected_unit}^4')
        self.append_output(f'Deviation moment about centroidal axes\tI_xy =\t{to_engineering_notation(Ixy)}\t{selected_unit}^4')
        self.append_output(f'Principal axis orientation angle\t\talpha_p =\t{to_engineering_notation(alpha*180/np.pi)}\tdeg')
        self.append_output(f'Principal moment of inertia\t\tI_xp =\t{to_engineering_notation(IxC)}\t{selected_unit}^4')
        self.append_output(f'Principal moment of inertia\t\tI_yp =\t{to_engineering_notation(IyC)}\t{selected_unit}^4')
        self.append_output(f'Radius of gyration of cross-section\ti_xp =\t{to_engineering_notation(ixc)}\t{selected_unit}')
        self.append_output(f'Radius of gyration of cross-section\ti_yp =\t{to_engineering_notation(iyc)}\t{selected_unit}')
        self.append_output(' ')


        # Save x and y values as class attributes for access in save_to_csv and other functions
        self.x_values = x_values
        self.y_values = y_values
    
        # Save calculation results as class attributes for access in save_to_csv and other functions
        self.A, self.xC, self.yC = A, xC, yC
        self.Ix, self.Iy, self.Ixy = Ix, Iy, Ixy
        self.IxC, self.IyC, self.alpha = IxC, IyC, alpha
        self.ixc, self.iyc = ixc, iyc
        self.date_time_str = date_time_str
       


    def save_to_csv(self):
        # Název souboru
        file_name = "results.csv"
    
        # Získání jednotky pro popisek ve výstupu
        selected_unit = self.get_selected_unit()
    
        try:
            with open(file_name, mode='w', newline='') as file:
                writer = csv.writer(file, delimiter=';', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        
                # Zápis záhlaví a základních informací
                writer.writerow(['Moment of Inertia Calculation'])
                writer.writerow(['Date and Time:', self.date_time_str])
                writer.writerow(['Selected Unit:', selected_unit])
                writer.writerow([])
            
                # Výpis souřadnic průřezu
                writer.writerow(['Cross-section defined by closed polygon:'])
                writer.writerow(['X [{}]'.format(selected_unit), 'Y [{}]'.format(selected_unit)])
                for x, y in zip(self.x_values, self.y_values):
                    writer.writerow([x, y])
                writer.writerow([])
            
                # Výsledky výpočtu
                writer.writerow(['Results:'])
                writer.writerow(['Area A', to_engineering_notation(self.A), f"{selected_unit}^2"])
                writer.writerow(['Centroid X-coordinate X_C', to_engineering_notation(self.xC), selected_unit])
                writer.writerow(['Centroid Y-coordinate Y_C', to_engineering_notation(self.yC), selected_unit])
                writer.writerow(['Moment of inertia I_x', to_engineering_notation(self.Ix), f"{selected_unit}^4"])
                writer.writerow(['Moment of inertia I_y', to_engineering_notation(self.Iy), f"{selected_unit}^4"])
                writer.writerow(['Deviation moment I_xy', to_engineering_notation(self.Ixy), f"{selected_unit}^4"])
                writer.writerow(['Principal axis angle alpha_p', to_engineering_notation(self.alpha * 180 / np.pi), 'degrees'])
                writer.writerow(['Principal inertia I_xp', to_engineering_notation(self.IxC), f"{selected_unit}^4"])
                writer.writerow(['Principal inertia I_yp', to_engineering_notation(self.IyC), f"{selected_unit}^4"])
                writer.writerow(['Radius of gyration i_xp', to_engineering_notation(self.ixc), selected_unit])
                writer.writerow(['Radius of gyration i_yp', to_engineering_notation(self.iyc), selected_unit])

            QMessageBox.information(self, "Success", f"Results saved to {file_name}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not save file: {e}")


        
#Application
app = QApplication([])
window = MainWindow()
window.show()
sys.exit(app.exec_())
