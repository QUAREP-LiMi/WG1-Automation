from ctypes import cdll, c_long, c_ulong, c_uint16, c_uint32, byref, create_string_buffer, c_bool, c_char_p, c_int, c_int16, \
    c_double, sizeof, c_voidp
from datetime import datetime, timedelta
from TLPM import TLPM
from TLPMX import TLPMX
import time
import sys
import os

#import win32gui
import win32com.client
import time
import traceback

print('Argument List: ', str(sys.argv))

# first argument is the wavelength
if len(sys.argv) > 1:
    # print(sys.argv[1])
    wavelength = float(sys.argv[1])

# second argument is the power level
if len(sys.argv) > 2:
    # print(sys.argv[2])
    power_level = float(sys.argv[2])

# third argument is the output file
fout = 0
if len(sys.argv) > 3:
    # print(os.stat(sys.argv[3]).st_size)
    fout = open(sys.argv[3], "a")

# fourth argument is the duration
duration = 5 * 60  # in seconds, default
if len(sys.argv) > 4:
    # print(sys.argv[4])
    duration = int(sys.argv[4]) 

# fifth argument is the measurement interval
if len(sys.argv) > 5:
    # print(sys.argv[5])
    avgTime = int(sys.argv[5])

# sixth argument is the integration time
if len(sys.argv) > 6:
    # print(sys.argv[6])
    integration = int(sys.argv[6])
    
# seventh argument states if temperature sensor is connected to Thorlabs PM100 or PM400
if len(sys.argv) > 7:
    if sys.argv[7] == "True":
        thermometer = True
        print('Temperature sensor connected to Thorlabs optical power meter is expected!')
    else:
        thermometer = False 
        print('No temperature sensor is expected!')
#print(thermometer)

# connect to power meter and perform measurement
try:
    # Open connection to Ophir power meter
    OphirCOM = win32com.client.Dispatch("OphirLMMeasurement.CoLMMeasurement")
    # Stop & Close all devices
    OphirCOM.StopAllStreams()
    OphirCOM.CloseAll()
    # Scan for connected Devices
    DeviceList = OphirCOM.ScanUSB()
    if len(DeviceList) != 0:
        DeviceHandle = OphirCOM.OpenUSBDevice(DeviceList[0])	# open first device
        exists = OphirCOM.IsSensorExists(DeviceHandle, 0)
        if exists:
            print("Ophir power meter connected!")

            # check if file is empty, if not print headline
            if fout and os.stat(sys.argv[3]).st_size == 0:
                print("timestamp", "wavelength", "setting", "power", end='', sep='\t')
                print("timestamp", "wavelength", "setting", "power", end='', sep='\t', file=fout)
                print("\nYYYY-MM-DD HH:MM:SS", "nm", "s", "W", end='', sep='\t')
                print("\nYYYY-MM-DD HH:MM:SS", "nm", "s", "W", end='', sep='\t', file=fout)

            print('\n----------Data for S/N {0} ---------------'.format(DeviceList[0]))

            # Set wavelength and range (auto)
            ranges = OphirCOM.GetRanges(DeviceHandle, 0)
            OphirCOM.AddWavelength(DeviceHandle, 0, wavelength)
            wavelengthList = OphirCOM.GetWavelengths(DeviceHandle, 0)
            #print(wavelengthList)
            OphirCOM.SetWavelength(DeviceHandle, 0, len(wavelengthList[1])-1)
            #print(wavelengthList[1][len(wavelengthList[1])-1])
            OphirCOM.SetRange(DeviceHandle, 0, 0)

            # start measuring
            OphirCOM.StartStream(DeviceHandle, 0)

            # Without this delay the first values are lower than the rest or lead to no counting 
            time.sleep(5)
            
            # set starttime and measurement duration       
            start = datetime.now()
            average_until = start 
            average_count = 0
            measure_until = start + timedelta(seconds=duration)
            average_until = start + timedelta(seconds=avgTime)
            average_start = average_until - timedelta(seconds=float(integration))
            while datetime.now() < measure_until:
                if datetime.now() >= average_start:
                    average_count = 0
                    total_power = 0
                    start_average = datetime.now()
                    #print('start_average = {0}, average_until = {1}\n'.format(start_average,average_until))
                    while (datetime.now() < average_until):
                        data = OphirCOM.GetData(DeviceHandle, 0)
                        #time.sleep(0.2)  # wait a little for data
                        if len(data[0]) > 0:  # if any data available, print the first one from the batch
                            #print('Reading = {0}, TimeStamp = {1}, Status = {2}, Count = {3}'.format(data[0][0], data[1][0], data[2][0], average_count+1))
                            total_power += (data[0][0])
                            average_count += 1

                    # calculate arithmetic mean of power and temperature
                    if average_count > 0:
                        total_power /= average_count
                        #ts = (start_average - start).total_seconds()

                        print('\n' + start_average.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3], int(wavelength), power_level, total_power, average_count,  
                              end='', sep='\t')
                        if fout:
                            print('\n' + start_average.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3], int(wavelength), power_level,
                                  total_power, end='', sep='\t', file=fout)
                    else:
                        print('\naverage_count = 0')
                    average_until += timedelta(seconds=avgTime)
                    average_start = average_until - timedelta(seconds=float(integration))
            # close the file
            if fout:
                fout.close()
        else:
            print('Sensor is not connected to Ophir Juno!')

    else:
        tlPM = TLPMX()
        deviceCount = c_uint32()
        try:
            tlPM.findRsrc(byref(deviceCount))
            Thorlabs = True
        except NameError as err:
            print("Error")
            Thorlabs = False
        if Thorlabs:

            # Connect to Thorlabs power meter
            resourceName = create_string_buffer(1024);
            tlPM.getRsrcName(c_int(0), resourceName);
            # print(c_char_p(resourceName.raw).value);
            tlPM.open(resourceName, c_bool(True), c_bool(True));

            # Check which Thorlabs power meter is connected
            index = c_uint32(0)
            modelName = create_string_buffer(1024)
            serialNumber = create_string_buffer(1024)
            manufacturer = create_string_buffer(1024)
            deviceAvailable = c_int16()
            tlPM.getRsrcInfo(index, modelName, serialNumber, manufacturer, deviceAvailable)
            print(manufacturer.value.decode('utf-8').title() + ' ' + modelName.value.decode('utf-8') + ' optical power meter connected!')

            # Set variable
            name = create_string_buffer(1024)
            snr = create_string_buffer(1024)
            message = create_string_buffer(1024)
            pType = c_int16()
            pStype = c_int16()
            pFlags = c_int16()
            channel = c_uint16(1);

            # Check to which channel the sensor is connected
            try:
                tlPM.getSensorInfo(name, snr, message, byref(pType), byref(pStype), byref(pFlags), channel)
                channel1 = True;
                print("Found sensor connected to channel 1!")
            except NameError as err:
                print("No sensor connected to channel 1!")
                channel = c_uint16(2);
                try:
                    tlPM.getSensorInfo(name, snr, message, byref(pType), byref(pStype), byref(pFlags), channel)
                    print("Found sensor connect to channel 2!")
                except NameError as err:
                    print("No sensor connected to channel 2!")
            # print(name, snr, message, pType, pStype, pFlags, channel)
            # print(name.value, snr.value, message.value, pType.value, pStype.value, pFlags.value,channel.value)

            # Set the wavelength
            tlPM.setWavelength(c_double(float(wavelength)), channel);
            time.sleep(0.1);  # Without this delay the first number is consistently higher than the rest

            # check if file is empty, if not print headline
            if fout and os.stat(sys.argv[3]).st_size == 0:

                # check if temperature sensor is connected
                if thermometer:
                    print("timestamp", "wavelength", "setting", "power", "temperature", end='', sep='\t')
                    print("timestamp", "wavelength", "setting", "power", "temperature", end='', sep='\t', file=fout)
                    print("\nYYYY-MM-DD HH:MM:SS", "nm", "s", "W", "C", end='', sep='\t')
                    print("\nYYYY-MM-DD HH:MM:SS", "nm", "s", "W", "C", end='', sep='\t', file=fout)
                else:
                    print("timestamp", "wavelength", "setting", "power", end='', sep='\t')
                    print("timestamp", "wavelength", "setting", "power", end='', sep='\t', file=fout)
                    print("\nYYYY-MM-DD HH:MM:SS", "nm", "s", "W", end='', sep='\t')
                    print("\nYYYY-MM-DD HH:MM:SS", "nm", "s", "W", end='', sep='\t', file=fout)

            # Without this delay the first number is consistently higher than the rest
            time.sleep(2)

            # Set variables needed for measurement
            power = c_double();
            temperature = c_double();

            # set starttime and measurement duration
            start = datetime.now();
            measure_until = start + timedelta(seconds=float(duration))
            average_until = start + timedelta(seconds=float(avgTime))
            average_until = start + timedelta(seconds=float(avgTime))
            average_start = average_until - timedelta(seconds=float(integration))
            while datetime.now() <= measure_until:
                # print("\n" + str(datetime.now()) + " > " + str(average_start) + " < " + str(average_until) + "\n")
                if datetime.now() >= average_start:
                    average_count = 0;
                    total_power = 0;
                    total_temperature = 0;

                    start_average = datetime.now()
                    while (datetime.now() < average_until):
                        tlPM.measPower(byref(power), channel);
                        total_power += power.value;
                        # print('Reading = {0}, Timestamp = {1}, Count = {2}'.format(power.value, str(datetime.now()), average_count+1))
                        if thermometer:
                            tlPM.measExtNtcTemperature(byref(temperature), channel);
                            total_temperature += temperature.value;
                        average_count += 1;

                    # calculate arithmetic mean of power and temperature if applicable
                    total_power /= average_count;
                    if thermometer:
                        total_temperature /= average_count;
                    ts = (start_average - start).total_seconds();

                    # write date into output file
                    if thermometer:
                        print('\n' + start_average.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3], int(wavelength), power_level,
                              total_power, total_temperature, end='', sep='\t')
                        if fout:
                            print('\n' + start_average.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3], int(wavelength),
                                  power_level,
                                  total_power, total_temperature, end='', sep='\t', file=fout)
                    else:
                        print('\n' + start_average.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3], int(wavelength), power_level,
                              total_power, end='', sep='\t')
                        if fout:
                            print('\n' + start_average.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3], int(wavelength),
                                  power_level,
                                  total_power, end='', sep='\t', file=fout)
                    average_until += timedelta(seconds=float(avgTime));
                    average_start = average_until - timedelta(seconds=float(integration))
            tlPM.close()
            tlPM = None

        else:
            print('No Ophir or Thorlabs powermeter connected')
except OSError as err:
    print("OS error: {0}".format(err))
except:
    traceback.print_exc()

# Stop & Close all devices
OphirCOM.StopAllStreams()
OphirCOM.CloseAll()

# Release the object
OphirCOM = None

