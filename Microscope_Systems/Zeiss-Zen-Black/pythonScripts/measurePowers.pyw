from ctypes import cdll, c_long, c_ulong, c_uint32, byref, create_string_buffer, c_bool, c_char_p, c_int, c_int16, \
    c_double, sizeof, c_voidp
from TLPM import TLPM
from datetime import datetime, timedelta
import time
import sys
import os

tlPM = TLPM()
deviceCount = c_uint32()
tlPM.findRsrc(byref(deviceCount))
#print("devices found: " + str(deviceCount.value))
if deviceCount.value<1:
    print("thorlabs power meter not found")
    exit(-1)

resourceName = create_string_buffer(1024)
tlPM.getRsrcName(c_int(0), resourceName)
#print(c_char_p(resourceName.raw).value)

tlPM.open(resourceName, c_bool(True), c_bool(True))

#message = create_string_buffer(1024)
#tlPM.getCalibrationMsg(message)
#print(c_char_p(message.raw).value)

print('Argument List: ',  str(sys.argv))

# first argument is the wavelength
if len(sys.argv) > 1:
    #print(sys.argv[1])
    wavelength = float(sys.argv[1])
    tlPM.setWavelength(c_double(wavelength))

# second argument is the power level
if len(sys.argv) > 2:
    #print(sys.argv[2])
    power_level = int(sys.argv[2])

#third argument is the output file
fout = 0
#append data file

	
if len(sys.argv) > 3:
    #print(sys.argv[2])
    fout = open(sys.argv[3],"a")
    #print(os.stat(sys.argv[3]).st_size)

#check if temperature sensor is connected
temperature = c_double()
try:
    tlPM.measExtNtcTemperature(byref(temperature))
except NameError:
    print("Temperature sensor not connected!")
#check if file is empty, if not print headline
if fout and os.stat(sys.argv[3]).st_size == 0:
    if temperature.value == 0:
        print("timestamp", "wavelength", "setting", "power", end='', sep='\t')
        print("timestamp", "wavelength", "setting", "power", end='', sep='\t', file=fout)
        print("\nYYYY-MM-DD HH:MM:SS", "nm","s","W", end='',sep='\t')
        print("\nYYYY-MM-DD HH:MM:SS", "nm","s","W", end='',sep='\t', file=fout)
    else:
        print("timestamp", "wavelength", "setting", "power", "temperature", end='', sep='\t')
        print("timestamp", "wavelength", "setting", "power", "temperature", end='', sep='\t', file=fout)
        print("\nYYYY-MM-DD HH:MM:SS", "nm", "s", "W", "C", end='',sep='\t')
        print("\nYYYY-MM-DD HH:MM:SS", "nm", "s", "W", "C", end='',sep='\t', file=fout)
	
#fourth argument is the duration and fifth argument is the measurement interval
duration = 5*60 # in seconds, default
if len(sys.argv) > 4:
    #print(sys.argv[4])
    duration = int(sys.argv[4])
if len(sys.argv) > 5:
    #print(sys.argv[5])
    avgTime = int(sys.argv[5])
	
time.sleep(1.5)	#Without this delay the first number is consistently higher than the rest

tmp = c_double()
tlPM.getWavelength(0,byref(tmp))
wavelength = tmp.value

# set starttime and measurement duration
start = datetime.now()
measure_until = start + timedelta(seconds=duration)
average_until = start
while datetime.now() < measure_until:
    average_until += timedelta(seconds=avgTime)
    average_count = 0
    total_power = 0
    total_temperature = 0
    start_average = datetime.now()	
   
    while(datetime.now() < average_until):
        power = c_double()
        tlPM.measPower(byref(power))
        total_power += power.value
        if temperature.value != 0:
            tlPM.measExtNtcTemperature(byref(temperature))
            total_temperature += temperature.value
        average_count += 1

    #calculate arithmetic mean of power and temperature
    total_power /= average_count
    total_temperature /= average_count

    ts = (start_average-start).total_seconds()
    if total_temperature == 0:
        print('\n' + start_average.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3], int(wavelength), power_level,total_power, end='',sep='\t')
        if fout:
            print('\n' + start_average.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],int(wavelength), power_level,total_power, end='', sep='\t', file=fout)
    else:
        print('\n' + start_average.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3], int(wavelength), power_level, total_power, total_temperature, end='', sep='\t')
        if fout:
            print('\n' + start_average.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3], int(wavelength), power_level, total_power, total_temperature, end='', sep='\t', file=fout)
tlPM.close()

#close the file
if fout:
    fout.close()