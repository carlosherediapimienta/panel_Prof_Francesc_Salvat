#  Colaboration: Prof. Francesc Salvat (University of Barcelona)
Collaboration with Professor Francesc Salvat, University of Barcelona, Physics.

Codes:
  1. Python_Code: This code rudimentarily presents the graphs derived from theoretical data (panel program) of Si28 at 45 MeV compared to the experimental data from https://www-nds.iaea.org/exfor/.
  2. Python_Code_MEV: This code is an improvement of the Python_Code. The improvements were: a) The user is prompted to input the directory where the theoretical and experimental values are located, and the code automatically reads all of them. It's important to note that the structure of the theoretical data should be calcDCS_*MEV.dat, and the experimental data should be Si28_*MEV.csv. b) Even if the experimental data has more energy values, the code will only select those that are in the title. In other words, if we have Si28_45MEV.csv, it will only select data with an energy of 45MEV from the file. c) It plots both theoretical and experimental data together.
