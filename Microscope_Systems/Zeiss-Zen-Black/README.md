# Laser Power Measurement Zen Black
# Introduction
This program allows a series of tests over illumination sources for Zeiss widefield and confocal microscopes running Zen Blue. It is possibe to test:

Short term stability: According to QUAREP-LiMi full test is completed in 5 minutes for each illumination line, testing powers every second.
Long term stability: The QUAREP-LiMi protocol stablishes 2h tests per line, with measurement intervals of 30s. 
Linearity (response): To analyze the linearity -or response curve- of each light source the powers are measured for a series of set powers.
These tests can be performed for the desired lines and for different test conditions.

# Disclaimer
High illumination powers represent a safety hazard for the equipment and for the operators. We assume that this software will be used by qualified personnel, with a sufficient degree of understanding of the system being used and of the process of light power intensity assessment. It is also assumed that all applicable laser safety regulations are followed.

This program was tested successfully in a specific microscope. We provide it in the hope that it is helpful, but we cannot provide support or warranty of any kind. Differences between similar microscopes (filters, light paths, etc.) are to be expected and the usually minor adaptations needed from one to another require the understanding of the code. Despite unlikely, damage to the equipment caused by wrong edits or by unforeseen circumstances is still possible. While unlikely, damage to the equipment caused by wrong edits or by unforeseen circumstances is still possible. Proceed at your own risk, following the local safety regulations and  by by ensuring complete understanding of the programs prior to their execution. In particular, for testing purposes we strongly advise to employ low laser power settings and reduced number of loops.

# Tested configurations
This program has been tested under Zen Black v. 2.3, running for Zeiss LSM800 (inverted and upright) confocal. According to our experience no changes were required to adapt the program between diferent systems of the same type.

# Installation
This program allows automatic power measurements for Zeiss microscopes running Zen Black

This software follows this hierarchy: Zen macro -> measurePowers.pyw -> TLPM.py -> TLPM_64.dll

Download all files and configurations and put them into a folder of your choice, e.g.

	C:\Users\desiredUser\QUAREP
 
The "Zen macro" runs under Zen Black. If you have Microsoft Office installed on your computer, copy the VBA file called "Power-Measurement.lvb" from the "Zen macro" folder into:

	C:\Users\desiredUser\Documents\Carl Zeiss\ZEN\Documents\Macros

to make the macro available. If you do not have Microsoft Office installed on your computer, copy the VBA file called "Power-Measurement-without-Office.lvb" in the same directory. If desiredUser is "all users" the macro will be available for all windows users

The Zen macro connects to a python interpreter (miniconda suggested) and invokes the 
measurePowers.pyw script. You can download miniconda under:

https://docs.conda.io/en/latest/miniconda.html

# Thorlabs power meter
The TLPM files from Thorlabs bring the low level access to the 
power meter device. You can download the Thorlabs software under

https://www.thorlabs.com/software_pages/ViewSoftwarePage.cfm?Code=OPM
 
# Ophir power meter
To able to use the Ophir power meter you need to download the latest version of StarLabs

https://www.ophiropt.com/laser--measurement/software/starlab-for-usb

# Configuration
The Zen software needs to load different files to function. In this way the macro can be adapted to different microscopes, as long as the configuration files are created at the same system. 

The following files are needed for the Macro:

	a. The VBA Macro named “Power-Measurement.lvb” in the main folder (or “Power-Measurement-without-Office.lvb”)
 	b. The python measurement script named “measurePowers.pyw” in folder “PythonScripts”
	c. The configuration file “measurementConfig.csv” in the main folder
 	d. The python Thorlabs library name “TLPMX.py” (only for Thorlab power meters)
 	e. The Thorlabs dll named “TLPMX_64.dll” or “TLPMX_32.dll” (only for Thorlab power meters)
  	f. "pywin32" package for python (miniconda, only for Ophir power meters)

The files d, e and f are not part of the Macro download. The Thorlabs python library (d) can be found under: 
	
	C:\Program Files (x86)\IVI Foundation\VISA\WinNT\TLPMX\Examples\Python

The Thorlabs dll (e) can be found under:
	
	C:\Program Files\IVI Foundation\VISA\Win64\Bin

The folders may vary depending on your operation system. Copy both files into the “PythonScripts” folder. 

The "pywin32" package f is only needed for the Ophir power meter. To install the "pywin32" package open a anaconda command prompt and type

	conda install pywin32

In the following table you can find the standard source folder and the suggested destination folder:

<table>
  <thead>
    <tr>
      <th align="left">
        File
      </th>
      <th align="left">
        Soucre
      </th>
      <th align="left">
        Destination
      </th>
    </tr>
  </thead>
    <tbody>
    <tr>
      <td>
        a.
      </td>
      <td>
	https://github.com/QUAREP-LiMi/WG1-Automation/blob/main/Microscope_Systems/Zeiss-Zen-Black/Zen%20macro/Power-Measurement.lvb
        https://github.com/QUAREP-LiMi/WG1-Automation/blob/main/Microscope_Systems/Zeiss-Zen-Black/Zen%20macro/Power-Measurement-without-Office.lvb
      </td>
      <td>
        C:\Users\desired-username\Documents\Carl Zeiss\ZEN\Documents\Macros
	C:\Users\desired-username\Documents\Carl Zeiss\ZEN\Documents\Macros
      </td>
    </tr>
    <tr>
      <td>
        b.
      </td>
      <td>
        https://github.com/QUAREP-LiMi/WG1-Automation/blob/main/Microscope_Systems/Zeiss-Zen-Black/pythonScripts/measurePowers.pyw
      </td>
      <td>
        C:\Users\your-username\QUAREP\Zen macro\scrips\measurePowers.pyw
      </td>
    </tr>
    <tr>
      <td>
        c.
      </td>
      <td>
        https://github.com/QUAREP-LiMi/WG1-Automation/blob/main/Microscope_Systems/Zeiss-Zen-Black/measurementConfig.csv
      </td>
      <td>
        C:\Users\your-username\QUAREP\Zen macro\measurementConfig.csv
      </td>
    </tr>
    <tr>
      <td>
        d
      </td>
      <td>
        C:\Program Files (x86)\IVI Foundation\VISA\WinNT\TLPMX\Examples\Python\TLPMX.py
      </td>
      <td>
         C:\Users\your-username\QUAREP\Zen macro\scrips\TLPMX.py
      </td>
    </tr>
    <tr>
      <td>
        e
      </td>
      <td>
        C:\Program Files\IVI Foundation\VISA\Win64\Bin\TLPMX_64.dll
      </td>
      <td>
         C:\Users\your-username\QUAREP\Zen macro\scrips\TLPMX_64.dll
      </td>
    </tr>   
    </tbody>
</table>

# Alter TLMPX.py file
Open the file

	“TLPMX.py” 

in a text editor. Go to line 287 for a 32 bit system or 289 for a 64 bit system and change the filename in brackets (example for line 241) from

	("TLPMX_64.dll")
to
	
	("C:\\the\\path\\to\\your\\folder\\TLPMX_64.dll")

Note that folder have to be separated by a double backslash “\\”. Save and close the file.

# Alter measurementConfig.csv file

You do not need to alter the file in a text editor as you can also alter it during execution of the macro later on. However it is possible to alter the file. Therefore open the file 
	 
	 “measurementConfig.csv”

in a text editor. Change the “scriptPath” in line 3 to the path where you stored the “measurePowers.pyw” script. Change the “dataSavePath” to the path where you want to store your measurement data. Change the “expName” to the corresponding name of the experiment in ZEN Black. Change the “expLocation” to the name of your facility.

# Create an experiment in Zeiss Zen Black
Create an experiment in the ZEN Black software according to the QUAREP Power Measurement Protocol:

https://www.protocols.io/view/illumination-power-stability-and-linearity-measure-5jyl853ndl2w/v2

No laser source must be chosen. Note that depending on the software version a continuous measurement mode is not possible if point scan is selected. Therefore a “Time Series” with maximum number of cycles has to be selected. (It has not been tested yet if this is long enough for a “Long Measurement” of 2 hours). Save the experiment under the same name as the “expName” in the “measurementConfig.csv” file.

# Load the macro
To load the macro go to the top menu and select “Macro…” from the drop down menu of the “Macro” (shortcut ALT+F8)). Click on load and search for the folder in which you stored the macro and choose the file “Power-Measurement.lvb” (or “Power-Measurement-without-Office.lvb”). You can assign it to the drop down menu by clicking on the tab “Assign Macro” and then choose the file again and insert a name.

# Execute macro for the first time
If you start the macro for the first time it will first search for the configuration file ”measurementConfig.csv” under:

	C:\Users\your-username\QUAREP\

If the file cannot be found in this folder a user dialog allows you to choose a folder containing the configuration file ”measurementConfig.csv”. This works only with the "Power-Measurement.lvb" macro. If you use the “Power-Measurement-without-Office.lvb” macro you have to change the location of the configuration file in line 50 in "Module1" in the VBA editor from
	
	fileName = "C:\Users\" & Environ$("UserName") & "\QUAREP\measurementConfig.csv"
to
	
	fileName = "your-measurementConfig.csv-file-location"

After the file is read it takes some time until the user form pops up as the macro loops through all beam splitters to get the relevant information. After that the user form appears. You can save your configuration at any time by clicking on the “Save Config” button which allows you to choose a folder where the configuration file “measurementConfig.csv“ will be saved (only for "Power-Measurement.lvb" macro). Be aware that your previous configuration will be overwritten if it is in the same folder. 
Saving the configuration will also speed up the start of the script next time, as the loop through all beam splitters is spared and instead read from the configuration file. Keep in mind that you delete the beam splitters from your configuration file when you have replace beam splitters in between measurements.

You can see additional settings by clicking on the button “More settings”. This opens another user form beneath the main from where you can set up your experiment name, python path, script path etc. If you click the save button all settings will be saved in this session. To save them permanently in a configuration file you have to click on “Save Config” in the main user form.

Before you start you have to choose your wavelength, beam splitter, power and type of measurement. All beam splitters of your instrument will appear in a dropdown menu. You can choose your beam splitters depending on your wavelength. The chosen power will be measured for every wavelength in case of a short or long measurement. For linearity measurements you can choose how many measurements point you want to have per decade. Here are some examples for this settings:

<table>
  <thead>
    <tr>
      <th>
        Steps
      </th>
      <th>
        Decade
      </th> 
      <th align="left">
        Laser power
      </th>
    </tr>
  </thead>
    <tbody>
    <tr>
      <td>
        10
      </td>
      <td>
        1
      </td>
      <td>
        10, 20, 30, 40, 50, 60, 70, 80, 90 and 100 %
      </td>
    </tr>
    <tr>
      <td>
        10
      </td>
      <td>
        2
      </td>
      <td>
        1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 90 and 100 %
      </td>
    </tr>
    <tr>
      <td>
        5
      </td>
      <td>
        1
      </td>
      <td>
        20, 40, 60, 80 and 100 %    
      </td>
    </tr>
    <tr>
      <td>
        5
      </td>
      <td>
        2
      </td>
      <td>
         2, 4, 6, 8, 10, 20, 40, 60, 80 and 100 %
      </td>
    </tr>
    </tbody>
</table>

If you have a temperature sensor is connected to you Thorlabs power meter you can check this option. Do not check this option if no temperature sensor is connected to you Thorlabs device as this will lead to an error.

# Contribution
Your contributions, comments and participation are very welcome. We are happy if you can copy and modify these macros for your needs, but if they also benefit the rest of the microscopy community we invite you to join us as a contributor.

# Authors
Macros (”Power-Measurement.lvb",”Power-Measurement-without-office.lvb"):
Arne Fallisch (Life Imaging Center, Albert–Ludwigs–Universität Freiburg) arne.fallisch@bioss.uni-freiburg.de

Python script (measurePowers.pyw)
Arne Fallisch (Life Imaging Center, Albert–Ludwigs–Universität Freiburg) arne.fallisch@bioss.uni-freiburg.de
Kees van der Oord (Nikon) 
Nasser Darwish (Imaging and Optics Facility, Institute of Science and Technology Austria)
