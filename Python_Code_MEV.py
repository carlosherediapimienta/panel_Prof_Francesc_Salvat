##### DCM file reading program
##### Authors: Carlos Heredia & Francesc Salvat 
##### University: Universitat de Barcelona, ICCUB

### Packages 
import matplotlib.pyplot as plt
import pandas as pd
import glob
import os
import numpy as np

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

##### READING calcDCS_*.dat

# Define the pattern to search for .dat files in a specific location
base_path = input("Enter the directory address where the theoretical data for Si28 is located:")
pattern = "calcDCS_*.dat"
dat_files = glob.glob(os.path.join(base_path, pattern))

all_extracted_data = []  # To store extracted data from all files

for file in dat_files:
    file_id = file.split('calcDCS_')[1].replace('MEV.dat', '')  # Extract the file_id from the filename
    extracted_data = extract_data(file, file_id)
    all_extracted_data.extend(extracted_data)

MEV_values = [row['E (MEV)'] for row in all_extracted_data]
theta_values = [row['Theta (deg)'] for row in all_extracted_data]
mu_values = [row['MU'] for row in all_extracted_data]
dcs_values = [row['DCS (cm^2/sr)'] for row in all_extracted_data]
dcs_ruth_values = [row['DCS-Ruth (cm^2/sr)'] for row in all_extracted_data]

###### READING Si28_*.csv
csv_path = input("Enter the directory address where the experimental data for Si28 is located:")
pattern_csv = "Si28_*.csv"
csv_files = glob.glob(os.path.join(csv_path, pattern_csv))

all_extracted_csv_data =[]

for csv in csv_files:
    csv_id = csv.split('Si28_')[1].replace('MEV.csv', '')  # Extract the file_id from the filename
    extracted_data_csv = read_csv(csv, csv_id)
    all_extracted_csv_data.append(extracted_data_csv)

# After extracting the data:
if len(all_extracted_csv_data) > 0:
    new_columns={"y": "DCS (cm^2/sr)", "x4(deg)": "Theta (deg)", "x2(eV)": "E (eV)"}    
    for df_idx, df in enumerate(all_extracted_csv_data):
        df.rename(columns=new_columns, inplace=True)
        if "DCS (cm^2/sr)" in df.columns:
         # Multiply the "y" (DCS) column by 10^(-24): B/SR --> cm^2/SR
            df['DCS (cm^2/sr)'] *= 10 ** (-24)
        if "E (eV)" in df.columns:
        # From eV --> MeV
            df["E (eV)"]*= 10 ** (-6)
#            df["E (eV)"] = df["E (eV)"].astype(int).astype(str).str.rstrip('.0')
            df["E (eV)"] = df["E (eV)"].astype(int).astype(str)
            df.rename(columns={"E (eV)": "E (MEV)"}, inplace=True)
            df = df[df["E (MEV)"] == df["csv_id"]]
        all_extracted_csv_data[df_idx] = df
else:
    print("No CSV data found.")

# Gather all the dataframes in one and then transform it into a list.
all_extracted_csv_data = pd.concat(all_extracted_csv_data, ignore_index=True).to_dict(orient='records')    

# Exctrating the desire information
MEV_values_csv = [row['E (MEV)'] for row in all_extracted_csv_data]
theta_values_csv = [row['Theta (deg)'] for row in all_extracted_csv_data]
dcs_values_csv = [row['DCS (cm^2/sr)'] for row in all_extracted_csv_data]

# Create a unique list of MEV values
unique_mev_values = list(set(MEV_values + MEV_values_csv))

# Create a plot for all MEV values
plt.figure()  # Create a single figure for the entire plot
plt.title("Si$^{28}$, elastic")

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
    # Filter values corresponding to each MEV value
    theta_values_filtered = [theta for theta, e in zip(theta_values, MEV_values) if e == mev]
    dcs_values_filtered = [dcs for dcs, e in zip(dcs_values, MEV_values) if e == mev]
    theta_values_csv_filtered = [theta for theta, e in zip(theta_values_csv, MEV_values_csv) if e == mev]
    dcs_values_csv_filtered = [dcs for dcs, e in zip(dcs_values_csv, MEV_values_csv) if e == mev]
    
    csv_marker = next(csv_marker_iterator)
    color = next(color_iterator)

    # Plot values for each dataset with appropriate markers and labels
    plt.plot(theta_values_filtered, dcs_values_filtered, linewidth=line_width, color = color, label=f'Theor. data (E = {mev} MeV)')
    plt.plot(theta_values_csv_filtered, dcs_values_csv_filtered, marker=csv_marker, markersize = csv_marker_size, linestyle='None',color = color, label=f'Exp. data (E = {mev} MeV)')

plt.xlabel(r'$\theta$ (deg)')
plt.ylabel('d$\sigma$/d$\Omega$  $(cm^2/sr)$')
plt.legend()
plt.yscale('log')
plt.xlim(0, 100)
plt.grid()

plt.show()  # Display the combined plot






