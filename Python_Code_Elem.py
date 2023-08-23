##### DCM file reading program
##### Authors: Carlos Heredia & Francesc Salvat 
##### University: Universitat de Barcelona, ICCUB

### Packages 
from operator import ilshift
import matplotlib.pyplot as plt
import pandas as pd
import glob
import os
import numpy as np
from periodictable import elements
import sys

### To use Latex in python
plt.rcParams['text.usetex'] = True
plt.rcParams['text.latex.preamble'] = r'\usepackage{amsmath}'


### Functions definitions:

# Reading and extracting function .csv
def read_csv(file_path, csv_id):
    try:
        data = pd.read_csv(file_path)
        data['csv_id'] = csv_id
        return data
    except FileNotFoundError:
        return "File not found."
    except Exception as e:
        return f"An error occurred: {e}"

### Reading and extracting function calcDCS
def extract_data(file_path,file_id):
    try:
        data = []
        with open(file_path, 'r') as file:
            lines = file.readlines()

        data_started = False
        for line in lines:
            line = line.strip()
            if line.startswith("#"):
                continue  # Skip comment lines
            if not data_started:
                data_started = True # Start extracting data when a non-comment line is encountered
            if data_started:
                columns = line.split()
                if len(columns) == 4:  # Ensure there are 4 columns of data
                    theta_deg, mu, dcs, dcs_ruth = columns
                    data.append({
                        'E (MEV)': file_id,
                        'Theta (deg)': float(theta_deg),
                        'MU': float(mu),
                        'DCS (cm^2/sr)': float(dcs),
                        'DCS-Ruth (cm^2/sr)': float(dcs_ruth)
                    })

        return data
    except FileNotFoundError:
        return "File not found."
    except Exception as e:
        return f"An error occurred: {e}"


## Main program

##### READING T*.dat
### In addition, we detect whether the user is entering a correct item. We access the "elements" library
### to verify that everything is correct. If not, we ask the user to enter the element again. 
while True:
    try:
        atomic_number = int(input("Please enter the atomic number: "))
        element = elements[atomic_number]
        element_isotopes = element.isotopes
        break
    except (KeyError, ValueError):
        print("Error: Invalid atomic number. Please enter a valid atomic number.")


### The same for the atomic mass
while True:
    try:
        atomic_mass = int(input("Please enter the isotope of the element: "))
        if atomic_mass in element_isotopes:
            break
        else: 
            print("Error: Invalid atomic mass. Please enter a valid atomic mass.")
    except (KeyError, ValueError):
        print("Error: Invalid atomic mass. Please enter a valid atomic mass.")


### We ask the user to enter the path to read all files beginning with T(element)(atomicmass)-*.dat 
base_path = input(f"Enter the directory address where the theoretical data for {element.symbol}{atomic_mass} is located: ")
pattern = f"T{element.symbol}{atomic_mass}-*.dat"
dat_files = glob.glob(os.path.join(base_path, pattern))

all_extracted_data = []  

for file in dat_files:
    file_id = os.path.basename(file).split("-")[-1].replace("MEV.dat", "") # We keep the energy that the user wants to study as id. 
    if "p" in file_id: # There may be cases where the files have decimals. For example, 179p3. This means, 179.3. We only accept one decimal place. 
        file_id = file_id.replace("p", ".")
    extracted_data = extract_data(file, file_id)
    all_extracted_data.extend(extracted_data)


MEV_values = [row['E (MEV)'] for row in all_extracted_data]
theta_values = [row['Theta (deg)'] for row in all_extracted_data]
mu_values = [row['MU'] for row in all_extracted_data]
dcs_values = [row['DCS (cm^2/sr)'] for row in all_extracted_data]
dcs_ruth_values = [row['DCS-Ruth (cm^2/sr)'] for row in all_extracted_data]


###### READING E*.csv
### The same as explained above but for data coming from the csv. 
csv_path = input(f"Enter the directory address where the experimental data for {element.symbol}{atomic_mass} is located: ")
pattern_csv = f"E{element.symbol}{atomic_mass}-*.csv"
csv_files = glob.glob(os.path.join(csv_path, pattern_csv))

all_extracted_csv_data =[]

for csv in csv_files:
    csv_id = os.path.basename(csv).split("-")[-1].replace("MEV.csv", "")  # Extract the file_id from the filename
    if "p" in csv_id:
        csv_id = csv_id.replace("p", ".")
    extracted_data_csv = read_csv(csv, csv_id)
    all_extracted_csv_data.append(extracted_data_csv)

# After extracting the data:
if len(all_extracted_csv_data) > 0:
    new_columns={"y": "DCS (cm^2/sr)", "x4(deg)": "Theta (deg)", "x2(eV)": "E (eV)"}    
    for df_idx, df in enumerate(all_extracted_csv_data):
        df.rename(columns=new_columns, inplace=True) # We rename the columns to be more familiar with the notation. 
        if "DCS (cm^2/sr)" in df.columns:
            df['DCS (cm^2/sr)'] *= 10 ** (-24) # Multiply the "y" (DCS) column by 10^(-24): B/SR --> cm^2/SR
        if "E (eV)" in df.columns:
            df["E (eV)"]*= 10 ** (-6) # From eV --> MeV
            df["E (eV)"] = round(df["E (eV)"],1) # If it has more than one decimal place, we keep the first decimal place by rounding up. 
            df["E (eV)"] = df["E (eV)"].astype(str).apply(lambda x: x.split('.0')[0] if x.endswith('.0') else x) # If the result is, for example, 45.0, we are left with only 45
            df.rename(columns={"E (eV)": "E (MEV)"}, inplace=True)
        if "y:Value" in df.columns:
            df = df[df["y:Value"] != "Data(NO-DIM)"] #We delete the data that we don't want.

### IMPORTANT: This part is very important! Note that we filter the values with the identifier of the energy to be studied. 
### There may be cases where there is more than one energy in the csv. You also have to keep in mind that the value to be used 
### with the identifier has to match the rounded energy value, otherwise it will not be discarded. For this reason, it is very important 
### to name the file with the correct energy to one decimal place, and if it has two decimal places, round it up.
            df = df[df["E (MEV)"] == df["csv_id"]] 
        all_extracted_csv_data[df_idx] = df
else:
    print("No CSV data found.")
    sys.exit()

# Gather all the dataframes in one and then transform it into a list.
all_extracted_csv_data = pd.concat(all_extracted_csv_data, ignore_index=True).to_dict(orient='records')    

# Exctrating the desire information
MEV_values_csv = [row['E (MEV)'] for row in all_extracted_csv_data]
theta_values_csv = [row['Theta (deg)'] for row in all_extracted_csv_data]
dcs_values_csv = [row['DCS (cm^2/sr)'] for row in all_extracted_csv_data]

# Maximum value of theta
just_in_case = 10 #To take a wide range, just in case.
max_theta = int(max(theta_values_csv) + just_in_case)

# Create a unique list of MEV values
unique_mev_values = sorted(list(set(MEV_values + MEV_values_csv)),key=lambda x: float(x))

# Create a plot for all MEV values
plt.figure()  # Create a single figure for the entire plot
plt.title(f"{element.symbol}$^{{{atomic_mass}}}$, elastic")

# Diferent types of markers
csv_markers = ['o', 's', 'D', '^', 'v', '>', '<', 'p', 'H', 'x']
csv_marker_iterator = iter(csv_markers)
csv_marker_size = 3

# Lines
line_width = 1.5

# Colours
color_palette = plt.colormaps['tab10']
color_iterator = iter(color_palette(np.linspace(0, 1, len(unique_mev_values))))
 
for mev in unique_mev_values:
    # We multiply it by powers of 10 for better visualisation. 
    power_of_10 = len(unique_mev_values) - idx - 1

    label_teoria = f'Theor. data (E = {mev} MeV)'
    if power_of_10 == 0:
        label_teoria += ''
    elif power_of_10 == 1:
        label_teoria += f' $\\times 10$'
    else:
        label_teoria += f' $\\times 10^{{{power_of_10}}}$'
        
    
    label_exp = f'Exp. data (E = {mev} MeV)'
    if power_of_10 == 0:
        label_exp += ''
    elif power_of_10 == 1:
        label_exp += f' $\\times 10$'
    else:
        label_exp += f' $\\times 10^{{{power_of_10}}}$'
    
    # Filter values corresponding to each MEV value and max_theta
    theta_values_filtered = [theta for theta, e in zip(theta_values, MEV_values) if e == mev and 1 <= theta <= max_theta]
    dcs_values_filtered = [dcs for theta, dcs, e in zip(theta_values, dcs_values, MEV_values) if e == mev and 1 <= theta <= max_theta]
    theta_values_csv_filtered = [theta for theta, e in zip(theta_values_csv, MEV_values_csv) if e == mev and 1 <= theta <= max_theta]
    dcs_values_csv_filtered = [dcs for theta, dcs, e in zip(theta_values_csv, dcs_values_csv, MEV_values_csv) if e == mev and 1 <= theta <= max_theta]
    
    csv_marker = next(csv_marker_iterator)
    color = next(color_iterator)

    # Plot values for each dataset with appropriate markers and labels
    plt.plot(theta_values_filtered, dcs_values_filtered, linewidth=line_width, color=color, label= label_teoria)
    plt.plot(theta_values_csv_filtered, dcs_values_csv_filtered, marker=csv_marker, markersize=csv_marker_size, linestyle='None', color=color, label= label_exp)

plt.xlabel(r'$\theta$ (deg)')
plt.ylabel('d$\sigma$/d$\Omega$  $(cm^2/sr)$')
plt.legend()
plt.yscale('log')

## The minimum value 1 is because at 0, it blows up and does not need to be analyzed. 
plt.xlim(1,max_theta)
plt.grid()

plt.show()  # Display the combined plot
