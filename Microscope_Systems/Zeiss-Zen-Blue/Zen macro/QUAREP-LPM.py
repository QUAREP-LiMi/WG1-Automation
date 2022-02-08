#
# Copyright 2022 Nasser Darwish Miranda
# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following conditions 
# are met:

# 1. Redistributions of source code must retain the above copyright notice, this list of conditions 
# and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions 
# and the following disclaimer in the documentation and/or other materials provided with the 
# distribution.

# 3. Neither the name of the copyright holder nor the names of its contributors may be used to 
# endorse or promote products derived from this software without specific prior written 
# permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND 
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. 
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, 
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT 
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR 
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY 
# OF SUCH DAMAGE.

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
    duration = 60;
    avgTime = 1;
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

        scriptCommand = pythonPath + " " + " " + scriptPath + " " + str(slambda) + " " + dataSavePath + dataSavePrefix + str(slambda) + dataSaveExt + " " + str(duration) + " " + str(avgTime) +" &"
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
    #duration = 7200;
    #interval = 300;
    #avgTime = 30;
    
    duration = 120;
    interval = 20;
    avgTime = 10;
    
    # Switching between lines makes sense only for the long test:


    # Time available per line
    switchTime = 0.5 #Assuming 0.5s needed to change between lines
    timePerLine = int(interval / linesToCheck) - switchTime * (linesToCheck - 1)
    print("Time per line" + str(timePerLine))

    # time loop
    timeExhausted = False
    initialTime = timer()
    while ~timeExhausted:
        currTime = timer()
        # Wavelength loop
        for lambdaInd in activeLines:
            slambda = wavelength[lambdaInd]
            scriptCommand = pythonPath + " " + " " + scriptPath + " " + str(slambda) + " " + dataSavePath + dataSavePrefix + str(slambda) + dataSaveExt + " " + str(timePerLine) + " " + str(avgTime) +" &"

            # Setup the experiment:
            expString = expPath + prefix + str(slambda) + expExt
            print(expString)
            experiment1 = ZenExperiment()            
            experiment1.Load(expString)
            Zen.Acquisition.Experiments.Add(experiment1)
            
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
            elapsedTime = currTime-initialTime
            print("Elapsed time:" + str(elapsedTime))
        if elapsedTime > duration:
            timeExhausted = True;
            break

    print("Long term measurement completed")
