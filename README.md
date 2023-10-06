#  Colaboration: Prof. Francesc Salvat (University of Barcelona)
Collaboration with Professor Francesc Salvat, University of Barcelona, Physics.

Article that refers: "Electromagnetic interaction models for Monte Carlo simulation of protons and alpha particles", arXiv: 2310.03357 [nucl-th]

Information Code: 

Nanme of the program: Article_Python_Code. This code presents the graphs derived from theoretical data (Panel --PENELOPE-- program) compared to the experimental data extracted from https://www-nds.iaea.org/exfor/
The user is prompted to input:
  1. The atomic number that are impacted by either the proton or the alfa particle.
  2.  The isotope number.
  3.   The type of projectile. For protons "P" and for alphas "a".
  4.   The directory where the theoretical and experimental values are located, and the code automatically reads all of them. It's important to note that the structure of the theoretical data must be T{type_particle}{Element}_{Energy}MEV.dat, and the experimental data must be E{type_particle}{Element}_{Energy}MEV.csv, where "type_particle" means the type of projectitle, and "Energy" referes to the projectile energy value. Even if the experimental data has more energy values, the code will only select those that are in the title. In other words, if we have a proton projectile and Si28, TPSi28_45MEV.dat and EPSi28_45MEV.csv, it will only select data with an energy of 45MEV from the file. On the other hand, it only contemplates energies with one decimal place, so if you have more decimals, the user will previously have to round up to one decimal place. The decimal must be represented by the letter "p" and not by the dot "." For example, if we have "45.65MEV", we would have to write "45p7MEV".

Then, it plots both theoretical and experimental data together. Once the graph is plotted, it gives you the option to compare it with another optical potential (indicating, by means of an input, the path where the new theoretical values with this potential are located). and plots those values on the same graph as before. 

Important observation: In the experimental data only those with "B/SR" units are selected, all those with different units are excluded. 
