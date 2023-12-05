# LPM Zen Blue general

# Introduction

This program allows a series of tests over illumination sources for Zeiss widefield and confocal microscopes running Zen Blue. It is possibe to test:

* Short term stability: According to QUAREP-LiMi full test is completed in 5 minutes for each illumination line, testing powers every second.
* Long term stability: The QUAREP-LiMi protocol stablishes 2h tests per line, with measurement intervals of 30s. To allow this for multiple lines this program interleaves the tests for all lines every interval, allowing the full check to be completed in a single run.
* Linearity (response): To analyze the linearity -or response curve- of each light source the powers are measured for a series of set powers.

These tests can be performed for the desired lines and for different test conditions.

# Disclaimer
High illumination powers represent a safety hazard for the equipment and for the operators. We assume that this software will be used by qualified personnel, with a sufficient degree of understanding of the system being used and of the process of light power intensity assessment. It is also assumed that all applicable laser safety regulations are followed.

We have tested this software successfully at different systems and, according to our experience, it is very likely to run correctly in other systems of the same type. However, even nearly identical setups might have unforseen differences, and for this reason the predicted behavior of the macros is not guaranteed.

After installation we strongly advise to test this software under safe conditions -i.e. low laser powers and short test cycles-.

# Installation
This software consists of the following files, placed in three different folders:

   * Macros and driver: 
      Zen Blue recognises python macros installed under "my documents", in "Carl Zeiss\Zen\Macros\". Use the "Public documents" (i.e. "C:\Users\Public\Public Documents\Carl Zeiss\Zen\Macros\") to make the macro available for all windows users):
         
      - QUAREP-LPM-vXY.py is the main program to execute. Currently you can use version 22 or above.
      - The interface file TLPM.py is a slightly modified version of the original file provided by Thorlabs(R).
      The TLPM files are provided by Thorlabs as a part of their TLPM control suite [Thorlabs link](https://www.thorlabs.com/software_pages/ViewSoftwarePage.cfm?Code=OPM).      
      - TLPM.dll is the driver of the Thorlabs power meter device.

   * Configuration folder
      - The configuration file tells the software all the necessary information to run correctly. Save it as C:\QUAREP-Macros\LPM\measurementConfig.csv and make sure that all information in it is consistent with your system.

   * Experiment files
   The optical configurations have to be created at the system by a qualified operator. Here we provide only example files. Once created, they will look like C:\QUAREP-Macros\LPM\Configs\LPM405.czexp, LPM488.czexp ...etc.
         
   - Make your own configurations at the specific microscope (not another of the same type) using Zen Blue, 
   - use only configurations created at the same system
   - Name them uniformly and meaningfully: e.g. LPM488.czexp, 

	   3.0 Detector windows must not overlap with laser lines being measured
	   3.2 Zoom in (e.g. 10x) use bidirectional scanning
	   3.1 According tho the configuration file "LPM" will be the prefix to parse the useful configurations
	   3.2 "488" will be read from the file name and used later to configure the power meter
	   3.3 If "LPM488.czexp" uses the 488nm laser, the measurement will correctly

   Export the configurations into C:\QUAREP-Macros\LPM\Configs\.

   The QUAREP-LPM macro loads specific experiment configurations (*.czexp files) for measuring each illumination source under the desired conditions. The power tests involve the load and execution of these experiments, which causes the detectors to be on during the process. If the spectral windows are not defined to avoid it, in confocal microscopes there is a risk of illuminating -and damaging- the detectors with light reflected on the surface of the power meter device.

It is possible to let the software read the list of available components from the system's database and build these configurations for you. However, in confocal microscopes is advisable to create the configurations manually to explicitly exclude back-reflection issues.

# Tested configurations
This program has been tested under Zen Blue 2.6, 3.1 and 3.8, running for Zeiss LSM800, LSM900 (inverted and upright) confocal and AxioImager (Colibri illumination) widefield systems. Even for other systems of these types the installed filters, detectors and light sources might vary. According to our experience no changes were required to adapt the program between diferent systems of the same type, but issues between software were addressed). Newer versions of Zen seem more consistent and we expect fewer problems with them.

# Contributing
Your contributions, comments and participation are very welcome. We are happy if you can copy and modify these macros for your needs, but if they also benefit the rest of the microscopy community we invite you to join us as a contributor.

# Authors
* Nasser Darwish (Imaging and Optics Facility, Institute of Science and Technology Austria) ndarwish@ist.ac.at
* Arne Fallisch (Life Imaging Center, Albert–Ludwigs–Universität Freiburg) arne.fallisch@bioss.uni-freiburg.de
