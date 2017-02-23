import matplotlib.pyplot as plt
import numpy as np


class SteelData:
    """
    This function finds number of bars in each region of the wall and their corresponding bar size
    """

    def __init__(self,
                 wall_depth,
                 wall_width,
                 boundary_depth,
                 steel_max,
                 boundary_row=3,
                 boundary_column=10,
                 cover=3.0,
                 boundary_middle_row='two',
                 fn='textfile.txt',
                 path='newpath/'):
        self._L = wall_depth
        self._t_w = wall_width
        self._L_be = boundary_depth
        self._rhoMax = steel_max
        self._boundary_row = boundary_row  # number of rows in the boundary
        self._boundary_column = boundary_column
        self._cover = cover
        self._boundary_middle_row = boundary_middle_row
        # self._boundary_spacing = 3.0  # in
        self._web_max_spacing = wall_width - 2 * cover  # in
        self._fname = fn
        self._path = path

    @property
    def all_operation(self):
        bar_size = {"No.2": (0.250, 0.05),  # 1st is diameter of the bar and then the area
                    "No.3": (0.375, 0.11),
                    "No.4": (0.500, 0.20),
                    "No.5": (0.625, 0.31),
                    "No.6": (0.750, 0.44),
                    "No.7": (0.875, 0.60),
                    "No.8": (1.000, 0.79),
                    "No.9": (1.128, 1.00),
                    "No.10": (1.27, 1.27),
                    "No.11": (1.41, 1.56),
                    "No.14": (1.693, 2.25),
                    "No.18": (2.257, 4.00),
                    "No.18J": (2.337, 4.29),
                    }
        bar_numbers = ["No.2",
                       "No.3",
                       "No.4",
                       "No.5",
                       "No.6",
                       "No.7",
                       "No.8",
                       "No.9",
                       "No.10",
                       "No.11",
                       "No.14",
                       "No.18",
                       "No.18J"
                       ]

        # boundary max steel limit
        A_boundary = self._L_be * self._t_w
        maxAs_be = A_boundary * self._rhoMax

        # web min steel limit (0.25%)
        rhoMin = 0.0025
        # rhoMin = self._rhoMax
        A_web = (self._L - 2 * self._L_be) * self._t_w
        minAs_web = A_web * rhoMin

        if self._boundary_row == 2:
            Ab_be = maxAs_be / (self._boundary_row * self._boundary_column)
        elif self._boundary_row == 3:
            if self._boundary_middle_row == 'two':
                Ab_be = maxAs_be / (self._boundary_column * 2 + 2)  # area of 1 bar needed
            elif self._boundary_middle_row == 'None' or self._boundary_middle_row == 'equal':
                Ab_be = maxAs_be / (self._boundary_column * self._boundary_row)  # area of 1 bar needed
            else:
                print "Something is wrong with the number of rows in the boundary"
        else:
            print "Are you sure there are more than 3 rows in the boundary element?!"

        for i in range(len(bar_numbers)):
            num = bar_numbers[i]
            if bar_size[num][1] < Ab_be:
                bound_bar_no = bar_numbers[i + 1]
        if self._L_be == 0:
            bound_bar_no = 'No.4'

        infile = open(self._fname, 'a')
        infile.write("Provided area of steel in the boundary = %.5f in^2\n"
                     % (self._boundary_column * self._boundary_row * bar_size[bound_bar_no][1]))
        infile.write("              Spacing between the bars = %.4f in.\n\n"
                     % ((self._L_be - 2 * self._cover) / (self._boundary_column - 1)))

        # check clear spacing between bars
        clear_spacing = (self._L_be - 2 * self._cover - self._boundary_column * bar_size[bound_bar_no][0]
                         + bar_size[bound_bar_no][0]) / (self._boundary_column - 1)
        boundary_spacing = (self._L_be - 2 * self._cover) / (self._boundary_column - 1)

        if self._L_be != 0:
            if self._boundary_row >= 3:
                if self._boundary_middle_row == 'two':
                    rho_be = ((self._boundary_column * 2 + 2) * bar_size[bound_bar_no][1]) * 100. / A_boundary
                else:
                    rho_be = ((self._boundary_column * 3) * bar_size[bound_bar_no][1]) * 100. / A_boundary
            else:
                rho_be = ((self._boundary_column * 2) * bar_size[bound_bar_no][1]) * 100. / A_boundary

            if clear_spacing < 1.5 * bar_size[bound_bar_no][1] or clear_spacing < 1.5:
                infile.write("----------------------- ATTENTION ----------------------------------\n")
                infile.write("    Clear spacing between bars in the boundary is not satisfied\n")
                infile.write("--------------------------------------------------------------------\n\n\n")

        # number of steel in the web
        web_bar_no = 'No.4'
        web_row = 2.0
        web_bar_count = minAs_web / bar_size[web_bar_no][1]
        web_column = int(web_bar_count / web_row + 1)
        web_spacing = (self._L - 2.0 * self._L_be) / (web_column + 1.0)
        As_web = web_row * web_column * bar_size[web_bar_no][1]
        rho_web = ((web_column * web_row) * bar_size[web_bar_no][1]) * 100. / A_web

        if self._L_be != 0:
            if self._boundary_row >= 3:
                if self._boundary_middle_row == 'two':
                    num_bars = self._boundary_column * 2 + 2
                else:
                    num_bars = self._boundary_column * 3
            else:
                num_bars = self._boundary_column*2

            infile.write("________________________________________________________________________________\n")
            infile.write("Boundary Element:\n")
            infile.write("                  'No of bars'    'Bar Size'     'Rho_l'     'Row'     'Column'\n")
            infile.write("                  ------------    ----------     -------     -----     --------\n")
            infile.write("                      %d             %s       %0.4f        %d          %d\n" \
                         % (num_bars,
                            bound_bar_no,
                            rho_be,
                            self._boundary_row,
                            self._boundary_column))
        infile.write("---------------------------------------------------------------------------------\n")
        infile.write("Web:\n")
        infile.write("                  'No of bars'    'Bar Size'     'Rho_l'     'Row'     'Column'\n")
        infile.write("                  ------------    ----------     -------     -----     --------\n")
        infile.write("                      %d             %s        %0.4f        %d          %d\n" \
                     % ((web_column * 2),
                        web_bar_no,
                        rho_web,
                        web_row,
                        web_column))
        infile.write("________________________________________________________________________________\n")

        # infile.write("Wall length = %d\n" % self._L)
        # infile.write("Wall thickness = %d\n" % self._t_w)
        infile.write("Wall BE depth = %d in.\n" % self._L_be)
        infile.write("Bar spacing in BE = %f in.\n" % boundary_spacing)
        infile.write("Bar spacing in web = %f in.\n" % web_spacing)
        # infile.write("\n")
        # infile.write("Boundary row = %d\n" % self._boundary_row)
        # infile.write("Boundary column = %d\n" % self._boundary_column)
        if self._L_be != 0:
            if rho_be > 0.03 * 100:
                infile.write("\t ----------------------------\n")
                infile.write("\t Steel in BE exceeds maximum!\n")
                infile.write("\t ----------------------------\n")
            else:
                infile.write("\t Max Steel Satisfied\n")
        else:
            infile.write("\t BE is not required, minimum reinforcement provided\n")

        if rho_web < 0.0025 * 100:
            infile.write("\t ----------------------------\n")
            infile.write("\t Steel in Web is NOT enough!\n")
            infile.write("\t ----------------------------\n")
        else:
            infile.write("\t Min Steel Satisfied\n")

        infile.close()

        # Plotting the longitudinal reinforcement configuration:
        x1, y1 = self._L / 2.0, self._t_w / 2.0
        section_coord = np.array([[x1, y1],
                                  [-x1, y1],
                                  [-x1, -y1],
                                  [x1, -y1],
                                  [x1, y1]])

        x2, y2 = self._L / 2.0 - self._cover, self._t_w / 2 - self._cover
        BE_bar_coord = np.array([x2, y2])
        for i in range(self._boundary_column):
            BE_bar_coord = np.vstack([BE_bar_coord, [x2, y2]])
            BE_bar_coord = np.vstack([BE_bar_coord, [x2, -y2]])
            BE_bar_coord = np.vstack([BE_bar_coord, [-x2, y2]])
            BE_bar_coord = np.vstack([BE_bar_coord, [-x2, -y2]])
            if self._boundary_row >= 3:
                if self._boundary_middle_row == 'two':
                    if i == 0 or i == self._boundary_column - 1:
                        BE_bar_coord = np.vstack([BE_bar_coord, [x2, 0.0]])
                        BE_bar_coord = np.vstack([BE_bar_coord, [-x2, 0.0]])
                else:
                    BE_bar_coord = np.vstack([BE_bar_coord, [x2, 0.0]])
                    BE_bar_coord = np.vstack([BE_bar_coord, [-x2, 0.0]])
            x2 -= boundary_spacing

        x3, y3 = self._L / 2 - self._L_be - web_spacing, self._t_w / 2 - self._cover
        web_bar_coord = np.array([x3, y3])
        for i in range(web_column):
            web_bar_coord = np.vstack([web_bar_coord, [x3, y3]])
            web_bar_coord = np.vstack([web_bar_coord, [x3, -y3]])
            x3 -= web_spacing

        plt.figure('Longitudinal Reinforcement Configuration', figsize=[15, 7.5])
        plt.plot(section_coord[:, 0], section_coord[:, 1], 'grey', lw=3)
        if self._L_be != 0:
            plt.plot(BE_bar_coord[:, 0], BE_bar_coord[:, 1], 'ro', ms=8)
        plt.plot(web_bar_coord[:, 0], web_bar_coord[:, 1], 'bo', ms=5)
        plt.plot([self._L / 2 - self._L_be, self._L / 2 - self._L_be], [self._t_w / 2, -self._t_w / 2], 'grey')
        plt.plot([-self._L / 2 + self._L_be, -self._L / 2 + self._L_be], [self._t_w / 2, -self._t_w / 2], 'grey')

        # plt.text(x1-self._L_be, self._t_w-10, r'BE: '+ str(self._boundary_column*2+2)+str(bound_bar_no), color='red')
        # plt.text(0, self._t_w-10, r'Web: '+ str(web_column*2)+r' No.4', color='blue')

        plt.title('Longitudinal Reinforcement Configuration')
        plt.axis('equal')
        plt.xlim(-x1 - 5, x1 + 5)
        plt.ylim(-y1 - 1, y1 + 1)
        plt.tick_params(
            axis='both',  # changes apply to the x-axis
            which='both',  # both major and minor ticks are affected
            bottom='off',  # ticks along the bottom edge are off
            top='off',  # ticks along the top edge are off
            left='off',
            right='off',
            labelbottom='off',
            labelleft='off')
        plt.fill_between(section_coord[:, 0], section_coord[:, 1], color='lightgray')
        plt.tight_layout()
        plt.savefig(self._path + "Longitudinal Reinforcement Configuration.pdf")
        # plt.show()

        return bound_bar_no, web_row, web_column, web_bar_no
