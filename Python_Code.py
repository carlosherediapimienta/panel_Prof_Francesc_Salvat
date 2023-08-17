##### DCM file reading program
##### Authors: Carlos Heredia & Francesc Salvat 
##### University: Universitat de Barcelona, ICCUB

### Packages 
import matplotlib.pyplot as plt
import pandas as pd

### To use Latex in python
plt.rcParams['text.usetex'] = True
plt.rcParams['text.latex.preamble'] = r'\usepackage{amsmath}'

### Functions definitions:


# Reading and extracting function .csv
def read_csv(file_path):
    try:
        data = pd.read_csv(file_path)
        return data
    except FileNotFoundError:
        return "File not found."
    except Exception as e:
        return f"An error occurred: {e}"

### Reading and extracting function calcDCS
def extract_data(file_path):
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

##### READING calcDCS_45MEV.dat
file_path = "C:\\Users\\test\\Desktop\\Carlos Heredia\\panel\\Carlos_Program\\calcDCS_45MEV.dat"
extracted_data = extract_data(file_path)


##### READING CSV
csv_file_path = "C:\\Users\\test\\Desktop\\Carlos Heredia\\panel\\Carlos_Program\\Si28.csv"
csv_data = read_csv(csv_file_path)


# After extracting the data:

# From CSV
if isinstance(csv_data, pd.DataFrame):
    # Multiply the "dy" column by 10^(-24): B/SR --> cm^2/SR
    csv_data["y"] *= 10 **(-24)
    
    # Rename the columns
    csv_data.rename(columns={"y": "DCS (cm^2/SR)", "x4(deg)": "Theta (deg)"}, inplace=True)
else:
    print("CSV Error")

# From calcDCS
theta_values = [row['Theta (deg)'] for row in extracted_data]
mu_values = [row['MU'] for row in extracted_data]
dcs_values = [row['DCS (cm^2/sr)'] for row in extracted_data]
dcs_ruth_values = [row['DCS-Ruth (cm^2/sr)'] for row in extracted_data]


# Calculate the ratio between "DCS" and "DCS-Ruth"
dcs_ratio = [dcs / dcs_ruth for dcs, dcs_ruth in zip(dcs_values, dcs_ruth_values)]

# Create a figure with two subplots
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))

# Plot "Theta (deg)" vs "DCS" on a logarithmic y-axis
ax1.plot(theta_values, dcs_ratio, label="d$\sigma$ / d$\sigma_{Ruth}$")
ax1.set_xlabel(r"$\theta$ (deg)")
ax1.set_ylabel("d$\sigma$ / d$\sigma_{Ruth}$")
ax1.set_title("d$\sigma$/d$\sigma_{Ruth}$ vs" r" $\theta$")
ax1.legend()
ax1.set_yscale('log')  # Set y-axis to logarithmic scale
ax1.grid()

# Plot "Theta (deg)" vs "DCS-Ruth" on a logarithmic y-axis
ax2.plot(theta_values, dcs_values, label="d$\sigma$/d$\Omega$", color='orange')
ax2.set_xlabel(r"$\theta$ (deg)")
ax2.set_ylabel("d$\sigma$/d$\Omega$ $(cm^2/sr)$")
ax2.set_title("d$\sigma$/d$\Omega$ vs" r" $\theta$")
ax2.legend()
ax2.set_yscale('log')  # Set y-axis to logarithmic scale
ax2.grid()


# Plot "Theta (deg)" vs "MU"
ax3.plot(mu_values, dcs_values, label="d$\sigma$/d$\Omega$", color='green')
ax3.set_xlabel("$\mu$")
ax3.set_ylabel("d$\sigma$/d$\Omega$ $(cm^2/sr)$")
ax3.set_title("d$\sigma$/d$\Omega$ vs $\mu$")
ax3.legend()
ax3.set_yscale('log')  # Set y-axis to logarithmic scale
ax3.grid()


# Adjust spacing between subplots
plt.tight_layout()

# Show the figure with both subplots
plt.show()

# Plot "DCS_Exp (cm^2/SR)" vs "Theta" on a logarithmic y-axis
plt.figure(figsize=(10, 6))
plt.scatter(csv_data["Theta (deg)"], csv_data["DCS (cm^2/SR)"], marker='x', s=10)  
plt.xlabel(r"$\theta$ (deg)")
plt.ylabel("d$\sigma$/d$\Omega$ $(cm^2/sr)$")
plt.title("d$\sigma_{Exp}$/d$\Omega$ vs" r" $\theta$")
plt.yscale('log')  # Set y-axis to logarithmic scale
plt.xlim(0, 100)
plt.grid


# Show the plot
plt.show()


### Combination of both DCS and DCS_Exp
plt.figure(figsize=(12, 6))

# Plot "DCS (cm^2/SR)" vs "Theta" with points on a logarithmic y-axis
plt.scatter(csv_data["Theta (deg)"], csv_data["DCS (cm^2/SR)"], marker='o', s=10, label="d$\sigma_{Exp}$/d$\Omega$")
plt.yscale('log')  # Set y-axis to logarithmic scale

# Plot "DCS" vs "Theta" with points
plt.plot(theta_values, dcs_values, label="d$\sigma$/d$\Omega$", color='orange')

plt.xlabel(r"$\theta$ (deg)")
plt.ylabel("d$\sigma$/d$\Omega$  $(cm^2/sr)$")
plt.title("d$\sigma_{Exp}$/d$\Omega$  and d$\sigma$/d$\Omega$ vs" r" $\theta$")
plt.legend()
plt.xlim(0, 100)
plt.grid()

# Show the plot
plt.show()



