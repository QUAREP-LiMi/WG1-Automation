#
# Copyright 2022 Nasser Darwish Miranda

# @author: Nasser Darwish, IST Austria

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
from timeit import default_timer as timer

with open('D:\\FACILITY\\QUAREP\\measurementConfig.csv') as configFile:
    csvReader = csv.reader(configFile, delimiter =",")
    processedLines = 0
    for row in csvReader:
        varName = row[0]
        if (varName == "pythonPath"):
            pythonPath = row[1]
        elif(varName == "scriptPath"):
            scriptPath = row[1]
        elif(varName == "dataSavePath"):
            dataSavePath = row[1]
        elif(varName == "dataSavePrefix"):
            dataSavePrefix = row[1]
        elif(varName == "dataSaveExt"):
            dataSaveExt = row[1]
        elif(varName == "expPath"):
            expPath = row[1]
        elif(varName == "prefix"):
            prefix = row[1]
        elif(varName == "expExt"):
            expExt = row[1]
        processedLines += 1

# Prefix selection window

GUIwin = ZenWindow();

GUIwin.Initialize('Standard multi-line power and stability assesment.\n 2021, QUAREP Consortium');
GUIwin.AddLabel('Prefix of the experiment names to be used:');
GUIwin.AddTextBox('prefixBox', 'Prefix (e.g LPM): ', prefix)
winOutput = GUIwin.Show();

prefix = winOutput.GetValue('prefixBox');
fileList = os.listdir(str(expPath));


filteredList = [elem for elem in fileList if elem.Contains(prefix)];

print(filteredList);


wavelength = [];
lineCount = len(filteredList)
for lineInd in range(0,lineCount):
    tempStr = filteredList[lineInd]
    startInd = tempStr.IndexOf(prefix)
    print(tempStr.Substring(startInd+prefix.Length,3))
    wavelength.append(int(tempStr.Substring(startInd+prefix.Length,3)))

# Second window
LambdaWin = ZenWindow(); 
LambdaWin.Initialize('Standard multi-line power and stability assesment.\n 2021, QUAREP Consortium');
LambdaWin.AddLabel('Choose which lasers should be measured:');

boxRow = 1;
boxCol = 0;
for lineInd in range(0,lineCount):
    LambdaWin.AddCheckbox(str(wavelength[lineInd])+"nm",str(wavelength[lineInd])+"nm",True,
    str(boxRow),str(boxCol))
    if (lineInd+1)%2 == 0:
        boxRow = boxRow+1
        boxCol = 0
    else:
        boxCol = boxCol+1

LambdaWin.AddDropDown("checkType", "Choose the test type", ["short term stability", "long term stability"], 0);
winOutput = LambdaWin.Show();

# Filtering lines after selection
activeLines = []
for lineInd in range(0,lineCount):
    if winOutput.GetValue(str(wavelength[lineInd])+"nm"):
        activeLines.append(lineInd)
linesToCheck = len(activeLines)

# Duration of the measurements, in seconds:
if winOutput.GetValue("checkType") == "short term stability":
    print("short: 5min every second one after another")
    duration = 300;
    interval = 1;
    avgTime = 30;
    durationms = duration * 10# Later we change it to 1000
    # For the short tests lines are checked oine after another
    # Wavelength loop
    for lambdaInd in activeLines:
        slambda = wavelength[lambdaInd]

        # Setup the experiment:
        expString = expPath + prefix + str(slambda) + expExt

        experiment1 = ZenExperiment()
        experiment1.Load(expString)
        Zen.Acquisition.Experiments.Add(experiment1)
        
        # Turn Laser on
        Zen.Acquisition.StartContinuous(experiment1)
        # Run the external software

        time.sleep(1);

        scriptCommand = pythonPath + " " + " " + scriptPath + " " + str(slambda) + " " + dataSavePath + dataSavePrefix + str(slambda) + dataSaveExt + " " + str(timePerLine) + str(avgTime) +" &amp;"
        print(scriptCommand)

        subprocess.call(scriptCommand)
        
        #Zen.Application.Wait(durationms)
        
        #Turn laser off
        Zen.Acquisition.StopContinuous(experiment1)
        # Save the experiment before removing:
        processedStr = expPath + prefix + str(slambda) + expExt
        experiment1.SaveAs(processedStr)
        
    print("Short term measurement completed")

if winOutput.GetValue("checkType") == "long term stability":
    print("long: 2h, every 5min over all lines ")
    duration = 7200;
    interval = 300;
    avgTime = 30;
    # Switching between lines makes sense only for the long test:


    # Time available per line
    switchTime = 0.5 #Assuming 0.5s needed to change between lines
    timePerLine = int(interval / linesToCheck) - switchTime
    print(timePerLine)

    # time loop
    timeExhausted = False
    initialTime = timer()
    while ~timeExhausted:
        currTime = timer()
        # Wavelength loop
        for lambdaInd in activeLines:
            slambda = wavelength[lambdaInd]
            scriptCommand = pythonPath + " " + " " + scriptPath + " " + str(slambda) + " " + dataSavePath + dataSavePrefix + str(slambda) + dataSaveExt + " " + str(timePerLine) + str(avgTime) +" &amp;"

            # Setup the experiment:
            expString = expPath + prefix + str(slambda) + expExt
            print(expString)
            experiment1 = ZenExperiment()            
            experiment1.Load(expString)
            Zen.Acquisition.Experiments.Add(experiment1)
            hardwaresetting1.SetParameter('MTBLM800AttenuatorShutter', 'Position', '5')
            
            # Turn Laser on
            Zen.Acquisition.StartContinuous(experiment1)
            # Run the external software
            subprocess.call(scriptCommand)
            #Turn laser off
            Zen.Acquisition.StopContinuous(experiment1)
        
            # Save the experiment before removing:
            processedStr = expPath + prefix + str(slambda) + expExt
            experiment1.SaveAs(processedStr)
            # Time checks to test only after the wavelength loop completes
            print(currTime-initialTime)
            if currTime-initialTime > duration:
                timeExhausted = True;
                break

    print("Long term measurement completed")
