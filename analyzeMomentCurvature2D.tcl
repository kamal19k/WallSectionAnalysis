# -------------------------------------------------------------------------------------------
# Moment-Curvature analysis of section

# define procedure
source MomentCurvature2D.tcl

set P -1800.000000;	# + Tension, - Compression
# set maximum Curvature:
set Ku [expr 0.00105/$in];
set numIncr 100;	# Number of analysis increments to maximum curvature (default=100)
# Call the section analysis procedure
MomentCurvature2D $SecTag $P $Ku $numIncr
