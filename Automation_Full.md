# Automated Laser Intensity Measurement
## Motivation
Light microscopy setups frequently rely on multiple excitation light sources. To ensure quality and measurement reproducibility, their short- (5 min) and long-term (120 min) illumination powers and stabilities need to be assessed through regular measurements with an external, calibrated power sensor. 
The assessment protocols can be very time and resource consuming. For instance, the long-term assessment, conducted on a system containing 3 lasers would require at least 6 h to complete. As most systems contain more than 3 excitation light sources, some degree of time-saving automation of the above task is imperative.
This protocol describes the automation of short- and long-term illumination power and stability measurement. The goal is to establish an unsupervised measurement scenario, where multiple lasers can be characterized within the span of a typical 4 h system reservation slot.
## The Measurement Protocols
The implemented [measurement protocols](https://github.com/QUAREP-LiMi/WG1-Automation/tree/main/Microscope_Systems) adhere to the guidelines established by the [QUAREP-LiMi Working Group 1](https://quarep.org/working-groups/wg-1-illumination-power/). The tools and materials provided here may change in accordance to future developments of the QUAREP-LiMi Working Group 1.
### Fully automated, short-term stability measurements
>1. The microscope control software activates the respective laser, sets its intensity level to 5 %, activates the Python script controlling the external power meter, to which it sends the wavelength and intensity (AOTF) information.
>2.	The Python script sets the power meter to the laser wavelength and instructs it to stream power measurements every 1 s for 600 s into a CSV file (laser wavelength, respective intensity and a timestamp of each measurement).
>3.	The microscope control software repeats steps 1 - 2 at the 20 % and 80 % laser intensity setting. 
>4.	The microscope control software repeats steps 1 - 3 for each laser.
### Fully automated, long-term stability measurements
Multiple, laser-based excitation wavelengths are interleaved within a repeating 30 sec measurement pattern:
>1.	The microscope control software activates the respective laser, sets its intensity to 5 %, activates the Python script controlling the external power meter to which it sends the wavelength and intensity (AOTF) information. 
>2.	The Python script sets the power meter to the laser wavelength and instructs it to stream a power measurement integrated for 1 s.
>3.	Steps 1 - 2 are repeated for the 20 % and 80 % laser intensity setting.
>4.	Steps 1 - 3 are repeated for x number of wavelengths (lasers) that fit within 30 s time window.
>5.	Steps 1 - 4 are repeated every 30 s for a total of 120 min.
>6.	Each measurement is appended to a CSV file, which contains the respective laser wavelength, intensity and a time stamp of each measurement.
## Requirements
- 	An automated (at least the illumination) microscope driven by a software that:
    - can switch between illumination modalities;
    - allows the automation of the acquisition process (e.g. looping though illumination sources);
    - provides a way to configure and control an external power meter device.
- A calibrated power meter device that accepts commands from the microscope control computer. This device needs:
  - either programming libraries that allow the remote control by a custom software or an interface that can be called using commands (e.g. serial port commands);
  - a spectral setting which, once configured, provides the calibrated radiometric readouts for the configuration selected;
  - to be capable of automatically storing the measured values in a file (e.g. *CSV*).
## Implementation Scheme
The microscope automation environment controls and configures the light sources and the power meter device by means of a programming interface that assigns the appropriate parameters and synchronizes them. Configuration files provide the system-specific information needed and in the end the results are stored in a CSV file. The scheme below shows the role played by each component in this implementation.
<figure>
    <img src="/Images/Automation_Full.png" alt="High-level implementation scheme" width=100%>
</figure>
<p align="center">
    Figure: <em>A high-level view of automated intensity measurement of a light source using a calibrated external power sensor.</em>
</p>
    

### External Power Meter Control
Ideally, the automation environment of the microscope control software establishes the communication with the external power meter.
- Case 1: Direct access to the power meter API by means of the same computer language implemented within both, the microscope control software and the power meter. This is the case, for example, for Visitron microscopes and Thorlabs power meters, where the former implement a python interpreter and the latter provide control functions in python.
- Case 2: An intermediate script is implemented to facilitate communication between microscope control software and power meter employing different computer languages. This approach is applicable in more cases and it will be covered below.
### Separate Configuration Files
Even while considering the same vendor the microscope hardware can vary significantly, from the type of the system to the installed light sources or the chosen filters and their placement. A single program would require serious modifications from one microscope to another unless we can move these settings to independent files. Part of our aim is to provide some already-made examples that can serve as a starting point for the development of automation solutions, case by case.
## Specific Implementations
### Microscope Control Software
As we are considering an already-configured microscope we will not describe how to set up the microscope control software. Nevertheless, with respect to functionality we can list the following examples:
- Nikon: the NIS Elements macro environment has been available for many years and validated for the purposes of this protocol.
- Zeiss: microscopes running under ZEN Blue software have a macro environment based on Iron Python. A ZEN Blue development module can be acquired separately, but it is not required for running pre-existing scripts. The ZEN Black microscope control software provides a visual basic interface. The large number of microscopes running ZEN Black makes them an important target for automated measurement protocol development, even though this microscope control software is being discontinued.
- Visitron and LaVision BioTec provide python interpreters.
- Leica Microsystems and Olympus have not made official announcements regarding equivalent solutions, although they might appear in the near future. Currently these two cases are covered by our alternative post-processing scheme.
### Programing Environment
The intermediate script is written in Python. We have successfully tested the miniconda environment as a lightweight package providing the necessary interpreter and libraries. It is also possible to compile these scripts.
### Power Meters and Software
We have tested several power meters from Thorlabs, all running under the Optical Power Monitor software [Thorlabs link](https://www.thorlabs.com/software_pages/ViewSoftwarePage.cfm?Code=OPM). The only additional requirement is to use the *TLPM.dll* driver provided in the same package. There is a driver switcher utility to assign the appropriate driver to the device.
## Configuration
1.	Install the Python environment (e.g. miniconda).
2.	The measurePower.pyw and TLPM.py scripts must be saved together with the TLPM.dll driver file. Choose an appropriate folder.
3.	Save the paths in a configuration file (see the examples provided). In this manner, the code will not depend on the installation paths.
4.	There are at least two different scenarios:
a.	When the settings are assigned by loading the configurations (e.g. Zen Blue), these configurations have to be created and exported as files. The paths will be provided in the configuration file.
b.	If the hardware components are operated one by one (e.g. NIS-Elements) the operator has to explore the optical configurations to assign the component indices manually (e.g. for the 488 nm measurement which are the indices for the appropriate laser and filter cube). Currently this is written on the first lines of code but will be moved to configuration files.
## Disclaimer
Running lasers with high power settings represents a hazard for the operator and can be dangerous for the detector hardware (detectors or cameras) unless the light path is set in a safe manner. The implementation of any laser power measurement configuration, as the automation setup must be carried out by a properly trained operator and must be tested in a safe manner (e.g. low powers first) before being put into production.
This protocol and all files associated with it are provided as a guide but they do not intend to be a final implementation for any system other than the ones tested by ourselves. Even among microscopes of the same type and from the same vendor minor differences might exist that can potentially require further adaptations. 
We take no responsibility for any damages caused to the equipment or the people involved in the application of these tools. 
## License
The licensing terms of this document are the same that apply to the QUAREP documents from which it depends, while the licensing for each of the scripts provided are given by their corresponding authors.
