#
# Copyright 2023 Nasser Darwish, Arne Fallisch

#@author: Nasser Darwish, Institute of Science and Technology Austria
#@author: Arne Fallisch, University of Freiburg

# This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS 
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL 
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS 
# IN THE SOFTWARE.

import subprocess, os, csv, time
from TLPM import TLPM
from timeit import default_timer as timer
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from shutil import copyfile

from ctypes import cdll, c_long, c_ulong, c_uint32, byref, create_string_buffer, c_bool, c_char_p, c_int, c_int16, \
    c_double, sizeof, c_voidp

import time
import sys
import codecs

def connectPowerMeter():

    tlPM = TLPM();
    deviceCount = c_uint32();
    tlPM.findRsrc(byref(deviceCount));
    print("devices found: " + str(deviceCount.value));
    if deviceCount.value<1:
        print("thorlabs power meter not found");
        exit(-1);

    resourceName = create_string_buffer(1024);
    tlPM.getRsrcName(c_int(0), resourceName);
    tlPM.open(resourceName, c_bool(True), c_bool(True));
    print('\nPower meter connected\n');
    return tlPM;

def configOverview(pathString):

    tree = safeLoadXML(pathString)
    root = tree.getroot()

    for child in root:
        print(child.tag, child.attrib)
    
def getActiveConfig(MTBpath):
    possibleFolders = os.listdir(MTBpath);
    activeConfigFile = 'Active Configuration.xml';
    
    for currDir in possibleFolders:
        currFullPath = MTBpath + currDir + '\\'+ activeConfigFile
        
        if (os.path.exists(currFullPath)):
            xmlfile = currFullPath

    print('Using '+ xmlfile +' as active configuration.\n');
    return(xmlfile)
    
def setBeamSplitters(pathString,visBS,invBS):
    
    global visBSAvailable, invBSAvailable
    tree = safeLoadXML(pathString)
    root = tree.getroot()
    
    if(visBSAvailable):
        # Set BeamSplitterVis
        beamSplitter = tree.find(".//ParameterCollection[@Id='MTBLSM880MbsVis']");
        beamSplitter[0].text = expBeamSplitterVis[visBS];
        beamSplitter[1].text = expBeamSplitterVisPosition[visBS];
    if(invBSAvailable):                
        # Set BeamSplitterInVis
        beamSplitterInVis = tree.find(".//ParameterCollection[@Id='MTBLSM880MbsInvis']");
        beamSplitterInVis[0].text = expBeamSplitterInVis[invBS];
        beamSplitterInVis[1].text = expBeamSplitterInVisPosition[invBS];
    safeWriteXML(pathString, root, tree)

def getLaserStatus(Id, pathString, detectionMode):
    tree = safeLoadXML(pathString)

    # Check detection mode and find corresponding LED or Laser line in the .exp file
    if detectionMode == 'WF':
        xmlLED = tree.find('.//HardwareSetting[@Name="Before [ANS] Smart"]');
        if xmlLED is None:
            xmlLED = tree.find('.//HardwareSetting[@Name="Before [CNF] Smart"]');
        xmlLightSource = xmlLED.find(".//ParameterCollection[@Id='" + Id + "']");    
    else:
        xmlLightSource = tree.find(".//ParameterCollection[@Id='" + Id + "']");    
        
    # Get the actual status from LED or Laser
    if(xmlLightSource[0].text == 'false'):
        print(Id + ' is currently disabled')
    if(xmlLightSource[0].text == 'true'):
        print(Id + ' is currently enabled')
    return xmlLightSource[0].text

def setLaserStatus(Id, Wavelength, pathString, enableStatus, detectionMode):

    tree = safeLoadXML(pathString);
    root = tree.getroot();

    # Check detection mode and find corresponding LED or Laser line in the .exp file
    if detectionMode == 'WF':
        xmlLED = tree.find('.//HardwareSetting[@Name="Before [ANS] Smart"]');
        if xmlLED is None:
            xmlLED = tree.find('.//HardwareSetting[@Name="Before [CNF] Smart"]');
        xmlLightSource = xmlLED.find(".//ParameterCollection[@Id='" + Id + "']"); 
        xmlFilter = xmlLED.find(".//ParameterCollection[@Id='MTBFLLEDFilterChanger']");
        if Wavelength == '555':
            xmlFilter[0].text = '1';
            xmlFilter[1].text = 'Albireo_Filter.555_30';
        if Wavelength == '590':
            xmlFilter[0].text = '2';
            xmlFilter[1].text = 'Albireo_Filter.590_27';
    else:
        xmlLightSource = tree.find(".//ParameterCollection[@Id='" + Id + "']");
    
    # Set the actual status from LED or Laser
    if enableStatus == True:
        xmlLightSource[0].text = 'true'
        print('Enabling '+Id)
    if enableStatus == False:
        xmlLightSource[0].text = 'false'
        print('Disabling '+Id)

    safeWriteXML(pathString, root, tree)

# Lasers .................................................................................

def disableAllLasers(pathString):

    print('Disabling all lasers or LEDs')
    tree = safeLoadXML(pathString)
    root = tree.getroot()
    for enabled in root.iter('IsEnabled'):
        enabled.text = 'false'
    
    safeWriteXML(pathString, root, tree)

def setAllIntensitiesToZero(pathString):
    
    print('Setting all intensities (powers) to zero');    
    tree = safeLoadXML(pathString);
    root = tree.getroot();
    for intensity in root.iter('Intensity'):
        intensity.text = '0'

    safeWriteXML(pathString, root, tree)

def getLaserPower(Id, pathString, detectionMode):
        
    tree = safeLoadXML(pathString)
    
    if detectionMode == 'WF':
        xmlLED = tree.find('.//HardwareSetting[@Name="Before [ANS] Smart"]');
        if xmlLED is None:
            xmlLED = tree.find('.//HardwareSetting[@Name="Before [CNF] Smart"]');
        xmlLightSource = xmlLED.find(".//ParameterCollection[@Id='" + Id + "']");
    else:
        xmlLightSource = tree.find(".//ParameterCollection[@Id='" + Id + "']");
    print('Current power of ' +Id+': ' + xmlLightSource[1].text)
    return parameter[1].text
    # If we get here noting was found
    print('Laser Id not found')
    return 0

def setLaserPower(Id, pathString, setPower, detectionMode):
        
    tree = safeLoadXML(pathString)
    root = tree.getroot()
    
    if detectionMode == 'WF':
        xmlLED = tree.find('.//HardwareSetting[@Name="Before [ANS] Smart"]');
        if xmlLED is None:
            xmlLED = tree.find('.//HardwareSetting[@Name="Before [CNF] Smart"]');
        xmlLightSource = xmlLED.find(".//ParameterCollection[@Id='" + Id + "']");    
    else:
        xmlLightSource = tree.find(".//ParameterCollection[@Id='" + Id + "']");    
    xmlLightSource[1].text = str(setPower);
    print('Setting power ' + xmlLightSource[1].text +' for ' + Id)
    
    safeWriteXML(pathString, root, tree)

# Experiment wavelengths .........................................................

def assignColibri(xmlTree, counter):
    xmlLightSource = xmlTree.find('.//HardwareSetting[@Name="Before [ANS] Smart"]');
    if xmlLightSource is None:
        xmlLightSource = xmlTree.find('.//HardwareSetting[@Name="Before [CNF] Smart"]');
    if xmlLightSource is not None:
        xmlColibri = xmlLightSource.find(".//ParameterCollection[@Id='MTBLED1']");
        if xmlColibri[0].text == "true":
            print(xmlColibri[0].text);
            expWavelength.append(int(385))
            expChosenWavelength.append(counter);
            expWavelengthId.append('MTBLED1');
            counter += 1                    
            print('Wavelength 385 nm found for MTBLED1');
        xmlColibri = xmlLightSource.find(".//ParameterCollection[@Id='MTBLED2']");
        if xmlColibri[0].text == "true":
            print(xmlColibri[0].text);
            expWavelength.append(int(430))
            expChosenWavelength.append(counter);
            expWavelengthId.append('MTBLED2');
            counter += 1
            print('Wavelength 430 nm found for MTBLED2');
        xmlColibri = xmlLightSource.find(".//ParameterCollection[@Id='MTBLED3']");
        if xmlColibri[0].text == "true":
            print(xmlColibri[0].text);
            expWavelength.append(int(475))
            expChosenWavelength.append(counter);
            expWavelengthId.append('MTBLED3');
            counter += 1
            print('Wavelength 475 nm found for MTBLED3');
        xmlColibri = xmlLightSource.find(".//ParameterCollection[@Id='MTBLED5']");
        if xmlColibri[0].text == "true":
            if xmlColibri[1].text == 'Albireo_Filter.555_30':
                print(xmlColibri[0].text);
                expWavelength.append(int(555))
                expChosenWavelength.append(counter);
                expWavelengthId.append('MTBLED5');
                counter += 1
                print('Wavelength 555 nm found for MTBLED5');
            elif xmlColibri[1].text == 'Albireo_Filter.590_27':
                print(xmlColibri[0].text);
                expWavelength.append(int(590))
                expChosenWavelength.append(counter);
                expWavelengthId.append('MTBLED5');
                counter += 1
                print('Wavelength 590 nm found for MTBLED5');
        xmlColibri = xmlLightSource.find(".//ParameterCollection[@Id='MTBLED6']");
        if xmlColibri[0].text == "true":
            print(xmlColibri[0].text);
            expWavelength.append(int(630))
            expChosenWavelength.append(counter);
            expWavelengthId.append('MTBLED6');
            counter += 1
            print('Wavelength 630 nm found for MTBLED6');
        xmlColibri = xmlLightSource.find(".//ParameterCollection[@Id='MTBLED4']");
        if xmlColibri[0].text == "true":
            print(xmlColibri[0].text);
            expWavelength.append(int(735))
            expChosenWavelength.append(counter);
            expWavelengthId.append('MTBLED7');
            counter += 1
            print('Wavelength 735 nm found for MTBLED7');
    else:
        print('Cannot find any light source!');
    return counter

def assignLSM(xmlTree, counter):
    xmlTracklaser = xmlTree.find('.//TrackLaserSettings');
    for xmlParameter in xmlTracklaser:
        if xmlParameter[0].text == "true":
            confXMLComponent = activeTree.find(".//Component[@MTBId='" + xmlParameter.attrib['Id'].replace('Line','')+ "']");
            confXMLBeam = confXMLComponent.find(".//Beam");
            print(confXMLBeam[0].text);
            expWavelengthId.append(xmlParameter.attrib['Id'])
            expWavelength.append(confXMLBeam[0].text);
            expChosenWavelength.append(counter);
            counter += 1
    return counter
    
# Files ..............................................................................................................

def safeLoadXML(xmlFile):    
    # Loading XML trees for Zen blue.
    if Zen.Application.Environment.Version.StartsWith('2'):
        # At least under Zen blue 2.6 The "parse" method fails, 
        # loading bad characters ("?) at the beggining of the XML content
        ff = open(xmlFile, mode='r')
        textXML = ff.read().decode("UTF-8")
        ff.close()
        tree = ET.ElementTree(ET.fromstring(textXML[1:]))
    else:
        # In Zen 3.1, 3.5 and 3.8 the parse method works well.
       tree = ET.parse(xmlFile);
       root = tree.getroot();
    return tree

def safeWriteXML(xmlFile, root, tree):
    # Loading XML trees (in principle experiment files, *.czexp) for Zen blue.
    if Zen.Application.Environment.Version.StartsWith('2'):
        # Workarounds for XML issues below Zen 3
        xmlstr = ET.tostring(root, encoding='utf-8').decode('utf-8')    #This seems to be the safe wat to save
        xmlstr = '<?xml version="1.0" encoding="utf-8"?>'+'\n'+xmlstr
        
        outputFile = codecs.open(xmlFile,"w", "utf-8-sig") # The files have to be in "utf-8 BOM" encoding
        outputFile.write(xmlstr)
        outputFile.close()
    else:
        # Zen 3 and above write XML trees without issues
        tree.write(xmlFile, encoding='utf-8', xml_declaration=True)

# Systeminfo ................................................................................................

def getAllLineIDs(xmlFile):
    # Provides illumination line IDs for lines under
    # the //TrackLaserSettings section in the xml file
    IDString =[];
    tree = safeLoadXML(xmlFile)

    tracklaser = tree.find('.//TrackLaserSettings')
    for parameter in tracklaser:        
        IDString.append(str(parameter.attrib['Id']))
    return IDString

def getWavelength(xmlFile, lineName, expWavelength):
    # For a given line Id, return the corresponding wavelength
    lineNames = getAllLineIDs(xmlFile);
    position = lineNames.index(lineName);
    return expWavelength[position]

def getLaserIdFromAPI():
    # Zen can list all components via its API. THis function returns 
    # all the entries starting with "MTBLSMLaserLine" (e.g. MTBLSMLaserLine2)
    # Tested for LSM800 and LSM900 systems
    laserNames = [];
    componentList = Zen.Devices.ReadHardwareSetting().GetAllComponentIds();
    for component in componentList:
        if(component.Contains('LaserLine')):
            laserNames.append(component);
            print('Got ' + component + ' laser Id from API');
    return laserNames


def getLEDIdFromAPI():
    
    # This function is not tested or used yet. It's intended to be 
    # similar to getLaserNamesFromAPI(), for LED (e.g. Colibri) lines
    
    LEDLines = [];
    componentList = Zen.Devices.ReadHardwareSetting().GetAllComponentIds();
    for component in componentList:
        if(component.Contains('MTBLED')):
            LEDLines.append(component);
            print('Got ' + component + ' LED Id from API');
    return LEDLines    


def getLedNamesFromTable():
    
    # This function is not used yet.
    
    if expDetectionMode[0] == 'WF':
        expWavelengthId = ('MTBLED1','MTBLED2','MTBLED3','MTBLED4','MTBLED5','MTBLED6');
    else:
        expWavelengthId = [];

def getLedWavelengths():

    # fills the "expWavelength" list using known values known from Coliblri lamps:
    # IDs, entry names in the xml files and corresponding wavelengths

    global activeTree
    global expWavelength
    global expWavelengthId
    global expDetectionMode
    
    expWavelengthIdTmp = [];
    
    for Id in expWavelengthId:
        
        # Get wavelength from laser from active configuration file
        confXMLComponent = activeTree.find(".//Component[@MTBId='" + Id + "']");
        confXMLWavelength = confXMLComponent.find(".//Wavelength");
        if confXMLWavelength.text == '425':
            print('Found wavelength 430 nm for component ' + Id);
            expWavelength.append('430');
        elif confXMLWavelength.text == '472':
            print('Found wavelength 475 for component ' + Id);
            expWavelength.append('475');
        elif confXMLWavelength.text == '507':
            print('Found wavelength 511 for component ' + Id);
            expWavelength.append('511');
        elif confXMLWavelength.text == '567':
            print('Found wavelength 555 nm for component ' + Id);
            expWavelength.append('555');
            print('Found wavelength 590 nm for component ' + Id);
            expWavelength.append('590');
            
            # Set LED two time as it has two wavelength: 555 and 590 nm
            expWavelengthIdTmp.append(Id);
        elif confXMLWavelength.text == '635':
            print('Found wavelength 630 nm for component ' + Id);
            expWavelength.append('630');
        else:
            print('Found wavelength ' + confXMLWavelength.text + ' nm for component ' + Id);
            expWavelength.append(confXMLWavelength.text);
        expWavelengthIdTmp.append(Id);
    
    # Reset array 
    expWavelengthId = expWavelengthIdTmp;
    return expWavelength

def getLaserWavelengths(xmlTree):

    # Return wavelengths for the corresponding line IDs, using
    # the information available in the Active Configuration file.
    global activeTree
    global expWavelength
    global expWavelengthId

    # Code does not work for me as get laser names from API does not work
    # Find the correspoinding wavelengths in the active tree
    for Id in expWavelengthId:
        confXMLComponent = activeTree.find(".//Component[@MTBId='" + Id.replace('Line','')+ "']");
        if not (confXMLComponent is None):
            confXMLBeam = confXMLComponent.find(".//Beam");
            print('Found wavelength ' + confXMLBeam[0].text + ' nm for component ' + Id);
            expWavelength.append(confXMLBeam[0].text);
    return expWavelength

def getDetectionMode(xmlTree):
    # Function to get detection mode colibri or laser
    xmlDetectionMode = xmlTree.find('.//DetectionModeSetup');
    if xmlDetectionMode[0].tag == 'Zeiss.Micro.Acquisition.WfTrackDetectionMode' or xmlDetectionMode[0].tag == 'Zeiss.Micro.Acquisition.WfTrackDetectionMode ':
        return 'WF';
    elif xmlDetectionMode[0].tag == 'Zeiss.Micro.LSM.Acquisition.Lsm880ChannelTrackDetectionMode':
        return 'LSM';
    elif xmlDetectionMode[0].tag == 'Zeiss.Micro.LSM.Acquisition.LsmChannelTrackDetectionMode':
        return 'LSM';

# Beam splitters ......................................................................................................................


def getBeamSplittersVis():
    # Function to get all beam splitters vis    
    
    # Define global variables
    global expBeamSplitterVis;
    global expBeamSplitterVisName;
    global expBeamSplitterVisPosition;
    
    # Get BeamSplittersVis from active configuration file
    confXMLMainBeamSplitterVis = activeTree.find(".//Component[@DisplayName='Main Beam Splitter VIS']");
    confXMLBeamSplitterVis = confXMLMainBeamSplitterVis.findall(".//Element[@Class]");
    for confXMLChild in confXMLBeamSplitterVis:
        expBeamSplitterVis.append(confXMLChild.attrib['Name']);
        expBeamSplitterVisName.append(confXMLChild.attrib['DisplayName']);
        expBeamSplitterVisPosition.append(confXMLChild.attrib['Position']);
        print(confXMLChild.attrib['Class'],confXMLChild.attrib['Position'],confXMLChild.attrib['DisplayName'],confXMLChild.attrib['Name']);


def getBeamSplittersInVis():
    # Function to get all beam splitters invis
    
    # Define global variables
    global expBeamSplitterInVis;
    global expBeamSplitterInVisName;
    global expBeamSplitterInVisPosition;
    
    # Get BeamSplittersInVis from active configuration file
    confXMLMainBeamSplitterInVis = activeTree.find(".//Component[@DisplayName='Main Beam Splitter INVIS']");
    confXMLBeamSplitterInVis = confXMLMainBeamSplitterInVis.findall(".//Element[@Class]");
    for confXMLChild in confXMLBeamSplitterInVis:
        expBeamSplitterInVis.append(confXMLChild.attrib['Name']);
        expBeamSplitterInVisName.append(confXMLChild.attrib['DisplayName']);
        expBeamSplitterInVisPosition.append(confXMLChild.attrib['Position']);
        print(confXMLChild.attrib['Class'],confXMLChild.attrib['Position'],confXMLChild.attrib['DisplayName'],confXMLChild.attrib['Name']);

def measure(wavelength, powerLevel, fileName, duration, avgTime, tlPM):
    # This function performs the power measurement, calling the tlPM device
    # The wavelength, average time and duration configure the process
    # The set powerlevel is written in the file together with the results
    
    thermometer = False;
    
    tlPM.setWavelength(c_double(float(wavelength)));
    time.sleep(0.1); #Without this delay the first number is consistently higher than the rest

    #check if temperature sensor is connected
    temperature = c_double();
    try:
        tlPM.measExtNtcTemperature(byref(temperature));
        thermometer = True;
    except NameError as err:
        print("Temperature sensor not connected! ");
        print(err.args);
    
    #check if file is empty, if not print headline
    origStdOut = sys.stdout
    with open(fileName,"a") as fout:
        if fout and os.stat(fileName).st_size == 0:
            sys.stdout = fout;
            if not thermometer:
                print("timestamp\twavelength\tsetting\tpower");
                print("YYYY-MM-DD HH:MM:SS\tnm\ts\tW");
            elif temperature.value != 0:
                print("timestamp\twavelength\tsetting\tpower\ttemperature");
                print("YYYY-MM-DD HH:MM:SS\tnm\ts\tW\tC");
            sys.stdout = origStdOut;
    
    start = datetime.now();

    measure_until = start + timedelta(seconds=float(duration))
    average_until = start
    while datetime.now() <= measure_until:
        average_until += timedelta(seconds=float(avgTime));
        average_count = 0;
        total_power = 0;
        total_temperature = 0;
        
        start_average = datetime.now()  
        while(datetime.now() < average_until):
            power = c_double();
            tlPM.measPower(byref(power));
            total_power += power.value;
    
            if thermometer:
                tlPM.measExtNtcTemperature(byref(temperature));
                total_temperature += temperature.value;
            average_count += 1;
            
        total_power /= average_count;
        if thermometer:
           total_temperature /= average_count;
        ts = (start_average-start).total_seconds();

        origStdOut = sys.stdout;
        with open(fileName,"a") as fout:

            if thermometer:
                outString = start_average.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + '\t' + str(wavelength) + '\t' + str(powerLevel) + '\t' + str(total_power) + '\t' + str(total_temperature);
            else:
                outString = start_average.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + '\t' + str(wavelength) + '\t' + str(powerLevel) + '\t' + str(total_power);
            sys.stdout = fout
            print(outString);
            sys.stdout = origStdOut
            print(outString);

def main():

    # Define global variables
    global expChosenWavelength;
    global activeTree, activeRoot;
    global expWavelength;
    global expWavelengthId;
    global expChosenWavelength;
    global expPower;
    global expChosenPower;
    global expDetectionMode;
    global expBeamSplitterVis;
    global expBeamSplitterVisName;
    global expBeamSplitterVisPosition;
    global expChosenBeamSplitterVis;
    global expBeamSplitterInVis;
    global expBeamSplitterInVisName;
    global expBeamSplitterInVisPosition;
    global expChosenBeamSplitterInVis;
    global expPath;
    global expPrefix;
    global expExt;
    global expShortDuration;
    global expShortInterval;
    global expLongDuration;
    global expLongInterval;
    global expLinearStep;
    global expLinearDuration;
    global dataSavePath;
    global dataSavePrefix;
    global dataSaveExt;
    global expChosenExperiment;
    
    now = datetime.now()
    dateTimeStr = now.strftime("%d%m%Y-%H%M")
    
    measConfig = 'measurementConfig.csv'
    measconfigPathUser = os.path.expanduser('~')+"\\Documents\\Carl Zeiss\\ZEN\\Documents\\Macros\\"
    measconfigPathGlobal = "C:\\Users\\Public\\Documents\\Carl Zeiss\\ZEN\\Documents\\Macros\\"
    
    if (os.path.exists(measconfigPathUser+measConfig)):
        measconfigPath = measconfigPathUser
    elif (os.path.exists(measconfigPathGlobal+measConfig)):
        measconfigPath = measconfigPathGlobal
    else:
        print("Error: No config file")
        return
    
    
    print(measconfigPath)
    
    measConfigFile = measconfigPath+'measurementConfig.csv'
    MTBpath = 'C:\\ProgramData\\Carl Zeiss\\MTB2011\\'
    
    visBSAvailable = False;
    invBSAvailable = False;

    with open(measConfigFile) as configFile:
        csvReader = csv.reader(configFile, delimiter =",")
        #processedLines = 0
        for row in csvReader:
            varName = row[0]
            if(varName == "dataSavePath"):
                dataSavePath = row[1]
            elif(varName == "dataSavePrefix"):
                dataSavePrefix = row[1]
            elif(varName == "dataSaveExt"):
                dataSaveExt = row[1]
            elif(varName == "expPath"):
                expPath = row[1]
            elif(varName == "expPrefix"):
                expPrefix = row[1]
            elif(varName == "expExt"):
                expExt = row[1]
            elif(varName == "expName"):
                expName = row[1]
            elif(varName == "expDetectionMode"):
                expDetectionMode = [];
                for lineInd in range(1,len(row)): 
                    expDetectionMode.append(row[lineInd]);                
            elif(varName == "expWavelength"):
                expWavelength = [];
                for lineInd in range(1,len(row)): 
                    expWavelength.append(row[lineInd]);
            elif(varName == "expWavelengthId"):
                expWavelengthId = [];
                for lineInd in range(1,len(row)): 
                    expWavelengthId.append(row[lineInd]);                    
            elif(varName == "expChosenWavelength"):
                expChosenWavelength = [];
                for lineInd in range(1,len(row)): 
                    expChosenWavelength.append(row[lineInd]);
            elif(varName =="expPower"):
                expPower = [];
                for lineInd in range(1,len(row)): 
                    expPower.append(row[lineInd]);
            elif(varName =="expChosenPower"):
                expChosenPower = [];
                for lineInd in range(1,len(row)): 
                    expChosenPower.append(row[lineInd]);
            elif(varName == "expBeamSplitterVis"):
                expBeamSplitterVis = [];
                for lineInd in range(1,len(row)): 
                    expBeamSplitterVis.append(row[lineInd]);
            elif(varName == "expBeamSplitterVisName"):
                expBeamSplitterVisName = [];
                for lineInd in range(1,len(row)): 
                    expBeamSplitterVisName.append(row[lineInd]);
            elif(varName == "expBeamSplitterVisPosition"):
                expBeamSplitterVisPosition = [];
                for lineInd in range(1,len(row)): 
                    expBeamSplitterVisPosition.append(row[lineInd]);
            elif(varName == "expChosenBeamSplitterVis"):
                expChosenBeamSplitterVis = []
                for lineInd in range(1,len(row)): 
                    expChosenBeamSplitterVis.append(row[lineInd]);
            elif(varName == "expBeamSplitterInVis"):
                expBeamSplitterInVis = [];
                for lineInd in range(1,len(row)): 
                    expBeamSplitterInVis.append(row[lineInd]);
            elif(varName == "expBeamSplitterInVisName"):
                expBeamSplitterInVisName = [];
                for lineInd in range(1,len(row)): 
                    expBeamSplitterInVisName.append(row[lineInd]);
            elif(varName == "expBeamSplitterInVisPosition"):
                expBeamSplitterInVisPosition = [];
                for lineInd in range(1,len(row)): 
                    expBeamSplitterInVisPosition.append(row[lineInd]);
            elif(varName == "expChosenBeamSplitterInVis"):
                expChosenBeamSplitterInVis = [];
                for lineInd in range(1,len(row)): 
                    expChosenBeamSplitterInVis.append(row[lineInd]);
            elif(varName == "expChosenExperiment"): #Short, long, linearity
                expChosenExperiment = [];
                for lineInd in range(1,len(row)): 
                    expChosenExperiment.append(eval(row[lineInd]));
            elif(varName == "expShortInterval"):
                expShortInterval = row[1];
            elif(varName == "expShortDuration"):
                expShortDuration = row[1];
            elif(varName == "expLongInterval"):
                expLongInterval = row[1];
            elif(varName == "expLongDuration"):
                expLongDuration = row[1];
            elif(varName == "expLinearStep"):
                expLinearStep = row[1];
            elif(varName == "expLinearDuration"):
                expLinearDuration = row[1];
            elif(varName == "expLocation"):
                expLocation = row[1];
            #processedLines += 1
    
    
    # The (MTB) active configuration is always available and contains unseful 
    # information, including the specific wavelengths for all the lines.
    
    currentConfigFile = getActiveConfig(MTBpath)
    activeTree = safeLoadXML(currentConfigFile)
    activeRoot = activeTree.getroot()

    # Connection to the power meter, established during the startup
    tlPM = connectPowerMeter();


    try:

        # Selection window for loading from czexp (experiment) files ####################################
        czexpWin = ZenWindow();
        # Check if wavelength and filters are read from experiment files 
        czexpWin.Initialize('Standard multi-line power and stability assesment.\nQUAREP Initiative, 2023');
        czexpWin.AddCheckbox("czexpFiles","Wavelength and filters from czexp files",False,"1","0");
        winOutput = czexpWin.Show();
    
        if (winOutput.HasCanceled):
            tlPM.close()
            print('\nConnexion to power meter closed\n')
            sys.exit();
    
        czexp = winOutput.GetValue("czexpFiles");
        fileList = os.listdir(str(expPath));
        filteredList = [elem for elem in fileList if elem.Contains(expPrefix)];
        print('Available experiment files: '+str(filteredList));
        # In case there is a BS it will be found later
        # Corresponding filter to wavelength 405, 445, 488, 514, 561, 
        # 594, 633, 639, 730 depends on microscope
        mainBeamSplitter = None
  
        
        if czexp:
            # experiment files available: take wavelengths from them,
            # finding the enabled lines in the files.
            expWavelength = [];
            expChosenWavelength = [];
            expWavelengthId = [];
            expDetectionMode = [];
            
            counter = 0;
            for file in filteredList:
    
                # Load each czexp file:
                xmlFile = expPath + file
                xmlTree = safeLoadXML(xmlFile)
                xmlRoot = xmlTree.getroot()
    
                # Get detection mode
                expDetectionMode.append(getDetectionMode(xmlTree));
                if expDetectionMode[counter] == 'LSM':
                    assignLSM(xmlTree, counter);
                elif expDetectionMode[counter] == 'WF':
                    assignColibri(xmlTree, counter);
            
            print('Detection modes: '+str(expDetectionMode));
            
        else:
            # There must be at least one experiment file available. The mode will be 
            # taken from it. For now all lines will be assigned to the same value. This
            # can be improved by finding line types first.

            #if 'expWavelength' not in globals():
        
            expWavelength = [];
            expWavelengthId = [];
            
            # Copy the available file to avoid modifying it:
            originalFile = expPath + filteredList[0];
            baseXMLFile = expPath + 'tempExp.czexp';
            copyfile(originalFile, baseXMLFile);
            baseXMLTree = safeLoadXML(baseXMLFile)
            
            # Get detection mode
            expDetectionMode = [];
            expDetectionMode.append(getDetectionMode(baseXMLTree));
            if expDetectionMode[0] == 'LSM':
                expWavelengthId = getLaserIdFromAPI(); 
                expWavelength = getLaserWavelengths(baseXMLTree);
            elif expDetectionMode[0] == 'WF':
                expWavelengthId = getLEDIdFromAPI();
                expWavelength = getLedWavelengths();
            print('Detection modes (copied from '+ originalFile + ') : '+str(expDetectionMode));
            
            #if 'expBeamSplitterVis' not in globals():
            # Visible light Beam Splitters
            expBeamSplitterVis = [];
            expBeamSplitterVisName = [];
            expBeamSplitterVisPosition = [];
            mainBeamSplitter = activeTree.find(".//Component[@DisplayName='Main Beam Splitter VIS']");
            if(mainBeamSplitter == None):
                print('No beam splitter for visible light')
            else:
                visBSAvailable = True;
                getBeamSplittersVis();
            #if 'expBeamSplitterInVis' not in globals():
            # Invisible light Beam Splitters
            expBeamSplitterInVis = [];
            expBeamSplitterInVisName = [];
            expBeamSplitterInVisPosition = [];
            mainBeamSplitterInVis = activeTree.find(".//Component[@DisplayName='Main Beam Splitter INVIS']");
            if(mainBeamSplitterInVis == None):
                print('No UV/IR beam splitters.')
            else:    
                invBSAvailable = True;
                getBeamSplittersInVis();
      
        # Set available power
        if 'expPower' not in globals():
            expPower = [];
            expPower = ('5','20','80','100');
    
        # User interface to select measurements ##########################################################################
        mainWin = ZenWindow();
        mainWin.Initialize('Standard multi-line power and stability assesment.\nQUAREP Initiative, 2023');
        mainWin.AddLabel('Choose which lasers should be measured:','0','0-1');
    
        # Headline of user interface 
        boxRow = 1;
        boxCol = 0;
        mainWin.AddLabel('Wavelength',str(boxRow),str(boxCol));
        boxCol = boxCol + 1;
        if not czexp:
            if visBSAvailable:
                mainWin.AddLabel('Beam splitter Vis',str(boxRow),str(boxCol));
                boxCol += 1;
            if invBSAvailable:
                mainWin.AddLabel('Beam splitter InVis',str(boxRow),str(boxCol));
                boxCol += 1;
        mainWin.AddLabel('Power',str(boxRow),str(boxCol));
        
        # Wavelength and beam splitters ........................................................................................
        boxRow += 1
        counter = 0;
    
        for lineInd in range(0,len(expWavelength)):
            boxCol = 0;
            if 'expChosenWavelength' not in globals():
                mainWin.AddCheckbox(str(expWavelength[lineInd]),'Spectral: ' + str(expWavelength[lineInd])+" nm",True,str(boxRow),str(boxCol))
            elif len(expChosenWavelength) > counter:
                if lineInd == int(expChosenWavelength[counter]):
                    mainWin.AddCheckbox(str(expWavelength[lineInd]),'Spectral: ' + str(expWavelength[lineInd])+" nm",True,str(boxRow),str(boxCol));
                    counter += 1;
                else:
                    mainWin.AddCheckbox(str(expWavelength[lineInd]),'Spectral: ' + str(expWavelength[lineInd])+" nm",False,str(boxRow),str(boxCol));
            else:
                mainWin.AddCheckbox(str(expWavelength[lineInd]),'Spectral: ' + str(expWavelength[lineInd])+" nm",False,str(boxRow),str(boxCol));
            if czexp:
                boxRow += 1
            else: 
                
                if 'expChosenBeamSplitterVis' not in globals() and visBSAvailable:
                    boxCol += 1;
                    notFound = True;
                    for i in range(0,len(expBeamSplitterVis)):
                        if expBeamSplitterVisName[i].find(str(expWavelength[lineInd])) != -1: 
                            mainWin.AddDropDown('expBeamSplitterVis'+str(expWavelength[lineInd]),'',expBeamSplitterVisName,i,str(boxRow),str(boxCol));
                            notFound = False;
                            break;
                    if notFound:
                        mainWin.AddDropDown('expBeamSplitterVis'+str(expWavelength[lineInd]),'',expBeamSplitterVisName,0,str(boxRow),str(boxCol));
                elif visBSAvailable:
                    boxCol += 1;
                    mainWin.AddDropDown('expBeamSplitterVis'+str(expWavelength[lineInd]),'',expBeamSplitterVisName,int(expChosenBeamSplitterVis[lineInd]),str(boxRow),str(boxCol));
                
                if 'expChosenBeamSplitterInVis' not in globals() and invBSAvailable:
                    boxCol += 1;
                    notFound = True;
                    for i in range(0,len(expBeamSplitterInVis)):
                        if expBeamSplitterInVisName[i].find(str(expWavelength[lineInd])) != -1: 
                            mainWin.AddDropDown('expBeamSplitterInVis'+str(expWavelength[lineInd]),'',expBeamSplitterInVisName,i,str(boxRow),str(boxCol));
                            notFound = False;
                            break;
                    if notFound:
                        mainWin.AddDropDown('expBeamSplitterInVis'+str(expWavelength[lineInd]),'',expBeamSplitterInVisName,0,str(boxRow),str(boxCol));
                elif invBSAvailable:
                    boxCol += 1;
                    mainWin.AddDropDown('expBeamSplitterInVis'+str(expWavelength[lineInd]),'',expBeamSplitterInVisName,int(expChosenBeamSplitterInVis[lineInd]),str(boxRow),str(boxCol));
                boxRow += 1
        lastBoxRow = boxRow;
        boxCol += 1;
        boxRow = 2;
    
        # Power check boxes ........................................................................................
        counter = 0;
        for lineInd in range(0,len(expPower)):
            if 'expChosenPower' not in globals():
                mainWin.AddCheckbox(str(expPower[lineInd]),str(expPower[lineInd])+' %',False,str(boxRow),str(boxCol));
            elif len(expChosenPower) > counter:
                if lineInd == int(expChosenPower[counter]):
                   mainWin.AddCheckbox(str(expPower[lineInd]),str(expPower[lineInd])+' %',True,str(boxRow),str(boxCol));
                   counter += 1;
                else:
                    mainWin.AddCheckbox(str(expPower[lineInd]),str(expPower[lineInd])+' %',False,str(boxRow),str(boxCol));
            else:
                mainWin.AddCheckbox(str(expPower[lineInd]),str(expPower[lineInd])+' %',False,str(boxRow),str(boxCol));
            boxRow +=1
        if boxRow > lastBoxRow:
            lastBoxRow = boxRow;
        boxCol = 0;
        boxRow = lastBoxRow + 1;
    
        # Short, long and linear measurements ......................................................................................
        if 'expChosenExperiment' not in globals():
            mainWin.AddCheckbox('short','Short measurement',False,str(boxRow),str(boxCol)+'-'+str(boxCol+1));
            boxCol += 2;
            mainWin.AddCheckbox('long','Long measurement',False,str(boxRow),str(boxCol)+'-'+str(boxCol+1));
            boxCol += 2;
            mainWin.AddCheckbox('linear','Linear measurement',False,str(boxRow),str(boxCol)+'-'+str(boxCol+1));
        else:
            mainWin.AddCheckbox('short','Short measurement',expChosenExperiment[0],str(boxRow),str(boxCol)+'-'+str(boxCol+1));
            boxCol += 2;
            mainWin.AddCheckbox('long','Long measurement',expChosenExperiment[1],str(boxRow),str(boxCol)+'-'+str(boxCol+1));
            boxCol += 2;
            mainWin.AddCheckbox('linear','Linear measurement',expChosenExperiment[2],str(boxRow),str(boxCol)+'-'+str(boxCol+1));
        boxCol = 0;
        boxRow += 1;
        
        # Durations, intervals and steps ..........................................................................................
        
        if 'expShortInterval' not in globals():
            mainWin.AddTextBox('shortInterval','short interval [s]',1,str(boxRow),str(boxCol)+'-'+str(boxCol+1));
        else:
            mainWin.AddTextBox('shortInterval','short interval [s]',expShortInterval,str(boxRow),str(boxCol)+'-'+str(boxCol+1));
        boxRow += 1;
        if 'expShortDuration' not in globals():
            mainWin.AddTextBox('shortDuration','short duration [s]',300,str(boxRow),str(boxCol)+'-'+str(boxCol+1));
        else:
            mainWin.AddTextBox('shortDuration','short duration [s]',expShortDuration,str(boxRow),str(boxCol)+'-'+str(boxCol+1));
        boxRow -= 1;
        boxCol += 2;
        
        if 'expLongInterval' not in globals():
            mainWin.AddTextBox('longInterval','Long interval [s]',5,str(boxRow),str(boxCol)+'-'+str(boxCol+1));
        else:
            mainWin.AddTextBox('longInterval','Long interval [s]',expLongInterval,str(boxRow),str(boxCol)+'-'+str(boxCol+1));
        boxRow += 1
        if 'expLongDuration' not in globals():
            mainWin.AddTextBox('longDuration','Long duration [min]',120,str(boxRow),str(boxCol)+'-'+str(boxCol+1));
        else:
            mainWin.AddTextBox('longDuration','Long duration [min]',expLongDuration,str(boxRow),str(boxCol)+'-'+str(boxCol+1));
        boxRow -= 1;
        boxCol += 2;
        
        if 'expLinearStep' not in globals():
            mainWin.AddTextBox('linearStep','linear step [%]',1,str(boxRow),str(boxCol)+'-'+str(boxCol+1));
        else:
            mainWin.AddTextBox('linearStep','linear step [%]',expLinearStep,str(boxRow),str(boxCol)+'-'+str(boxCol+1));
        boxRow += 1;
        if 'expLinearDuration' not in globals():
            mainWin.AddTextBox('linearDuration','phase duration [s]',30,str(boxRow),str(boxCol)+'-'+str(boxCol+1));
        else:
            mainWin.AddTextBox('linearDuration','phase duration [s]',expLinearDuration,str(boxRow),str(boxCol)+'-'+str(boxCol+1));
        boxRow += 1;
    
        winOutput = mainWin.Show();
        if (winOutput.HasCanceled):
            tlPM.close()
            sys.exit();
    
        # Initialize list for active selection
        expChosenWavelength = [];
        if czexp:
            expChosenfilteredList = [];
        else:
            expChosenBeamSplitterVis = [];
            expChosenBeamSplitterVisPosition = [];
            expChosenBeamSplitterInVis = [];
            expChosenBeamSplitterInVisPosition = [];
      
        # Write laser lines and corresponding beam splitters into a list after selection
        for lineInd in range(0,len(expWavelength)):
            if winOutput.GetValue(str(expWavelength[lineInd])):
                print(winOutput.GetValue(str(expWavelength[lineInd])+"nm"));
                print('Adding wavelength: ' + str(expWavelength[lineInd]) + 'nm');
                expChosenWavelength.append(lineInd);
                if czexp:
                    expChosenfilteredList.append(filteredList[lineInd]);
            if not czexp:
                if(visBSAvailable):
                    expBeamSplitterVisIndex = expBeamSplitterVisName.index(winOutput.GetValue('expBeamSplitterVis'+str(expWavelength[lineInd])));
                    expChosenBeamSplitterVis.append(expBeamSplitterVisIndex);
                if(invBSAvailable):
                    expBeamSplitterInVisIndex = expBeamSplitterInVisName.index(winOutput.GetValue('expBeamSplitterInVis'+str(expWavelength[lineInd])));
                    expChosenBeamSplitterInVis.append(expBeamSplitterInVisIndex);
            
        # Write power into a list after selection
        expChosenPower = [];
        for lineInd in range(0,len(expPower)):
            #print(winOutput.GetValue(str(expPower[lineInd])));
            print('adding power setting: ' + str(expPower[lineInd]));
            if winOutput.GetValue(str(expPower[lineInd])):
                expChosenPower.append(lineInd);
    
        if winOutput.GetValue('short'):
            short = True;
            expShortDuration = winOutput.GetValue('shortDuration');
            expShortInterval = winOutput.GetValue('shortInterval');
        else: 
            short = False;
            expShortDuration = 0;
            expShortInterval = winOutput.GetValue('shortInterval');
        if winOutput.GetValue('long'):
            long = True;
            expLongDuration = winOutput.GetValue('longDuration');
            expLongInterval = winOutput.GetValue('longInterval');
        else: 
            long = False;
            expLongDuration = 0;
            expLongInterval = winOutput.GetValue('longInterval');
        if winOutput.GetValue('linear'):
            linear = True;
            expLinearDuration = winOutput.GetValue('linearDuration');
            expLinearStep = winOutput.GetValue('linearStep');
        else: 
            linear = False;
            expLinearDuration = 0;
            expLinearStep = winOutput.GetValue('linearStep');
    
        # User interface experiment additional data
        if not czexp:
            ConfigWin = ZenWindow();
            ConfigWin.Initialize('Additional setting');
            ConfigWin.AddLabel('Set additional settings:');
        
            boxCol = 0
            boxRow = 1
            if 'expName' in globals():
                ConfigWin.AddTextBox('expName','Experiment name',expName,str(boxRow),str(boxCol));
            else:
                ConfigWin.AddTextBox('expName','Experiment name','',str(boxRow),str(boxCol));
            boxRow += 1
            if 'expPath' in globals():
                ConfigWin.AddTextBox('expPath','Experiment path',expPath,str(boxRow),str(boxCol));
            else:
                ConfigWin.AddTextBox('expPath','Experiment path','',str(boxRow),str(boxCol));
            boxRow += 1
            if 'expPrefix' in globals():
                ConfigWin.AddTextBox('expPrefix','Experiment prefix',expPrefix,str(boxRow),str(boxCol));
            else:
                ConfigWin.AddTextBox('expPrefix','Experiment prefix','',str(boxRow),str(boxCol));
            boxRow += 1
            if 'dataSavePath' in globals():
                ConfigWin.AddTextBox('dataSavePath','Data save path',dataSavePath,str(boxRow),str(boxCol));
            else:
                ConfigWin.AddTextBox('dataSavePath','Data save path','',str(boxRow),str(boxCol));
            boxRow += 1
            if 'dataSavePrefix' in globals():
                ConfigWin.AddTextBox('dataSavePrefix','Data save prefix',dataSavePrefix,str(boxRow),str(boxCol));
            else:
                ConfigWin.AddTextBox('dataSavePrefix','Data save prefix','',str(boxRow),str(boxCol));
            boxRow += 1
            if 'dataSaveExt' in globals():
                ConfigWin.AddTextBox('dataSaveExt','Data save extension',dataSaveExt,str(boxRow),str(boxCol));
            else:
                ConfigWin.AddTextBox('dataSaveExt','Data save extension','',str(boxRow),str(boxCol));
            boxRow += 1
        
            ConfigWin.AddCheckbox('save','Save data in config file',True,str(boxRow),str(boxCol))
        
            winOutput = ConfigWin.Show();
            if (winOutput.HasCanceled):
                tlPM.close()
                print('\nConnexion to power meter closed\n')
                sys.exit();
        
            if winOutput.GetValue('save'):
                fout = 0;
                fout = open(measConfigFile,'w');
                fout.write('Varname,value\n');
                fout.write('dataSavePath,' + winOutput.GetValue('dataSavePath') + '\n');
                fout.write('dataSavePrefix,' + winOutput.GetValue('dataSavePrefix') + '\n');
                fout.write('dataSaveExt,' + winOutput.GetValue('dataSaveExt') + '\n');
                fout.write('expPath,' + winOutput.GetValue('expPath') + '\n');
                fout.write('expPrefix,' + winOutput.GetValue('expPrefix') + '\n');
                fout.write('expName,' + winOutput.GetValue('expName') + '\n');
                tmpDetectionMode = '';
                for detectionMode in expDetectionMode:
                    tmpDetectionMode += ',' + str(detectionMode);
                fout.write('expDetectionMode' + tmpDetectionMode + '\n');
                tmpWavelength = '';
                for wavelength in expWavelength:
                    tmpWavelength += ',' + str(wavelength);
                fout.write('expWavelength' + tmpWavelength + '\n');
                tmpChosenWavelength = '';
                tmpWavelengthId = '';
                for WavelengthId in expWavelengthId:
                    tmpWavelengthId += ',' + str(WavelengthId);
                fout.write('expWavelengthId' + tmpWavelengthId + '\n');
                for chosenWavelength in expChosenWavelength:
                    tmpChosenWavelength += ',' + str(chosenWavelength);
                fout.write('expChosenWavelength' + tmpChosenWavelength + '\n');
                tmpPower = '';
                for Power in expPower:
                    tmpPower += ',' + str(Power);
                fout.write('expPower' + tmpPower + '\n');
                tmpChosenPower = '';
                for chosenPower in expChosenPower:
                    tmpChosenPower += ',' + str(chosenPower);
                fout.write('expChosenPower' + tmpChosenPower + '\n');
                
                if visBSAvailable:
                    tmpBeamSplitterVis = '';
                    for BeamSplitterVis in expBeamSplitterVis:
                        tmpBeamSplitterVis += ',' + BeamSplitterVis
                    fout.write('expBeamSplitterVis' + tmpBeamSplitterVis + '\n');
                    tmpBeamSplitterVisName = '';
                    for BeamSplitterVisName in expBeamSplitterVisName:
                        tmpBeamSplitterVisName += ',' + str(BeamSplitterVisName)
                    fout.write('expBeamSplitterVisName' + tmpBeamSplitterVisName + '\n');
                    tmpBeamSplitterVisPosition = '';
                    for BeamSplitterVisPosition in expBeamSplitterVisPosition:
                        tmpBeamSplitterVisPosition += ',' + str(BeamSplitterVisPosition)
                    fout.write('expBeamSplitterVisPosition' + tmpBeamSplitterVisPosition + '\n');
                    tmpChosenBeamSplitterVis = '';
                    for chosenBeamSplitterVis in expChosenBeamSplitterVis:
                        tmpChosenBeamSplitterVis += ',' + str(chosenBeamSplitterVis)
                    fout.write('expChosenBeamSplitterVis' + tmpChosenBeamSplitterVis + '\n');
                if invBSAvailable:
                    tmpBeamSplitterInVis = '';
                    for BeamSplitterInVis in expBeamSplitterInVis:
                        tmpBeamSplitterInVis += ',' + BeamSplitterInVis
                    fout.write('expBeamSplitterInVis' + tmpBeamSplitterInVis + '\n');
                    tmpBeamSplitterInVisName = '';
                    for BeamSplitterInVisName in expBeamSplitterInVisName:
                        tmpBeamSplitterInVisName += ',' + str(BeamSplitterInVisName)
                    fout.write('expBeamSplitterInVisName' + tmpBeamSplitterInVisName + '\n');
                    tmpBeamSplitterInVisPosition = '';
                    for BeamSplitterInVisPosition in expBeamSplitterInVisPosition:
                        tmpBeamSplitterInVisPosition += ',' + str(BeamSplitterInVisPosition)
                    fout.write('expBeamSplitterInVisPosition' + tmpBeamSplitterInVisPosition + '\n');
                    tmpChosenBeamSplitterInVis = '';
                    for chosenBeamSplitterInVis in expChosenBeamSplitterInVis:
                        tmpChosenBeamSplitterInVis += ',' + str(chosenBeamSplitterInVis)
                    fout.write('expChosenBeamSplitterInVis' + tmpChosenBeamSplitterInVis + '\n');
                fout.write('expChosenExperiment,' + str(short) + ',' + str(long) + ',' + str(linear) + '\n');
                fout.write('expShortDuration,' + str(expShortDuration) + '\n');
                fout.write('expShortInterval,' + str(expShortInterval) + '\n');
                fout.write('expLongDuration,' + str(expLongDuration) + '\n');
                fout.write('expLongInterval,' + str(expLongInterval) + '\n');
                fout.write('expLinearStep,' + str(expLinearStep) + '\n');
                fout.write('expLinearDuration,' + str(expLinearDuration) + '\n');
                fout.close()
    
        # Short term measurements #######################################################################
        
        if short and expShortDuration != 0:
            print("\nShort term stability: \n" +
                  "Recommended settings: \n" + 
                  "  - 5 minutes per line or point, \n" +
                  "  - 1 second average.\n" + 
                  "Will be executed sequentially (line after line)\n");
            
            # The files will be saved into folders named using a time stamp if the next lines are uncommented
            # currPathStr = dataSavePath + '\\'+ dateTimeStr + '\\'
            # if not (os.path.exists(currPathStr)):
            #    os.mkdir(currPathStr)
            
            if czexp:
                
                # Preparation phase: We overwrite desired powers ......................................
                for lineInd in range(0,len(expChosenfilteredList)):
                    xmlFile = expPath + expChosenfilteredList[lineInd];
                    print('loading from: ' + xmlFile)
                    xmlTree = safeLoadXML(xmlFile)
                    xmlRoot = xmlTree.getroot();
                    
                    if expDetectionMode[lineInd] == 'WF':
                        xmlLED = xmlTree.find('.//HardwareSetting[@Name="Before [ANS] Smart"]');
                        if xmlLED is None:
                            xmlLED = xmlTree.find('.//HardwareSetting[@Name="Before [CNF] Smart"]');
                        xmlLightSource = xmlLED.find(".//ParameterCollection[@Id='" + expWavelengthId[expChosenWavelength[lineInd]] + "']");    
                    else:
                        xmlLightSource = xmlTree.find(".//ParameterCollection[@Id='" + expWavelengthId[expChosenWavelength[lineInd]] + "']");
                
                    for spower in expChosenPower:            
                        xmlLightSource[1].text = expPower[spower];
                        safeWriteXML(xmlFile, xmlRoot, xmlTree)
                
                        # Execution phase, looped over power choices ...........................................................
                
                        # Setup experiment
                        experiment1 = ZenExperiment();
                        print('loading: ' + xmlFile)                
                        experiment1.Load(xmlFile);
                        Zen.Acquisition.Experiments.Add(experiment1);
    
                        # Turn on light source or laser
                        if expDetectionMode[lineInd] == 'LSM':
                            Zen.Acquisition.StartContinuous(experiment1);
                        elif expDetectionMode[lineInd] == 'WF':
                            Zen.Acquisition.StartLive(experiment1);
                        
                        # Measure and write to output file
                        time.sleep(1);
                        outputFileName = dataSavePath + dataSavePrefix + dateTimeStr + '_' + str(expWavelength[expChosenWavelength[lineInd]]) + '_short_' + str(expPower[spower]) + dataSaveExt
                        print('wavelength: ' + str(expWavelength[expChosenWavelength[lineInd]]) + ' nm; power: ' + str(expPower[spower]) + ' %; save path: ' + outputFileName + '; duration: ' + str(expShortDuration) + ' ; average time: ' + str(expShortInterval))
                        measure(expWavelength[expChosenWavelength[lineInd]], expPower[spower],outputFileName, expShortDuration, expShortInterval,tlPM)
                        
                        # Turn on light source or laser
                        if expDetectionMode[lineInd] == 'LSM':
                            Zen.Acquisition.StopContinuous(experiment1);
                        elif expDetectionMode[lineInd] == 'WF':
                            Zen.Acquisition.StopLive(experiment1);
            
            # Configurations taken from the created file ........................................
            else:        
                # No specific czexp files. One will be used and modified
                for lineInd in range(0,len(expChosenWavelength)):
                    for spower in expChosenPower:
    
                        # Preparation phase ..................................................................                    
                        
                        # We create the configurations from the base XML (available globally)
                        currInd = expWavelength.IndexOf(expChosenWavelength[lineInd]);
                        newConfig = expPath + 'temp' + str(expChosenWavelength[lineInd])+ '.czexp';                    
                        originalFile = expPath + filteredList[0];
                        copyfile(originalFile, newConfig);
    
                        # Turn on light source
                        print('Finding available lines from the experiment files: \n' + baseXMLFile)
                        disableAllLasers(newConfig);
                        print('all lasers off');
                        setLaserStatus(expWavelengthId[expChosenWavelength[lineInd]], expWavelength[expChosenWavelength[lineInd]], newConfig, True, expDetectionMode[0]);
                        print('line '+ str(expWavelength[expChosenWavelength[lineInd]]) +' nm activated');
                        setLaserPower(expWavelengthId[expChosenWavelength[lineInd]], newConfig, expPower[spower], expDetectionMode[0]);
                        print('power set to ' + str(expPower[spower]) + '%');
    
                        # Configure beam splitters
                        if expDetectionMode[0] == 'LSM':
                            if(visBSAvailable & len(expChosenBeamSplitterVis)>0): 
                                visBS = expChosenBeamSplitterVis[lineInd]
                            else:
                                visBS = []
                            if(invBSAvailable & len(expChosenBeamSplitterInVis)>0):
                                invBS = expChosenBeamSplitterInVis[lineInd]
                            else:
                                invBS = []
                            if(len(visBS)>0 | len(invBS)>0):
                                setBeamSplitters(newConfig,visBS,invBS)
    
                        #Execution phase .....................................................................
                        
                        # Setup experiment
                        experiment1 = ZenExperiment();
                        experiment1.Load(newConfig);
                        Zen.Acquisition.Experiments.Add(experiment1);
    
                        # Turn on light source or laser
                        if expDetectionMode[0] == 'LSM':
                            Zen.Acquisition.StartContinuous(experiment1);
                        elif expDetectionMode[0] == 'WF':
                            Zen.Acquisition.StartLive(experiment1);
                        
                        # Set output file and measure
                        time.sleep(0.1);
                        outputFileName = dataSavePath + dataSavePrefix + dateTimeStr + '_' + str(expWavelength[expChosenWavelength[lineInd]]) + '_short_' + str(expPower[spower]) + dataSaveExt
                        print('wavelength: ' + str(expWavelength[expChosenWavelength[lineInd]]) + ' nm; power: ' + expPower[spower] + ' %; save path: ' + outputFileName + '; duration: ' + str(expShortDuration) + ' ; average time: ' + str(expShortInterval))
                        measure(expWavelength[expChosenWavelength[lineInd]], expPower[spower],outputFileName, expShortDuration, expShortInterval,tlPM)
    
                        # Turn off light sources
                        if expDetectionMode[0] == 'LSM':
                            Zen.Acquisition.StopContinuous(experiment1);
                        elif expDetectionMode[0] == 'WF':
                            Zen.Acquisition.StopLive(experiment1);
                print("Power phase completed")
            print("Short term measurement completed")
    
        # Long term measurement ########################################################################
        if long and expLongDuration != 0:
            # The files will be saved into folders named using a time stamp if the next lines are uncommented
            #currPathStr = dataSavePath + '\\'+ dateTimeStr + '\\'
            #if not (os.path.exists(currPathStr)):
            #    os.mkdir(currPathStr)        
        
            print("\nLong term stability: \n" +
                  "Recommended settings: \n" + 
                  "  - 2 hours per line, \n" +
                  "  - every 5 minutes, \n" +
                  "  - 30 second average.\n" + 
                  "Will be executed in paralel (lines interleaved)");
            
            if czexp:
                # Preparation phase: We overwrite desired powers ......................................
                for lineInd in range(0,len(expChosenfilteredList)):
                    xmlFile = expPath + expChosenfilteredList[lineInd];
                    print('loading from: '+xmlFile)
                    xmlTree = safeLoadXML(xmlFile)
                    xmlRoot = xmlTree.getroot();
                    
                    if expDetectionMode[lineInd] == 'WF':
                        xmlLED = xmlTree.find('.//HardwareSetting[@Name="Before [ANS] Smart"]');
                        if xmlLED is None:
                            xmlLED = xmlTree.find('.//HardwareSetting[@Name="Before [CNF] Smart"]');
                        xmlLightSource = xmlLED.find(".//ParameterCollection[@Id='" + expWavelengthId[expChosenWavelength[lineInd]] + "']");    
                    else:
                        xmlLightSource = xmlTree.find(".//ParameterCollection[@Id='" + expWavelengthId[expChosenWavelength[lineInd]] + "']");
                
                    for spower in expChosenPower:            
                        xmlLightSource[1].text = expPower[spower];
                        safeWriteXML(xmlFile, xmlRoot, xmlTree)
                
                        # Execution phase, looped over power choices ...........................................................
                
                        # Setup experiment
                        experiment1 = ZenExperiment();
                        print('loading: ' + xmlFile)                
                        experiment1.Load(xmlFile);
                        Zen.Acquisition.Experiments.Add(experiment1);
    
                        # Turn on light source or laser
                        if expDetectionMode[lineInd] == 'LSM':
                            Zen.Acquisition.StartContinuous(experiment1);
                        elif expDetectionMode[lineInd] == 'WF':
                            Zen.Acquisition.StartLive(experiment1);
                        
                        # Measure and write to output file
                        time.sleep(1);
                        outputFileName = dataSavePath + dataSavePrefix + dateTimeStr + '_' + str(expWavelength[expChosenWavelength[lineInd]]) + '_long_' + str(expPower[spower]) + dataSaveExt
                        print('wavelength: ' + str(expWavelength[expChosenWavelength[lineInd]]) + ' nm; power: ' + str(expPower[spower]) + ' %; save path: ' + outputFileName + '; duration: ' + str(expLongDuration) + ' ; average time: ' + str(expLongInterval))
                        measure(expWavelength[expChosenWavelength[lineInd]], expPower[spower],outputFileName, expLongDuration, expLongInterval,tlPM)
                        
                        # Turn on light source or laser
                        if expDetectionMode[lineInd] == 'LSM':
                            Zen.Acquisition.StopContinuous(experiment1);
                        elif expDetectionMode[lineInd] == 'WF':
                            Zen.Acquisition.StopLive(experiment1);
            else:
                # No specific czexp files. One will be used and modified
                for lineInd in range(0,len(expChosenWavelength)):
                    for spower in expChosenPower:
    
                        # Preparation phase ..................................................................                    
                        
                        # We create the configurations from the base XML (available globally)
                        currInd = expWavelength.IndexOf(expChosenWavelength[lineInd]);
                        newConfig = expPath + 'temp' + str(expChosenWavelength[lineInd])+ '.czexp';                    
                        originalFile = expPath + filteredList[0];
                        copyfile(originalFile, newConfig);
    
                        # Turn on light source
                        print('Finding available lines from the experiment files: \n' + baseXMLFile)
                        
                        
                        disableAllLasers(newConfig);
                        print('all lasers off');
                        setLaserStatus(expWavelengthId[expChosenWavelength[lineInd]], expWavelength[expChosenWavelength[lineInd]], newConfig, True, expDetectionMode[0]);
                        print('line '+ str(expWavelength[expChosenWavelength[lineInd]]) +' nm activated');
                        setLaserPower(expWavelengthId[expChosenWavelength[lineInd]], newConfig, expPower[spower], expDetectionMode[0]);
                        print('power set to ' + str(expPower[spower]) +  '%');
    
                        # Configure beam splitters
                        if expDetectionMode[0] == 'LSM':
                            if(visBSAvailable & len(expChosenBeamSplitterVis)>0): 
                                visBS = expChosenBeamSplitterVis[lineInd]
                            else:
                                visBS = []
                            if(invBSAvailable & len(expChosenBeamSplitterInVis)>0):
                                invBS = expChosenBeamSplitterInVis[lineInd]
                            else:
                                invBS = []
                            if(len(visBS)>0 | len(invBS)>0):
                                setBeamSplitters(newConfig,visBS,invBS)
    
                        #Execution phase .....................................................................
                        
                        # Setup experiment
                        experiment1 = ZenExperiment();
                        experiment1.Load(newConfig);
                        Zen.Acquisition.Experiments.Add(experiment1);
    
                        # Turn on light source or laser
                        if expDetectionMode[0] == 'LSM':
                            Zen.Acquisition.StartContinuous(experiment1);
                        elif expDetectionMode[0] == 'WF':
                            Zen.Acquisition.StartLive(experiment1);
                        
                        # Set output file and measure
                        time.sleep(0.1);
                        outputFileName = dataSavePath + dataSavePrefix + dateTimeStr + '_' + str(expWavelength[expChosenWavelength[lineInd]]) + '_long_' + str(expPower[spower]) + dataSaveExt
                        print('wavelength: ' + str(expWavelength[expChosenWavelength[lineInd]]) + ' nm; power: ' + expPower[spower] + ' %; save path: ' + outputFileName + '; duration: ' + str(expLongDuration) + ' ; average time: ' + str(expLongInterval))
                        measure(expWavelength[expChosenWavelength[lineInd]], expPower[spower],outputFileName, expLongDuration, expLongInterval,tlPM)
                       
                        # Turn on light source or laser
                        if expDetectionMode[0] == 'LSM':
                            Zen.Acquisition.StartContinuous(experiment1);
                        elif expDetectionMode[0] == 'WF':
                            Zen.Acquisition.StartLive(experiment1);
                            
                print("Power phase completed")
            print("Long term measurement completed")
    
        # Linear measurement ###########################################################################
        if linear and expLinearDuration != 0:
            # The files will be saved into folders named using a time stamp
            #currPathStr = dataSavePath + '\\'+ dateTimeStr + '\\'
            #if not (os.path.exists(currPathStr)):
            #    os.mkdir(currPathStr)        
    
            print("\nLinearity check: \n" +
                  "Suggested settings: \n" + 
                  "  - Full range divided in 10 steps \n" +
                  "  - 3 second average.\n" + 
                  "Will be executed sequentially (line after line)");
    
            #timePerStep = 3 # averaging time
            timePerStep = expLinearDuration;
            
            if czexp:
                for lineInd in range(0,len(expChosenfilteredList)):
                    xmlFile = expPath + expChosenfilteredList[lineInd];
                    print('loading from: ' + xmlFile)
                    xmlTree = safeLoadXML(xmlFile)
                    xmlRoot = xmlTree.getroot();
                    slambda = expChosenWavelength[lineInd]
                    
                    # Preparation phase .....................................................................
                    if expDetectionMode[lineInd] == 'WF':
                        xmlLED = xmlTree.find('.//HardwareSetting[@Name="Before [ANS] Smart"]');
                        if xmlLED is None:
                            xmlLED = xmlTree.find('.//HardwareSetting[@Name="Before [CNF] Smart"]');
                        xmlLightSource = xmlLED.find(".//ParameterCollection[@Id='" + expWavelengthId[expChosenWavelength[lineInd]] + "']");    
                    else:
                        xmlLightSource = xmlTree.find(".//ParameterCollection[@Id='" + expWavelengthId[expChosenWavelength[lineInd]] + "']");
                    
                    # Preparation phase .....................................................................
                    for spower in range(int(expLinearStep),101,int(expLinearStep)):
                        xmlLightSource[1].text = str(spower);
                        safeWriteXML(xmlFile, xmlRoot, xmlTree)
                        
                        # Setup experiment
                        experiment1 = ZenExperiment();
                        print('loading: ' + xmlFile)                
                        experiment1.Load(xmlFile);
                        Zen.Acquisition.Experiments.Add(experiment1);
    
                        # Execution phase phase .............................................................
    
                        # Turn on light source or laser
                        if expDetectionMode[lineInd] == 'Lsm880':
                            Zen.Acquisition.StartContinuous(experiment1);
                        elif expDetectionMode[lineInd] == 'WF':
                            Zen.Acquisition.StartLive(experiment1);
                    
                        # Measure and write to output file
                        time.sleep(1);
                        outputFileName = dataSavePath + dataSavePrefix + dateTimeStr + '_' + str(expWavelength[expChosenWavelength[lineInd]]) + '_linear' + dataSaveExt
                        print('wavelength: ' + str(expWavelength[expChosenWavelength[lineInd]]) + ' nm; power: ' + str(spower) + ' %; save path: ' + outputFileName+'; duration: ' + str(expLinearDuration) + ' ; average time: ' + str(expLinearDuration))
                        measure(expWavelength[expChosenWavelength[lineInd]], str(spower),outputFileName, expLinearDuration, expLinearDuration,tlPM)
                        
                        # Turn on light source or laser
                        if expDetectionMode[lineInd] == 'Lsm880':
                            Zen.Acquisition.StopContinuous(experiment1);
                        elif expDetectionMode[lineInd] == 'WF':
                            Zen.Acquisition.StopLive(experiment1);
            else:
                # No specific czexp files. One will be used and modified
                for lineInd in range(0,len(expChosenWavelength)):
                    
                    slambda = expChosenWavelength[lineInd]
                    
                    # Preparation phase: We create the configurations .................................
                    for spower in range(int(expLinearStep),101,int(expLinearStep)):
                        
                        # starting from the same base experiment file .....................................................                   
                        print('Finding available lines from the experiment files: \n' + baseXMLFile)
                        newConfig = expPath + 'temp' + str(expChosenWavelength[lineInd])+ 'power'+ str(spower) +'.czexp'
                        copyfile(baseXMLFile, newConfig);
    
                        # Preparation phase .....................................................................
                        disableAllLasers(newConfig);
                        print('all lasers off');
                        setLaserStatus(expWavelengthId[expChosenWavelength[lineInd]], expWavelength[expChosenWavelength[lineInd]], newConfig, True, expDetectionMode[0]);
                        print('line '+ str(expWavelength[expChosenWavelength[lineInd]]) +' nm activated');
                        setLaserPower(expWavelengthId[expChosenWavelength[lineInd]], newConfig, spower, expDetectionMode[0]);
                        print('power set to ' + str(spower) + '%');
    
                        # Configure beam splitters
                        if(visBSAvailable & len(expChosenBeamSplitterVis)>0): 
                            visBS = expChosenBeamSplitterVis[lineInd]
                        else:
                            visBS = []
                        if(invBSAvailable & len(expChosenBeamSplitterInVis)>0):
                            invBS = expChosenBeamSplitterInVis[lineInd]
                        else:
                            invBS = []
                        if(len(visBS)>0 | len(invBS)>0):
                            setBeamSplitters(newConfig,visBS,invBS)
    
                        # Execution phase ................................................................            
                    
                        # Setup the experiment:
                        experiment1 = ZenExperiment();
                        experiment1.Load(newConfig);
                        Zen.Acquisition.Experiments.Add(experiment1);
    
                        # Turn on light sources
                        if expDetectionMode[0] == 'LSM':
                            Zen.Acquisition.StartContinuous(experiment1);
                        elif expDetectionMode[0] == 'WF':
                            Zen.Acquisition.StartLive(experiment1);
                        
                        time.sleep(0.1);
                        # Configure output file and measure
                        outputFileName = dataSavePath + dataSavePrefix + dateTimeStr + '_' + str(expWavelength[expChosenWavelength[lineInd]]) + '_linear' + dataSaveExt
                        print('wavelength: ' + str(expWavelength[expChosenWavelength[lineInd]]) + ' nm; power: ' + str(spower) + ' %; save path: ' + outputFileName + '; duration: ' + str(expLinearDuration) + ' ; average time: ' + str(expLinearDuration))
                        measure(expWavelength[expChosenWavelength[lineInd]], str(spower),outputFileName, expLinearDuration, expLinearDuration,tlPM)
                        
                        # Turn off light sources
                        if expDetectionMode[0] == 'LSM':
                            Zen.Acquisition.StopContinuous(experiment1);
                        elif expDetectionMode[0] == 'WF':
                            Zen.Acquisition.StopLive(experiment1);
                print('Wavelength phase completed')
            print('Linear measurement completed');    
        
        tlPM.close()
        print('\nAll measurements completed\n');
        print('Connection to power meter closed\n');
        
    except Exception as e:
        tlPM.close();
        print('\nConnection to power meter closed\n');
        
        exc_type, exc_value, exc_traceback = sys.exc_info() # most recent (if any) by default
         
        traceback_details = {
            'filename': exc_traceback.tb_frame.f_code.co_filename,
            'lineno'  : exc_traceback.tb_lineno,
            'name'    : exc_traceback.tb_frame.f_code.co_name,
            'type'    : exc_type.__name__,
            'message' : exc_value.message, # or see traceback._some_str()
        }
        print(traceback_details);
main()

