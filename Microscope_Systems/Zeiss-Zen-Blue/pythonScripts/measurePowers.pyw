from ctypes import cdll, c_long, c_ulong, c_uint32, byref, create_string_buffer, c_bool, c_char_p, c_int, c_int16, \
    c_double, sizeof, c_voidp
from TLPM import TLPM
from datetime import datetime, timedelta
import time
import sys

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

#second argument is the output file
fout = 0
#append data file

	
if len(sys.argv) > 2:
    #print(sys.argv[2])
    fout = open(sys.argv[2],"a")
	
duration = 5*60 # in seconds, default
if len(sys.argv) > 3:
    #print(sys.argv[3])
    duration = int(sys.argv[3])
if len(sys.argv) > 4:
    #print(sys.argv[4])
    avgTime = int(sys.argv[4])
	
time.sleep(0.1)	#Without this delay the first number is consistently higher than the rest

tmp = c_double()
tlPM.getWavelength(0,byref(tmp))
wavelength = tmp.value

start = datetime.now()
measure_until = start + timedelta(seconds=duration)
average_until = start
while datetime.now() < measure_until:
    average_until += timedelta(seconds=avgTime)	
    average_count = 0
    total_power = 0
    start_average = datetime.now()	
    while(datetime.now() < average_until):
        power = c_double()
        tlPM.measPower(byref(power))
        total_power += power.value
        average_count += 1
    total_power /= average_count
    ts = (start_average-start).total_seconds()
	
    print(wavelength,'\t',start_average.strftime("%Y-%m-%d %H:%M:%S"),'\t',ts,'\t',total_power)
    if fout:        
        print(wavelength, '\t', start_average.strftime("%Y-%m-%d %H:%M:%S"), '\t', ts, '\t', total_power, file=fout)
tlPM.close()

#close the file
if fout:	
	fid.close()

print('End program')
