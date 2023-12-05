The path to this file is hard coded into the QUAREP-LPM.py, currently in lines 587 and 568:

>>       measconfigPath = 'C:\\QUAREP\\'
>>       measConfigFile = measconfigPath+'measurementConfig.csv'

Please make sure that the configuratioin file is saved in the given location, or change it accordingly.

This file includes two fields relevant for the installation of the macro:

dataSavePath: The files will be saved in this folder automatically
expPath: The experiment files have to be stored in this folder in order to be available to the macro.
