# Introduction
This program was tested successfully in a specific microscope. We provide it in the hope that it 
is helpful, but we cannot provide support or warranty of any kind. Differences between similar 
microscopes (filters, light paths, etc.) are to be expected and the usually minor adaptations 
needed from one to another require the understanding of the code. Despite unlikely, damage to 
the equipment caused by wrong edits or by unforeseen circumstances is still possible. While 
unlikely, damage to the equipment caused by wrong edits or by unforeseen circumstances is still 
possible. Proceed at your own risk, following the local safety regulations and  by by ensuring 
complete understanding of the programs prior to their execution. In particular, for testing 
purposes we strongly advise to employ low laser power settings and reduced number of loops.

# Installation
This program allows automatic power measurements for Zeiss microscopes running Zen Black

This software follows this hierarchy: Zen macro -> measurePowers.pyw -> TLPM.py -> TLPM_64.dll

The "Zen macro" runs under Zen Black. If you have Microsoft Office installed on your computer, copy the VBA file called "Power-Measurement.lvb" into:

	C:\Users\desiredUser\Documents\Carl Zeiss\ZEN\Documents\Macros

to make the macro available. If you do not have Microsoft Office installed on your computer, copy the VBA file called "Power-Measurement-without-Office.lvb" in the same directory. If desiredUser is "all users" the macro will be available for all windows users

The Zen macro connects to a python interpreter (miniconda suggested) and invokes the 
measurePowers.pyw script. You can download miniconda under:

https://docs.conda.io/en/latest/miniconda.html

# Thorlabs power meter
The TLPM files from Thorlabs bring the low level access to the 
power meter device. You can download the Thorlabs software under

https://www.thorlabs.com/software_pages/ViewSoftwarePage.cfm?Code=OPM
 
The Zen software needs to load configuration files to setup the light sources. In this
way the macro can be adapted to different microscopes, as long as the configuration files
are created at the same system. These files should be stored in the "Configs" folder.

The measurementConfig.csv file contains the instructions needed to relove all the 
dependencies. This can be customized if the files are saved in different locations.

# Ophir power meter
To able to use the Ophir power meter you need to download the latest version of StarLabs

https://www.ophiropt.com/laser--measurement/software/starlab-for-usb

# Configuration
The following files are needed for the Macro:

	a. The VBA Macro named “Power-Measurement.lvb” in the main folder (or “Power-Measurement-without-Office.lvb”)
 	b. The python measurement script named “measurePowers.pyw” in folder “PythonScripts”
	c. The configuration file “measurementConfig.csv” in the main folder
 	d. The python Thorlabs library name “TLPM.py” (only for Thorlab power meters)
 	e. The Thorlabs dll named “TLPM_64.dll” or “TLPM_32.dll” (only for Thorlab power meters)
  	f. pywin32 package for python (miniconda, only for Ophir power meters)

The files d and e are not part of the Macro download. The Thorlabs python library can be found under: 
	
	C:\Program Files (x86)\IVI Foundation\VISA\WinNT\TLPM\Examples\Python

The Thorlabs dll can be found under:
	
	C:\Program Files\IVI Foundation\VISA\Win64\Bin

The folders may vary depending on your operation system. Copy both files int the “PythonScripts” folder.

# Alter TLMP.py and measurementConfig.csv
Open the file

	“TLPM.py” 

in a text editor. Go to line 239 for a 32 bit system or 241 for a 64 bit system and change the filename in brackets (example for line 241) from

	("TLPM_64.dll")
to
	
	("C:\\the\\path\\to\\your\\folder\\TLPM_64.dll")

Note that folder have to be separated by a double backslash “\\”. Save and close the file.
Open the file 
	 
	 “measurementConfig.csv”

in a text editor. Change the “scriptPath” in line 3 to the path where you stored the “measurePowers.pyw” script. Change the “dataSavePath” to the path where you want to store your measurement data. Change the “expName” to the corresponding name of the experiment in ZEN Black. Change the “expLocation” to the name of your facility.

# Install the pywin32 package using miniconda
Open a anaconda command prompt and type

	conda install pywin32

# Create an experiment in Zeiss Zen Black
Create an experiment in the ZEN Black software according to the QUAREP Power Measurement Protocol:

https://www.protocols.io/view/illumination-power-stability-and-linearity-measure-5jyl853ndl2w/v2

No laser source must be chosen. Note that depending on the software version a continuous measurement mode is not possible if point scan is selected. Therefore a “Time Series” with maximum number of cycles has to be selected. (It has not been tested yet if this is long enough for a “Long Measurement” of 2 hours). Save the experiment under the same name as the “expName” in the “measurementConfig.csv” file.

# Load the macro
To load the macro go to the top menu and select “Macro…” from the drop down menu of the “Macro” (shortcut ALT+F8)). Click on load and search for the folder in which you stored the macro and choose the file “Power-Measurement.lvb”. You can assign it to the drop down menu by clicking on the tab “Assign Macro” and then choose the file again and insert a name.

# Execute macro for the first time
If you start the macro for the first time it will first search for the configuration file ”measurementConfig.csv” under:

	C:\users\username\Thorlabs\QUAREP\

If the file cannot be found in this folder a user dialog allows you to choose a folder containing the configuration file ”measurementConfig.csv”. If you want to permanently change the location folder of the configuration file you have to change it in line 51 in module  in the VBA editor from
	
	fileName = "A:\Data\" & Environ$("UserName") & "\Thorlabs\QUAREP\measurementConfig.csv"
to
	
	fileName = "A:\Data\" & Environ$("UserName") & "\Thorlabs\QUAREP\measurementConfig.csv"

After the file is read it takes some time until the user form pops up as the macro loops through all beam splitters to get the relevant information. After that the user form appears. You can save your configuration at any time by clicking on the “Save Config” button which allows you to choose a folder where the configuration file “measurementConfig.csv“ will be saved. Be aware that your previous configuration will be overwritten if it is in the same folder.

Before you start you have to choose your wavelength, beam splitter, power and type of measurement. All beam splitters of your instrument will appear in a dropdown menu. You can choose your beam splitters depending on your wavelength. The chosen power will be measured for every wavelength in case of a short or long measurement.

You can see additional settings by clicking on the button “More settings”. This opens another user form beneath the main from where you can set up your experiment name, python path, script path etc as is shown in Figure 4. If you click the save button all settings will be saved in this session. To save them permanently in a configuration file you have to click on “Save Config” in the main user form.

# License
The automation script is covered by the 3-Clause BSD license. You can freely use, modify, 
and share it. Only mentioning the origianl authors in a modified version requires prior 
consent.

The additional software necessary is provided and licensed by the corresponding vendors.
To make use of it please review and agree their terms.

# Disclaimer
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND 
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. 
IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, 
INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT 
NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR 
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY 
OF SUCH DAMAGE.

 
