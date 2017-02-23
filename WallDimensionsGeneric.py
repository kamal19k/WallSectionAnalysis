import SteelData
import os
import subprocess


class Moment_capacity:
    ''' ********* '''

    def __init__(self,
                 wall_depth,
                 wall_width,
                 boundary_depth,
                 steel_max,
                 boundary_row=3.0,
                 boundary_column=10,
                 cover=3.0,
                 boundary_middle_row='two',
                 fc=5,
                 axial_load=-1441,
                 fn='textfile.txt',
                 path='newpath/'
                 ):
        self.wall_depth = wall_depth
        self.wall_width = wall_width
        self.boundary_depth = boundary_depth
        self.steel_max = steel_max
        self.boundary_row = boundary_row
        self.boundary_column = boundary_column
        self.cover = cover
        self.boundary_middle_row = boundary_middle_row
        self.fc = fc
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

        E = 30000.0  # ksi
        fy = 60.0  # ksi
        steel_calc = SteelData.SteelData(wall_depth, wall_width, boundary_depth, steel_max, boundary_row,
                                         boundary_column,
                                         cover, boundary_middle_row, fn, path)
        res = steel_calc.all_operation
        bound_bar_no, web_row, web_column, web_bar_no = res[0], res[1], res[2], res[3]
        Ab_be = bar_size[bound_bar_no][1]

        ###############################################################################################################

        # Create OpenSEES files:
        filename = "build_RCSection.tcl"
        infile = open(filename, 'w')  # writing the script
        infile.write('# --------------------------------------------------------------------------------------------\n')
        # build a section
        # SET UP ----------------------------------------------------------------------------
        infile.write('# build a section\n')
        infile.write('# SET UP ----------------------------------------------------------------------------\n')
        infile.write('wipe;				# clear memory of all past model definitions\n')
        infile.write('model BasicBuilder -ndm 2 -ndf 3;	# Define the model builder, ndm=#dimension, ndf=#dofs\n')
        infile.write('set dataDir Data;			# set up name of data directory -- simple\n')
        infile.write('file mkdir $dataDir; 			# create data directory\n')
        infile.write('source LibUnits.tcl;			# define units\n')
        infile.write('\n')

        # MATERIAL parameters -------------------------------------------------------------------
        infile.write('# MATERIAL parameters -------------------------------------------------------------------\n')
        infile.write('set IDconcCore 1; 				# material ID tag -- confined core concrete\n')
        infile.write('set IDconcCover 2; 				# material ID tag -- unconfined cover concrete\n')
        infile.write('set IDreinf 3; 				# material ID tag -- reinforcement\n')

        # nominal concrete compressive strength
        infile.write('# nominal concrete compressive strength\n')
        infile.write('set fc 		[expr -%f*$ksi];   # CONCRETE Compressive Strength, ksi (+Tension, -Compression)\n'
                     % fc)
        infile.write('set Ec 		[expr 57*$ksi*sqrt(-$fc/$psi)];	# Concrete Elastic Modulus\n')

        # confined concrete
        infile.write('# confined concrete\n')
        infile.write('set Kfc 		1.3;			# ratio of confined to unconfined concrete strength\n')
        infile.write('set fc1C 		[expr $Kfc*$fc];		# CONFINED concrete (mander model), maximum stress\n')
        infile.write('set eps1C	[expr 2.*$fc1C/$Ec];	# strain at maximum stress \n')
        infile.write('set fc2C 		[expr 0.2*$fc1C];		# ultimate stress\n')
        infile.write('set eps2C 	[expr 5*$eps1C];		# strain at ultimate stress \n')

        # unconfined concrete
        infile.write('# unconfined concrete\n')
        infile.write(
            'set fc1U 		$fc;		# UNCONFINED concrete (todeschini parabolic model), maximum stress\n')
        infile.write('set eps1U	-0.003;			# strain at maximum strength of unconfined concrete\n')
        infile.write('set fc2U 		[expr 0.2*$fc1U];		# ultimate stress\n')
        infile.write('set eps2U	-0.01;			# strain at ultimate stress\n')
        infile.write('set lambda 0.1;				# ratio between unloading slope at $eps2 and initial slope $Ec\n')

        # tensile-strength properties
        infile.write('# tensile-strength properties\n')
        infile.write('set ftC [expr -0.14*$fc1C];		# tensile strength +tension\n')
        infile.write('set ftU [expr -0.14*$fc1U];		# tensile strength +tension\n')
        infile.write('set Ets [expr $ftU/0.002];		# tension softening stiffness\n')

        # -----------
        infile.write('set Fy 		[expr %f*$ksi];		# STEEL yield stress\n' % fy)
        infile.write('set Es		[expr %f*$ksi];		# modulus of steel\n' % E)
        infile.write('set b		0.000000;			# strain-hardening ratio \n')
        infile.write('set R0 18;				# control the transition from elastic to plastic branches\n')
        infile.write('set cR1 0.925;				# control the transition from elastic to plastic branches\n')
        infile.write('set cR2 0.15;				# control the transition from elastic to plastic branches\n')

        # Define materials
        # Concrete
        # infile.write('uniaxialMaterial Concrete02 $IDconcCore $fc1C $eps1C $fc2C $eps2C $lambda $ftC $Ets;'
        #              '	# build core concrete (confined)\n')
        # infile.write('uniaxialMaterial Concrete02 $IDconcCover $fc1U $eps1U $fc2U $eps2U $lambda $ftU $Ets;'
        #              '	# build cover concrete (unconfined)\n')
        # infile.write("# Core concrete (confined)\n")
        infile.write("uniaxialMaterial Concrete01  $IDconcCore  -%f  -0.004   -%f     -0.014\n"  # confined concrete
                     % (fc, 0.1 * fc))
        infile.write("uniaxialMaterial Concrete01  $IDconcCover  -%f   -0.002   0.0     -0.010\n"  # unconfined concrete
                     % fc)
        infile.write('\n')

        # Steel
        infile.write('uniaxialMaterial Steel02 $IDreinf $Fy $Es $b $R0 $cR1 $cR2;'
                     '				# build reinforcement material\n')
        # infile.write("#                        tag  fy E0    b\n")
        # infile.write("uniaxialMaterial Steel01  3  $fy $E 0.01\n\n")

        infile.write('\n')

        # # section GEOMETRY
        # infile.write('# section GEOMETRY -------------------------------------------------------------\n')
        # infile.write('set HSec [expr %f*$in]; 		# Column Depth\n' % wall_depth)
        # infile.write('set BSec [expr %f*$in];		# Column Width\n' % wall_width)
        # infile.write('set coverH [expr %f*$in];		# Column cover to reinforcing steel NA, parallel to H\n' % cover)
        # infile.write('set coverB [expr %f*$in];		# Column cover to reinforcing steel NA, parallel to B\n' % cover)
        # infile.write('set numBarsTop 16;		# number of longitudinal-reinforcement bars in steel layer. -- top\n')
        # infile.write('set numBarsBot 16;		# number of longitudinal-reinforcement bars in steel layer. -- bot\n')
        # infile.write('set numBarsIntTot 6;			# number of longitudinal-reinforcement bars in steel layer.'
        #              ' -- total intermediate skin reinforcement, symm about y-axis\n')
        # infile.write('set barAreaTop [expr 2.25*$in2];	# area of longitudinal-reinforcement bars -- top\n')
        # infile.write('set barAreaBot [expr 2.25*$in2];	# area of longitudinal-reinforcement bars -- bot\n')
        # infile.write('set barAreaInt [expr 2.25*$in2];	# area of longitudinal-reinforcement bars'
        #              ' -- intermediate skin reinf\n')
        infile.write('set SecTag 1;			# set tag for symmetric section\n')
        # infile.write('\n')
        #
        # # FIBER SECTION properties -------------------------------------------------------------
        # infile.write('# FIBER SECTION properties -------------------------------------------------------------\n')
        # infile.write('set coverY [expr $HSec/2.0];	# The distance from the section z-axis to the edge of the cover '
        #              'concrete -- outer edge of cover concrete\n')
        # infile.write('set coverZ [expr $BSec/2.0];	# The distance from the section y-axis to the edge of the cover '
        #              'concrete -- outer edge of cover concrete\n')
        # infile.write('set coreY [expr $coverY-$coverH];	# The distance from the section z-axis to the edge of the core '
        #              'concrete --  edge of the core concrete/inner edge of cover concrete\n')
        # infile.write('set coreZ [expr $coverZ-$coverB];	# The distance from the section y-axis to the edge of the core '
        #              'concrete --  edge of the core concrete/inner edge of cover concreteset nfY 16;'
        #              '			# number of fibers for concrete in y-direction\n')
        # infile.write('set nfY 16;			# number of fibers for concrete in y-direction\n')
        # infile.write('set nfZ 4;				# number of fibers for concrete in z-direction\n')
        # infile.write('set numBarsInt [expr $numBarsIntTot/2];	# number of intermediate bars per side\n')

        # Define Cross Section for nonlinear col
        infile.write("# Define cross-section for nonlinear columns\n")
        infile.write("# ------------------------------------------\n")

        infile.write("# set some paramaters\n")
        infile.write("set colWidth %f;   # Width (thickness) of the wall\n" % wall_width)
        infile.write("set colDepth %f;   # Length of the wall\n\n" % wall_depth)

        infile.write("set webWidth %f;   # Width (thickness) of the web\n" % wall_width)
        infile.write("set webDepth %f;   # Length of the web\n" % (wall_depth - 2 * boundary_depth))

        infile.write("set L_be %f;   # Length of Boundary Element\n" % boundary_depth)

        infile.write("set cover  %f;\n" % cover)
        infile.write("set spacing 3;\n")  # ********************************************************
        infile.write("set As_b    %f;     # area of %s bars\n" % (Ab_be,
                                                                  bound_bar_no))
        infile.write("set As_w    %f;      # area of %s bars\n\n" % (bar_size[web_bar_no][1], web_bar_no))

        infile.write("# some variables derived from the parameters\n")
        infile.write("set y1 [expr $colDepth/2.0]\n")
        infile.write("set z1 [expr $colWidth/2.0]\n\n")

        # Create section fiber
        infile.write("section Fiber 1 {\n")
        if boundary_depth != 0:
            infile.write("\t # Create the concrete core fibers\n")
            infile.write("\t # Right Core:\n")
            infile.write("\t patch rect 1 [expr int($colDepth/2)] 1 [expr $y1-$L_be+$cover] [expr $cover-$z1]"
                         " [expr $y1-$cover] [expr $z1-$cover]\n")
            # infile.write("\t patch rect 1 [expr $L_be/2] 1 [expr $y1-$L_be+$cover] [expr $cover-$z1]"
            #              " [expr $y1-$cover] [expr $z1-$cover]\n")
            infile.write("\t # Left Core:\n")
            infile.write("\t patch rect 1 [expr int($colDepth/2)] 1 [expr $cover-$y1] [expr $cover-$z1]"
                         " [expr $L_be-$y1-$cover] [expr $z1-$cover]\n")
            infile.write("\t # Create the concrete cover fibers (top, bottom, left, right, middle)\n")
            infile.write("\t patch rect 2 [expr int($webDepth/2)] 1  [expr -$y1] [expr $z1-$cover] $y1 $z1\n")
            infile.write("\t patch rect 2 [expr int($webDepth/2)] 1  [expr -$y1] [expr -$z1] $y1 [expr $cover-$z1]\n")
            infile.write("\t patch rect 2 2 1  [expr -$y1] [expr $cover-$z1] [expr $cover-$y1] [expr $z1-$cover]\n")
            infile.write("\t patch rect 2 2 1  [expr $y1-$cover] [expr $cover-$z1] $y1 [expr $z1-$cover]\n")
        infile.write("\t patch rect 2 [expr int($webDepth/2)] 1  [expr $L_be-$y1-$cover] [expr $cover-$z1]"
                     " [expr $y1-$L_be+$cover] [expr $z1-$cover]\n")
        infile.write("\t # Create the reinforcing fibers\n")
        # boundary_vspacing = (wall_width - 2*cover) / (boundary_row - 1)

        # Right BE bars
        if boundary_depth != 0:
            infile.write("\t layer straight 3 %d $As_b [expr $y1-$cover]    [expr $z1-$cover]   [expr $y1-$L_be]"
                         "  [expr $z1-$cover]\n" % boundary_column)  # top row
            infile.write("\t layer straight 3 %d $As_b [expr $y1-$cover]    [expr $cover-$z1]   [expr $y1-$L_be]"
                         "  [expr $cover-$z1]\n" % boundary_column)  # bottom row
            if boundary_row >= 3.0:  # middle row
                infile.write("\t layer straight 3 %d $As_b [expr $y1-$cover]    0.0"
                             "   [expr $y1-$L_be+$cover]  0.0\n"
                             % (2 if boundary_middle_row == 'two' else boundary_column))
        # web bars
        infile.write("\t layer straight 3 %d $As_w [expr $y1-$L_be]    [expr $z1-$cover]   [expr $L_be-$y1]"
                     "  [expr $z1-$cover]\n" % web_column)  # top row
        infile.write("\t layer straight 3 %d $As_w [expr $y1-$L_be]    [expr $cover-$z1]   [expr $L_be-$y1]"
                     "  [expr $cover-$z1]\n" % web_column)  # bottom row

        # Left BE bars
        if boundary_depth != 0:
            infile.write("\t layer straight 3 %d $As_b [expr $cover-$y1]    [expr $cover-$z1]   [expr $L_be-$y1-$cover]"
                         "  [expr $cover-$z1]\n" % boundary_column)  # bottom row
            infile.write("\t layer straight 3 %d $As_b [expr $cover-$y1]    [expr $z1-$cover]   [expr $L_be-$y1-$cover]"
                         "  [expr $z1-$cover]\n" % boundary_column)  # top row
            if boundary_row >= 3.0:
                infile.write("\t layer straight 3 %d $As_b [expr $cover-$y1]    0.0"
                             "   [expr $L_be-$y1-$cover]  0.0\n"
                             % (2 if boundary_middle_row == 'two' else boundary_column))
        infile.write("};	# end of fiber section definition\n\n")

        infile.close()  # close build_RCSection.tcl file
        ###############################################################################################################

        # Create MomentCurvature2D.tcl file
        filename = "MomentCurvature2D.tcl"
        infile = open(filename, 'w')  # writing the script

        infile.write('proc MomentCurvature2D { secTag axialLoad maxK {numIncr 100} } {\n')
        infile.write('\t##################################################\n')
        infile.write('\t# A procedure for performing section analysis (only does\n')
        infile.write('\t# moment-curvature, but can be easily modified to do any mode\n')
        infile.write('\t# of section reponse.)\n')
        infile.write('\n')

        # Define two nodes at (0,0)
        infile.write('\t# Define two nodes at (0,0)\n')
        infile.write('\tnode 1001 0.0 0.0\n')
        infile.write('\tnode 1002 0.0 0.0\n')
        infile.write('\n')

        infile.write('\t# Fix all degrees of freedom except axial and bending\n')
        infile.write('\tfix 1001 1 1 1\n')
        infile.write('\tfix 1002 0 1 0\n')
        infile.write('\n')

        # Define element
        infile.write('\t# Define element\n')
        infile.write('\t#                         tag ndI ndJ  secTag\n')
        infile.write('\telement zeroLengthSection  2001   1001   1002  $secTag\n')
        infile.write('\n')

        # Create recorder
        infile.write('\t# Create recorder\n')
        infile.write('\trecorder Node -file data/Mphi.out -time -node 1002 -dof 3 disp;'
                     '      # output moment (col 1) & curvature (col 2)\n')
        infile.write('\trecorder Element -file data/StressStrain%s.out -time -ele 2001 section fiber'
                     ' %.1f 0 stressStrain\n' % ('_ExtComp', wall_depth / 2.0))
        infile.write('\trecorder Element -file data/StressStrain%s.out -time -ele 2001 section fiber'
                     ' %.1f 0 stressStrain\n' % ('_ExtTens', -wall_depth / 2.0))
        infile.write('\trecorder Element -file data/StressStrain%s.out -time -ele 2001 section fiber'
                     ' 0 0 3 stressStrain\n' % '_Center')
        for k in range(1, 6 + 1):
            if k < 4:
                infile.write('\trecorder Element -file data/StressStrain%s.out -time -ele 2001 section fiber'
                             ' %.1f 0 stressStrain\n' % ('_pos' + str(k), k * wall_depth / 8.0))
            else:
                infile.write('\trecorder Element -file data/StressStrain%s.out -time -ele 2001 section fiber'
                             ' %.1f 0 stressStrain\n' % ('_neg' + str(k), k * -wall_depth / 8.0))
        infile.write('\n')

        infile.write('\trecorder Element -file data/StressStrainTensionSteel.out -time -ele 2001 section fiber'
                     ' %.1f %.1f 3 stressStrain\n' % (-wall_depth - cover, wall_width - cover))
        infile.write('\n')

        # Define constant axial load
        infile.write('\t# Define constant axial load\n')
        infile.write('\tpattern Plain 3001 "Constant" {\n')
        infile.write('\tload 1002 $axialLoad 0.0 0.0\n')
        infile.write('\t}\n')
        infile.write('\n')

        # Define analysis parameters
        infile.write('\tintegrator LoadControl 0 1 0 0\n')
        infile.write('\tsystem SparseGeneral -piv;	# Overkill, but may need the pivoting!\n')
        infile.write('\ttest EnergyIncr  1.0e-9 10\n')
        infile.write('\tnumberer Plain\n')
        infile.write('\tconstraints Plain\n')
        infile.write('\talgorithm Newton\n')
        infile.write('\tanalysis Static\n')
        infile.write('\n')

        # Do one analysis for constant axial load
        infile.write('\t# Do one analysis for constant axial load\n')
        infile.write('\tanalyze 1\n\n')

        infile.write('\tloadConst -time 0.0\n\n')

        # Define reference moment
        infile.write('\t# Define reference moment\n')
        infile.write('\tpattern Plain 3002 "Linear" {\n')
        infile.write('\t	load 1002 0.0 0.0 1.0\n')
        infile.write('\t}\n')
        infile.write('\n')

        # Compute curvature increment
        infile.write('\t# Compute curvature increment\n')
        infile.write('\tset dK [expr $maxK/$numIncr]\n')
        infile.write('\n')

        # Use displacement control at node 1002 for section analysis, dof 3
        infile.write('\t# Use displacement control at node 1002 for section analysis, dof 3\n')
        infile.write('\tintegrator DisplacementControl 1002 3 $dK 1 $dK $dK\n')
        infile.write('\n')

        # Do the section analysis
        infile.write('\t# Do the section analysis\n')
        infile.write('\tset ok [analyze $numIncr]\n')
        infile.write('\n')

        # if convergence failure
        infile.write('\t# ----------------------------------if convergence failure-------------------------\n')
        infile.write('\tset IDctrlNode 1002\n')
        infile.write('\tset IDctrlDOF 3\n')
        infile.write('\tset Dmax $maxK\n')
        infile.write('\tset Dincr $dK\n')
        infile.write('\tset TolStatic 1.e-9;\n')
        infile.write('\tset testTypeStatic EnergyIncr \n')
        infile.write('\tset maxNumIterStatic 6\n')
        infile.write('\tset algorithmTypeStatic Newton\n')
        infile.write('\tif {$ok != 0} {  \n')
        infile.write('\t\t# if analysis fails, we try some other stuff, performance is slower inside this loop\n')
        infile.write('\t\tset Dstep 0.0;\n')
        infile.write('\t\tset ok 0\n')
        infile.write('\t\twhile {$Dstep <= 1.0 && $ok == 0} {\n')
        infile.write('\t\t\tset controlDisp [nodeDisp $IDctrlNode $IDctrlDOF ]\n')
        infile.write('\t\t\tset Dstep [expr $controlDisp/$Dmax]\n')
        infile.write('\t\t\tset ok [analyze 1];                		'
                     '# this will return zero if no convergence problems were encountered\n')
        infile.write('\t\t\tif {$ok != 0} {;				# reduce step size if still fails to converge\n')
        infile.write('\t\t\t\tset Nk 4;			# reduce step size\n')
        infile.write('\t\t\t\tset DincrReduced [expr $Dincr/$Nk];\n')
        infile.write('\t\t\t\tintegrator DisplacementControl  $IDctrlNode $IDctrlDOF $DincrReduced\n')
        infile.write('\t\t\t\tfor {set ik 1} {$ik <=$Nk} {incr ik 1} {\n')
        infile.write('\t\t\t\t\tset ok [analyze 1];                		'
                     '# this will return zero if no convergence problems were encountered\n')
        infile.write('\t\t\t\t\tif {$ok != 0} {  \n')
        infile.write('\t\t\t\t\t\t# if analysis fails, we try some other stuff\n')
        infile.write('\t\t\t\t\t\t# performance is slower inside this loop	global maxNumIterStatic;	    '
                     '# max no. of iterations performed before "failure to converge" is retd\n')
        infile.write('\t\t\t\t\t\tputs "Trying Newton with Initial Tangent .."\n')
        infile.write('\t\t\t\t\t\ttest NormDispIncr   $TolStatic      2000 0\n')
        infile.write('\t\t\t\t\t\talgorithm Newton -initial\n')
        infile.write('\t\t\t\t\t\tset ok [analyze 1]\n')
        infile.write('\t\t\t\t\t\ttest $testTypeStatic $TolStatic      $maxNumIterStatic    0\n')
        infile.write('\t\t\t\t\t\talgorithm $algorithmTypeStatic\n')
        infile.write('\t\t\t\t\t}\n')
        infile.write('\t\t\t\t\tif {$ok != 0} {\n')
        infile.write('\t\t\t\t\t\tputs "Trying Broyden .."\n')
        infile.write('\t\t\t\t\t\talgorithm Broyden 8\n')
        infile.write('\t\t\t\t\t\tset ok [analyze 1 ]\n')
        infile.write('\t\t\t\t\t\talgorithm $algorithmTypeStatic\n')
        infile.write('\t\t\t\t\t}\n')
        infile.write('\t\t\t\t\tif {$ok != 0} {\n')
        infile.write('\t\t\t\t\t\tputs "Trying NewtonWithLineSearch .."\n')
        infile.write('\t\t\t\t\t\talgorithm NewtonLineSearch 0.8 \n')
        infile.write('\t\t\t\t\t\tset ok [analyze 1]\n')
        infile.write('\t\t\t\t\t\talgorithm $algorithmTypeStatic\n')
        infile.write('\t\t\t\t\t}\n')
        infile.write('\t\t\t\t\tif {$ok != 0} {;				# stop if still fails to converge\n')
        infile.write('\t\t\t\t\t\tputs [format $fmt1 "PROBLEM" $IDctrlNode $IDctrlDOF [nodeDisp $IDctrlNode'
                     ' $IDctrlDOF] $LunitTXT]\n')
        infile.write('\t\t\t\t\t\treturn -1\n')
        infile.write('\t\t\t\t\t}; # end if\n')
        infile.write('\t\t\t\t}; # end for\n')
        infile.write('\t\t\t\tintegrator DisplacementControl  $IDctrlNode $IDctrlDOF $Dincr;'
                     '	# bring back to original increment\n')
        infile.write('\t\t\t}; # end if\n')
        infile.write('\t\t};	# end while loop\n')
        infile.write('\t};      # end if ok !0\n')
        infile.write('\t# ------------------------------------------------------------------------------------------\n')
        infile.write('\tglobal LunitTXT;					# load time-unit text\n')
        infile.write('\tif {  [info exists LunitTXT] != 1} {set LunitTXT "Length"};'
                     '		# set blank if it has not been defined previously.\n')
        infile.write('\n')

        infile.write('\tset fmt1 "%s Pushover analysis: CtrlNode %.3i, dof %.1i, Curv=%.4f /%s";'
                     '	# format for screen/file output of DONE/PROBLEM analysis\n')
        infile.write('\tif {$ok != 0 } {\n')
        infile.write('\t\tputs [format $fmt1 "PROBLEM" $IDctrlNode $IDctrlDOF [nodeDisp $IDctrlNode'
                     ' $IDctrlDOF] $LunitTXT]\n')
        infile.write('\t} else {\n')
        infile.write('\t\tputs [format $fmt1 "DONE"  $IDctrlNode $IDctrlDOF [nodeDisp $IDctrlNode'
                     ' $IDctrlDOF] $LunitTXT]\n')
        infile.write('\t}\n')
        infile.write('\n')

        infile.write('}\n')
        infile.close()
        #############################################################################################################

        # Create analyzeMomentCurvature2D.tcl file
        filename = "analyzeMomentCurvature2D.tcl"
        infile = open(filename, 'w')  # writing the script
        infile.write('# -------------------------------------------------------------------------------------------\n')
        infile.write('# Moment-Curvature analysis of section\n\n')
        # define procedure
        infile.write('# define procedure\n')
        infile.write('source MomentCurvature2D.tcl\n\n')

        # set AXIAL LOAD
        infile.write('set P %f;	# + Tension, - Compression\n' % axial_load)

        # set maximum Curvature:
        infile.write('# set maximum Curvature:\n')
        infile.write('set Ku [expr 0.00105/$in];\n')
        infile.write('set numIncr 100;	# Number of analysis increments to maximum curvature (default=100)\n')
        infile.write('# Call the section analysis procedure\n')
        infile.write('MomentCurvature2D $SecTag $P $Ku $numIncr\n')
        infile.close()
        #############################################################################################################

        # Create runFile2D.tcl file
        filename = "runFile2D.tcl"
        infile = open(filename, 'w')  # writing the script
        infile.write('puts "------------------ 2D Model -------------------"\n')
        infile.write('source build_RCSection.tcl\n')
        infile.write('source analyzeMomentCurvature2D.tcl\n')
        infile.close()
        #############################################################################################################

        # Run OpenSEES file
        cmd = ['OpenSees', filename]   # runFile2D.tcl is the main file
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        process.wait()
