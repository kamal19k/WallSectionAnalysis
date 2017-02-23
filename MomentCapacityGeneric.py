import datetime
import os
import subprocess
import time
import numpy as np

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

import WallDimensionsGeneric

''' Functions'''


class Plotter:
    def __init__(self, a, b):
        plt.close()
        fig = plt.figure()
        fig.add_subplot(111)
        if type(a) is str or type(b) is str:
            print "ERROR! The data entered for plotting are of type string!"
        if isinstance(a, float):
            plt.plot(a, b, 'bo', ms=16)
        elif isinstance(a, list):
            plt.plot(a, b)
            plt.plot([-0.003, -0.003], [0, max(b)], 'k', dashes=(5, 2))
        elif all(isinstance(el, list) for el in a):
            assert isinstance(b, list)
            for k, j in zip(a, b):
                plt.plot(k, j)
                plt.plot([-0.003, -0.003], [0, max(b[-1])], 'k', dashes=(5, 2))
        else:
            plt.plot(a, b, 'bo', ms=16)

        plt.xlabel('Strain, ft/ft')
        plt.ylabel('Moment, k-ft')
        pp.savefig(fig)


''' Enter the following information: '''
phi = 0.9  # Flexural reduction factor
L = 30.0 * 12.0  # length of the shear wall [in.]
t_w = 2.0 * 12.0  # thickness (width) of the shear wall [in.]
L_be = 54.  # length of Boundary Element [in.]
boundary_column = 10  # no. of cols in BE
axial_load = -1065.0  # axial load (negative is compression)
compStrain = -0.003  # Strain at which capacity measured
steel_max = np.arange(0.01, 0.03, .003)

day = str(datetime.datetime.today().date())
pref = 'UnPunched_ELF_Dmax_secB2_' + day + '/'  # This is the name of Folder will be created
# pref = 'Punched50_ELF_pier_' + day + '/'  # This is the name of Folder will be created
path = 'C:/Users/kamal2/Google Drive/2015_ATC_123_Research_Tsenguun_Kamal/Final Design/' \
       '8 Story Building/Dmax/Design Trials/' + pref
if not os.path.exists(path):
    os.makedirs(path)
filename = path + 'steel_data.txt'
# close file:
subprocess.Popen('TASKKILL /IM notepad.exe')
# remove the previous file
if os.path.isfile(filename):
    os.remove(filename)

# print "Number of Runs = %.0f \n" % (len(L) * len(t_w) * len(L_be))
boundary_row = 3
if boundary_row == 2:
    boundary_middle_row = 'None'  # no boundary middle rows are available
elif boundary_row > 2:
    # boundary_middle_row = 'equal'   # using the same no of bars in the middle row as the top & bottom rows
    boundary_middle_row = 'two'  # Only using 2 bars in the middle row (at the ends)

S, M = [], []
# for i in range(len(L)):
#     for ii in range(len(t_w)):
for k in range(len(steel_max)):
    # for t in range(len(L_be)):
    strain, moment, moment_ft = [], [], []
    print ("New Section: \n")
    a = WallDimensionsGeneric.Moment_capacity(wall_depth=L,  # wall length
                                              wall_width=t_w,  # wall thickness
                                              boundary_depth=L_be,  # length of BE
                                              steel_max=steel_max[k],  # max steel
                                              boundary_row=3,  # no of rows in BE
                                              boundary_column=boundary_column,  # no of cols in BE
                                              cover=3.0,  # concrete cover
                                              boundary_middle_row=boundary_middle_row,
                                              fc=5,  # concrete compressive strength
                                              axial_load=axial_load,
                                              fn=filename,
                                              path=path)  # axial load
    # insert a function here to do calcs
    inf = open("Data/StressStrain_ExtComp.out")
    inf2 = np.loadtxt("Data/StressStrainTensionSteel.out")
    for number, l in enumerate(inf, 1):
        if l in ['\n', '\r\n']:
            break
        else:
            g = l.split()
            strain.append(float(g[2]))  # strain is the 3rd col in the file
    index = 0
    while strain[index] > compStrain and index < len(strain) - 1:
        # print index, strain[index], len(strain)
        index += 1
    inf3 = open("Data/Mphi.out")
    inf4 = np.loadtxt("Data/Mphi.out")
    print max(inf4[:, 0])
    for num, l2 in enumerate(inf3):
        if l2 in ['\n', '\r\n']:
            break
        else:
            g = l2.split()
            moment.append(float(g[0]))  # moment is the 1st col in the file
            moment_ft.append(float(g[0]) / 12.0)  # moment in k-ft
    print index
    c_moment = moment[index] * phi / 12.0
    # strain_steel = inf2[index][2]
    S.append(strain)
    M.append(moment_ft)
    pp = PdfPages(path + 'moment_strain_plots.pdf')
    for i in range(len(S)):
        Plotter(S[i], M[i])
    Plotter(compStrain, c_moment)
    infile = open(filename, 'a')
    if index < len(strain) - 1:
        infile.write("phiMn = Factored moment capacity at max. compressive strain of %.3f is %.1f kip-ft\n"
                     % (compStrain, c_moment))
        infile.write("Tensile strain in the extreme steel bar = %f\n" % inf2[index][2])
    else:
        infile.write("phiMn = Factored moment capacity at max. compressive strain of %.3f is %.1f kip-ft\n"
                     % (strain[len(strain) - 1], c_moment))
        # infile.write("Tensile strain in the extreme steel bar = %f\n" % inf2[len(strain)-1][2])
    infile.write("\n")
    infile.write("|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||\n\n\n\n\n\n")
    infile.close()

pp.close()
print "||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||"
print "                               Job Completed Successfully!"
print "||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||"

subprocess.Popen([filename], shell=True)
