# --------------------------------------------------------------------------------------------
# build a section
# SET UP ----------------------------------------------------------------------------
wipe;				# clear memory of all past model definitions
model BasicBuilder -ndm 2 -ndf 3;	# Define the model builder, ndm=#dimension, ndf=#dofs
set dataDir Data;			# set up name of data directory -- simple
file mkdir $dataDir; 			# create data directory
source LibUnits.tcl;			# define units

# MATERIAL parameters -------------------------------------------------------------------
set IDconcCore 1; 				# material ID tag -- confined core concrete
set IDconcCover 2; 				# material ID tag -- unconfined cover concrete
set IDreinf 3; 				# material ID tag -- reinforcement
# nominal concrete compressive strength
set fc 		[expr -5.000000*$ksi];   # CONCRETE Compressive Strength, ksi (+Tension, -Compression)
set Ec 		[expr 57*$ksi*sqrt(-$fc/$psi)];	# Concrete Elastic Modulus
# confined concrete
set Kfc 		1.3;			# ratio of confined to unconfined concrete strength
set fc1C 		[expr $Kfc*$fc];		# CONFINED concrete (mander model), maximum stress
set eps1C	[expr 2.*$fc1C/$Ec];	# strain at maximum stress 
set fc2C 		[expr 0.2*$fc1C];		# ultimate stress
set eps2C 	[expr 5*$eps1C];		# strain at ultimate stress 
# unconfined concrete
set fc1U 		$fc;		# UNCONFINED concrete (todeschini parabolic model), maximum stress
set eps1U	-0.003;			# strain at maximum strength of unconfined concrete
set fc2U 		[expr 0.2*$fc1U];		# ultimate stress
set eps2U	-0.01;			# strain at ultimate stress
set lambda 0.1;				# ratio between unloading slope at $eps2 and initial slope $Ec
# tensile-strength properties
set ftC [expr -0.14*$fc1C];		# tensile strength +tension
set ftU [expr -0.14*$fc1U];		# tensile strength +tension
set Ets [expr $ftU/0.002];		# tension softening stiffness
set Fy 		[expr 60.000000*$ksi];		# STEEL yield stress
set Es		[expr 30000.000000*$ksi];		# modulus of steel
set b		0.000000;			# strain-hardening ratio 
set R0 18;				# control the transition from elastic to plastic branches
set cR1 0.925;				# control the transition from elastic to plastic branches
set cR2 0.15;				# control the transition from elastic to plastic branches
uniaxialMaterial Concrete01  $IDconcCore  -5.000000  -0.004   -0.500000     -0.014
uniaxialMaterial Concrete01  $IDconcCover  -5.000000   -0.002   0.0     -0.010

uniaxialMaterial Steel02 $IDreinf $Fy $Es $b $R0 $cR1 $cR2;				# build reinforcement material

set SecTag 1;			# set tag for symmetric section
# Define cross-section for nonlinear columns
# ------------------------------------------
# set some paramaters
set colWidth 24.000000;   # Width (thickness) of the wall
set colDepth 360.000000;   # Length of the wall

set webWidth 24.000000;   # Width (thickness) of the web
set webDepth 252.000000;   # Length of the web
set L_be 54.000000;   # Length of Boundary Element
set cover  3.000000;
set spacing 3;
set As_b    0.310000;     # area of No.5 bars
set As_w    0.200000;      # area of No.4 bars

# some variables derived from the parameters
set y1 [expr $colDepth/2.0]
set z1 [expr $colWidth/2.0]

section Fiber 1 {
	 # Create the concrete core fibers
	 # Right Core:
	 patch rect 1 [expr int($colDepth/2)] 1 [expr $y1-$L_be+$cover] [expr $cover-$z1] [expr $y1-$cover] [expr $z1-$cover]
	 # Left Core:
	 patch rect 1 [expr int($colDepth/2)] 1 [expr $cover-$y1] [expr $cover-$z1] [expr $L_be-$y1-$cover] [expr $z1-$cover]
	 # Create the concrete cover fibers (top, bottom, left, right, middle)
	 patch rect 2 [expr int($webDepth/2)] 1  [expr -$y1] [expr $z1-$cover] $y1 $z1
	 patch rect 2 [expr int($webDepth/2)] 1  [expr -$y1] [expr -$z1] $y1 [expr $cover-$z1]
	 patch rect 2 2 1  [expr -$y1] [expr $cover-$z1] [expr $cover-$y1] [expr $z1-$cover]
	 patch rect 2 2 1  [expr $y1-$cover] [expr $cover-$z1] $y1 [expr $z1-$cover]
	 patch rect 2 [expr int($webDepth/2)] 1  [expr $L_be-$y1-$cover] [expr $cover-$z1] [expr $y1-$L_be+$cover] [expr $z1-$cover]
	 # Create the reinforcing fibers
	 layer straight 3 20 $As_b [expr $y1-$cover]    [expr $z1-$cover]   [expr $y1-$L_be]  [expr $z1-$cover]
	 layer straight 3 20 $As_b [expr $y1-$cover]    [expr $cover-$z1]   [expr $y1-$L_be]  [expr $cover-$z1]
	 layer straight 3 2 $As_b [expr $y1-$cover]    0.0   [expr $y1-$L_be+$cover]  0.0
	 layer straight 3 38 $As_w [expr $y1-$L_be]    [expr $z1-$cover]   [expr $L_be-$y1]  [expr $z1-$cover]
	 layer straight 3 38 $As_w [expr $y1-$L_be]    [expr $cover-$z1]   [expr $L_be-$y1]  [expr $cover-$z1]
	 layer straight 3 20 $As_b [expr $cover-$y1]    [expr $cover-$z1]   [expr $L_be-$y1-$cover]  [expr $cover-$z1]
	 layer straight 3 20 $As_b [expr $cover-$y1]    [expr $z1-$cover]   [expr $L_be-$y1-$cover]  [expr $z1-$cover]
	 layer straight 3 2 $As_b [expr $cover-$y1]    0.0   [expr $L_be-$y1-$cover]  0.0
};	# end of fiber section definition

