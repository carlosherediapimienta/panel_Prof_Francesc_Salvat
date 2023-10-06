##### DCM file reading program
##### Authors: Carlos Heredia & Francesc Salvat 
##### University: Universitat de Barcelona, ICCUB

### Packages 
from email import header
from math import cos
from operator import ilshift, index
from textwrap import indent
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


## 
#  Main program
## 

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
        print("Error: Invalid atomic mass. Please enter a valid atomic mass")

### Projectile type and atomic mass (EV)
atomic_mass_unit = 9.314940954e8 # Unified atomic mass unit (eV)
while True:
    projectile_type = input('Select the type of projectile ("p" = proton or "a" = alpha particles): ').strip()
    if projectile_type == "p":
        mass_projectile = 1.007276466874e-6 * atomic_mass_unit # Proton mass (MeV)
        projectile_type_dat = str.upper(projectile_type)
        break
    elif projectile_type == "a":
        mass_projectile = 4.001506179127e-6 * atomic_mass_unit # Alpha mass (MeV)
        projectile_type_dat = projectile_type
        break
    else:
        print("The projectile type is incorrect. Please try again.")


### We ask the user to enter the path to read all files beginning with T(element)(atomicmass)-*.dat 
base_path = input(f"Enter the address of the directory where the {element.symbol}{atomic_mass} theoretical data are located: ").strip()
pattern = f"T{projectile_type_dat}{element.symbol}{atomic_mass}-*.dat"
file_path = glob.glob(os.path.join(base_path, pattern))

theoretical_extracted_data = []  

for file in file_path:
    file_id = os.path.basename(file).split("-")[-1].replace("MEV.dat", "") # We keep the energy that the user wants to study as id. 
    if "p" in file_id: # There may be cases where the files have decimals. For example, 179p3. This means, 179.3. We only accept one decimal place. 
        file_id = file_id.replace("p", ".")
    extracted_data = extract_data(file, file_id)
    theoretical_extracted_data.extend(extracted_data)

theoretical_data_df = pd.DataFrame(theoretical_extracted_data, columns=['E (MEV)', 'Theta (deg)','MU','DCS (cm^2/sr)','DCS-Ruth (cm^2/sr)'])
theoretical_data_df = theoretical_data_df.drop('MU', axis=1)


###### READING E*.csv
### The same as explained above but for data coming from the csv. 
csv_path = input(f"Enter the directory address where the experimental data for {element.symbol}{atomic_mass} is located: ").strip()
pattern_csv = f"E{projectile_type_dat}{element.symbol}{atomic_mass}-*.csv"
csv_files = glob.glob(os.path.join(csv_path, pattern_csv))

experimental_extracted_csv_data =[]

for csv in csv_files:
    csv_id = os.path.basename(csv).split("-")[-1].replace("MEV.csv", "")  # Extract the file_id from the filename
    if "p" in csv_id:
        csv_id = csv_id.replace("p", ".")
    extracted_data_csv = read_csv(csv, csv_id)
    experimental_extracted_csv_data.append(extracted_data_csv)

# After extracting the data:
if len(experimental_extracted_csv_data) > 0:
    new_columns={"author1": "Author","year1": "Year","y": "DCS_Lab (b/sr)", "x4(deg)": "Theta_Lab (deg)", "x2(eV)": "E (eV)"}    
    for df_idx, df in enumerate(experimental_extracted_csv_data):
        df.rename(columns=new_columns, inplace=True) # We rename the columns to be more familiar with the notation. 
        if "DCS_Lab (b/sr)" in df.columns:
            df['DCS_Lab (b/sr)'] *= 1e-24 # Multiply the "y" (DCS) column by 10^(-24): B/SR --> cm^2/SR
            df = df.rename(columns={'DCS_Lab (b/sr)': 'DCS_Lab (cm^2/sr)'})
        if "E (eV)" in df.columns:
            df["E (eV)"]*= 1e-6 # From eV --> MeV
            df["E (eV)"] = round(df["E (eV)"],1) # If it has more than one decimal place, we keep the first decimal place by rounding up. 
            df["E (eV)"] = df["E (eV)"].astype(str).apply(lambda x: x.split('.0')[0] if x.endswith('.0') else x) # If the result is, for example, 45.0, we are left with only 45
            df.rename(columns={"E (eV)": "E (MEV)"}, inplace=True)
        if "y:Value" in df.columns:
            df = df[df["y:Value"] == "Data(B/SR)"] #We delete the data that we don't want.

### IMPORTANT: This part is very important! Note that we filter the values with the identifier of the energy to be studied. 
### There may be cases where there is more than one energy in the csv. You also have to keep in mind that the value to be used 
### with the identifier has to match the rounded energy value, otherwise it will not be discarded. For this reason, it is very important 
### to name the file with the correct energy to one decimal place, and if it has two decimal places, round it up.
            df = df[df["E (MEV)"] == df["csv_id"]] 
        columns_to_keep=["Author","Year","DCS_Lab (cm^2/sr)", "Theta_Lab (deg)", "E (MEV)"]
        df=df[columns_to_keep]

        experimental_extracted_csv_data[df_idx] = df
else:
    print("No CSV data found.")
    sys.exit()

# Gather all the dataframes in one
experimental_data_df = pd.concat(experimental_extracted_csv_data, ignore_index=True)

atomic_mass_dat = atomic_mass
atomic_mass *= atomic_mass_unit*1e-6 #Atomic mass in MeV
speed_light = 137.035999139 ### Speed of light (1/alpha); in this context, alpha = fine-structure constant (Hartree atomic units)

experimental_data_df['Theta_Lab (rad)'] = np.deg2rad(experimental_data_df['Theta_Lab (deg)'])
experimental_data_df["E (MEV)"] = experimental_data_df["E (MEV)"].astype("float64")

aux1 = np.sqrt(experimental_data_df["E (MEV)"]*(experimental_data_df["E (MEV)"] + 2*mass_projectile*speed_light**2))
aux2 = experimental_data_df["E (MEV)"] + mass_projectile*speed_light**2 + atomic_mass*speed_light**2
experimental_data_df["Beta_CM"] = aux1 / aux2
                                                                                                                                                   
experimental_data_df["Gamma_CM"]= np.sqrt(1/(1-experimental_data_df["Beta_CM"]**2))
experimental_data_df["Tau"]= np.sqrt((1-experimental_data_df["Beta_CM"]**2)*(mass_projectile/atomic_mass)**2 + experimental_data_df["Beta_CM"]**2)

experimental_data_df["E (MEV)"] = experimental_data_df["E (MEV)"].astype(str).apply(lambda x: x.split('.0')[0] if x.endswith('.0') else x) #We don't need it to compute anything else, therefore, we recover it as a string value

def theta_CM(exp_df):
     cosine_theta_denom = exp_df["Gamma_CM"]**2*np.sin(exp_df["Theta_Lab (rad)"])**2 + np.cos(exp_df["Theta_Lab (rad)"])**2

     aux1 = -exp_df["Tau"]*exp_df["Gamma_CM"]**2*np.sin(exp_df['Theta_Lab (rad)'])**2
     aux2= np.cos(exp_df['Theta_Lab (rad)'])**2 + exp_df['Gamma_CM']**2*(1-exp_df['Tau']**2)*np.sin(exp_df['Theta_Lab (rad)'])**2
     aux3 = np.cos(exp_df["Theta_Lab (rad)"])*np.sqrt(aux2)

     if exp_df["Tau"] < 1:
       cosine_theta_num_p = aux1  + aux3
       theta_CM_m = 0
     elif exp_df["Tau"] >= 1:
       cosine_theta_num_m = aux1 - aux3
       cosine_theta_num_p = aux1 + aux3
       theta_CM_m = np.arccos(cosine_theta_num_m / cosine_theta_denom)     
     theta_CM_p = np.arccos(cosine_theta_num_p / cosine_theta_denom)

     return theta_CM_m, theta_CM_p

experimental_data_df[["Theta_CM_m (deg)","Theta_CM_p (deg)"]] = np.degrees(experimental_data_df.apply(lambda row: pd.Series(theta_CM(row)), axis=1))

def DCS_CM(exp_df):
    aux1 =(exp_df["Gamma_CM"]**2*np.sin(exp_df["Theta_Lab (rad)"])**2 + np.cos(exp_df["Theta_Lab (rad)"])**2)**2
    aux2 = np.sqrt(np.cos(exp_df['Theta_Lab (rad)'])**2 + exp_df['Gamma_CM']**2*(1-exp_df['Tau']**2)*np.sin(exp_df['Theta_Lab (rad)'])**2) 
    Jacobian_num =  aux1*aux2
        
    aux1 = exp_df["Tau"]*np.cos(exp_df["Theta_Lab (rad)"]) 
    aux2 = np.sqrt(np.cos(exp_df['Theta_Lab (rad)'])**2 + exp_df['Gamma_CM']**2*(1-exp_df['Tau']**2)*np.sin(exp_df['Theta_Lab (rad)'])**2)
    if exp_df["Tau"] < 1:
       aux3 = aux1 + aux2
       Jacobian_denom = exp_df["Gamma_CM"]**2*aux3**2                                                                                                        
    elif exp_df["Tau"] >= 1:
       aux3 = aux1 - aux2
       Jacobian_denom_m = exp_df["Gamma_CM"]**2*aux3**2

       aux3 = aux1+aux2
       Jacobian_denom_p = exp_df["Gamma_CM"]**2*aux3**2

       Jacobian_denom = Jacobian_denom_m + Jacobian_denom_p
    DCS_CM = np.abs(Jacobian_num/Jacobian_denom)*exp_df["DCS_Lab (cm^2/sr)"]
    return DCS_CM

experimental_data_df["DCS_CM (cm^2/sr)"] = experimental_data_df.apply(DCS_CM, axis=1)

 ## Data is writen into a .dat file
for mev_value in experimental_data_df['E (MEV)'].unique():
    mev_p = str(mev_value).replace(".", "p")
    pattern_dat = f"E{projectile_type_dat}{element.symbol}{atomic_mass_dat}-{mev_p}MEV.dat"
    dat_path_write = os.path.join(csv_path, pattern_dat) 
    
    experimental_data_df_mev = experimental_data_df[experimental_data_df['E (MEV)']== mev_value]
    experimental_data_df_mev = experimental_data_df_mev[["Theta_CM_p (deg)", "DCS_CM (cm^2/sr)","Author", "Year", "Theta_CM_m (deg)"]]

    experimental_data_df_mev["Theta_CM_p (deg)"] = experimental_data_df_mev["Theta_CM_p (deg)"].apply(lambda x: "{:.3f}".format(x))
    experimental_data_df_mev["Theta_CM_m (deg)"] = experimental_data_df_mev["Theta_CM_m (deg)"].apply(lambda x: "{:.3f}".format(x))
    experimental_data_df_mev["DCS_CM (cm^2/sr)"] = experimental_data_df_mev["DCS_CM (cm^2/sr)"].apply(lambda x: "{:.5e}".format(x))

    experimental_data_df_mev.to_csv(dat_path_write, sep='\t', index=False)

# Maximum value of theta
just_in_case = 10 #To take a wide range, just in case.
max_theta = int(max(experimental_data_df['Theta_CM_p (deg)']) + just_in_case)

# Create a unique list of MEV values
unique_mev_values = sorted(list(set(theoretical_data_df['E (MEV)']).union(set(experimental_data_df['E (MEV)'].astype(str)))),key=lambda x: float(x))

# Ploting 
# Create a plot for all MEV values
plt.figure()  # Create a single figure for the entire plot
plt.title(f"{element.symbol}$^{{{atomic_mass_dat}}}$, elastic")

# Diferent types of markers
csv_marker_size = 5

# Lines
line_width = 1.5

# Colours
color_palette = plt.colormaps['tab10']
color_iterator = iter(color_palette(np.linspace(0, 1, len(unique_mev_values))))


for idx, mev in enumerate(unique_mev_values):
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
    
    
    experimental_data_df_filtered = experimental_data_df.loc[(experimental_data_df['E (MEV)'] == mev) & (1<= experimental_data_df['Theta_CM_p (deg)']) & (experimental_data_df['Theta_CM_p (deg)'] <= max_theta)]
    theoretical_data_df_filtered = theoretical_data_df.loc[(theoretical_data_df['E (MEV)'] == mev) & (1<= theoretical_data_df['Theta (deg)']) & (theoretical_data_df['Theta (deg)']<= max_theta)]

    experimental_data_df_filtered.loc[:,'DCS_CM (cm^2/sr)'] *= 10**power_of_10
    theoretical_data_df_filtered.loc[:,"DCS (cm^2/sr)"] *= 10**power_of_10

    color = next(color_iterator)

    plt.plot(experimental_data_df_filtered["Theta_CM_p (deg)"],experimental_data_df_filtered["DCS_CM (cm^2/sr)"], marker='x', markersize=csv_marker_size, linestyle='None', color=color, label= label_exp)
    plt.plot(theoretical_data_df_filtered["Theta (deg)"], theoretical_data_df_filtered['DCS (cm^2/sr)'], linewidth=line_width, color=color, label= label_teoria)

plt.xlabel('$\\theta$ (deg)')
plt.ylabel('d$\sigma$/d$\Omega$  $(cm^2/sr)$')
plt.legend()

## The minimum value 1 is because at 0, it blows up and does not need to be analyzed. 
plt.xlim(1,max_theta)
plt.yscale('log')
plt.grid()

plt.show()  # Display the combined plot

################
###### Comparison with other optical potential:
################

while True:
    answer_comparison = input('Do you want to compare it with another optical potential? Yes (Y) or No (N): ').strip()
    if answer_comparison == "Y":
        break
    elif answer_comparison == "N":
        print('Ok! Bye :)')
        sys.exit()
    else:
        print("The answer is incorrect. Please try again.")

### We ask the user to enter the path to read all files beginning with T(element)(atomicmass)-*.dat 
base_path = input(f"Enter the address of the directory where the {element.symbol}{atomic_mass_dat} theoretical data are located with another optical potencial: ").strip()
pattern = f"T{projectile_type_dat}{element.symbol}{atomic_mass_dat}-*.dat"
file_path = glob.glob(os.path.join(base_path, pattern))

theoretical_extracted_data = []  

for file in file_path:
    file_id = os.path.basename(file).split("-")[-1].replace("MEV.dat", "") # We keep the energy that the user wants to study as id. 
    if "p" in file_id: # There may be cases where the files have decimals. For example, 179p3. This means, 179.3. We only accept one decimal place. 
        file_id = file_id.replace("p", ".")
    extracted_data = extract_data(file, file_id)
    theoretical_extracted_data.extend(extracted_data)

theoretical_data_df_V2 = pd.DataFrame(theoretical_extracted_data, columns=['E (MEV)', 'Theta (deg)','MU','DCS (cm^2/sr)','DCS-Ruth (cm^2/sr)'])
theoretical_data_df_V2 = theoretical_data_df_V2.drop('MU', axis=1)

theoretical_data_df_V2 = theoretical_data_df_V2[theoretical_data_df_V2['E (MEV)'] == theoretical_data_df['E (MEV)']]

plt.figure()  # Create a single figure for the entire plot
plt.title(f"{element.symbol}$^{{{atomic_mass_dat}}}$, elastic")
color_iterator = iter(color_palette(np.linspace(0, 1, len(unique_mev_values))))

for idx, mev in enumerate(unique_mev_values):
    # We multiply it by powers of 10 for better visualisation. 
    power_of_10 = len(unique_mev_values) - idx - 1

    label_teoria = f'Theor. data (E = {mev} MeV)'
    if power_of_10 == 0:
        label_teoria += ''
    elif power_of_10 == 1:
        label_teoria += f' $\\times 10$'
    else:
        label_teoria += f' $\\times 10^{{{power_of_10}}}$'

    label_teoria_2nd = f'Theor. data 2nd opt. (E = {mev} MeV)'
    if power_of_10 == 0:
        label_teoria_2nd += ''
    elif power_of_10 == 1:
        label_teoria_2nd += f' $\\times 10$'
    else:
        label_teoria_2nd += f' $\\times 10^{{{power_of_10}}}$'
        
    
    label_exp = f'Exp. data (E = {mev} MeV)'
    if power_of_10 == 0:
        label_exp += ''
    elif power_of_10 == 1:
        label_exp += f' $\\times 10$'
    else:
        label_exp += f' $\\times 10^{{{power_of_10}}}$'
    
    
    experimental_data_df_filtered = experimental_data_df.loc[(experimental_data_df['E (MEV)'] == mev) & (1<= experimental_data_df['Theta_CM_p (deg)']) & (experimental_data_df['Theta_CM_p (deg)'] <= max_theta)]
    theoretical_data_df_filtered = theoretical_data_df.loc[(theoretical_data_df['E (MEV)'] == mev) & (1<= theoretical_data_df['Theta (deg)']) & (theoretical_data_df['Theta (deg)']<= max_theta)]
    theoretical_data_df_filtered_V2 = theoretical_data_df_V2.loc[(theoretical_data_df_V2['E (MEV)'] == mev) & (1<= theoretical_data_df_V2['Theta (deg)']) & (theoretical_data_df_V2['Theta (deg)']<= max_theta)]

    experimental_data_df_filtered.loc[:,'DCS_CM (cm^2/sr)'] *= 10**power_of_10
    theoretical_data_df_filtered.loc[:,"DCS (cm^2/sr)"] *= 10**power_of_10
    theoretical_data_df_filtered_V2.loc[:,"DCS (cm^2/sr)"] *= 10**power_of_10

    color = next(color_iterator)

    plt.plot(experimental_data_df_filtered["Theta_CM_p (deg)"],experimental_data_df_filtered["DCS_CM (cm^2/sr)"], marker='x', markersize=csv_marker_size, linestyle='None', color=color, label= label_exp)
    plt.plot(theoretical_data_df_filtered["Theta (deg)"], theoretical_data_df_filtered['DCS (cm^2/sr)'], linewidth=line_width, color=color, label= label_teoria)
    plt.plot(theoretical_data_df_filtered_V2["Theta (deg)"], theoretical_data_df_filtered_V2['DCS (cm^2/sr)'], linestyle="--", linewidth=line_width, color=color, label= label_teoria_2nd)

plt.xlabel('$\\theta$ (deg)')
plt.ylabel('d$\sigma$/d$\Omega$  $(cm^2/sr)$')
plt.legend()

## The minimum value 1 is because at 0, it blows up and does not need to be analyzed. 
plt.xlim(4,max_theta)
plt.yscale('log')
plt.grid()

plt.show()  # Display the combined plot