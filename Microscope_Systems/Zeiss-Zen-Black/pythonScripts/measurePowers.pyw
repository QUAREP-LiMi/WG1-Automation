from ctypes import cdll, c_long, c_ulong, c_uint32, byref, create_string_buffer, c_bool, c_char_p, c_int, c_int16, \
    c_double, sizeof, c_voidp
from datetime import datetime, timedelta
from TLPM import TLPM
import time
import sys
import os

#import win32gui
import win32com.client
import traceback

print('Argument List: ', str(sys.argv))

# first argument is the wavelength
if len(sys.argv) > 1:
    # print(sys.argv[1])
    wavelength = float(sys.argv[1])

# second argument is the power level
if len(sys.argv) > 2:
    # print(sys.argv[2])
    power_level = int(sys.argv[2])

# third argument is the output file
fout = 0
if len(sys.argv) > 3:
    # print(os.stat(sys.argv[3]).st_size)
    fout = open(sys.argv[3], "a")

# fourth argument is the duration and fifth argument is the measurement interval
duration = 5 * 60  # in seconds, default
if len(sys.argv) > 4:
    # print(sys.argv[4])
    duration = int(sys.argv[4])
if len(sys.argv) > 5:
    # print(sys.argv[5])
    avgTime = int(sys.argv[5])

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

            # Without this delay the first number is consistently higher than the rest
            time.sleep(1.5)

            # set starttime and measurement duration
            start = datetime.now()
            measure_until = start + timedelta(seconds=duration)
            average_until = start
            while datetime.now() < measure_until:
                average_until += timedelta(seconds=avgTime)
                average_count = 0
                total_power = 0
                start_average = datetime.now()

                while (datetime.now() < average_until):
                    data = OphirCOM.GetData(DeviceHandle, 0)
                    time.sleep(0.2)  # wait a little for data
                    if len(data[0]) > 0:  # if any data available, print the first one from the batch
                        # print('Reading = {0}, TimeStamp = {1}, Status = {2}'.format(data[0][0], data[1][0], data[2][0]))
                        total_power += (data[0][0])
                    average_count += 1

                # calculate arithmetic mean of power and temperature
                total_power /= average_count
                ts = (start_average - start).total_seconds()

                print('\n' + start_average.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3], int(wavelength), power_level, total_power,
                      end='', sep='\t')
                if fout:
                    print('\n' + start_average.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3], int(wavelength), power_level,
                          total_power, end='', sep='\t', file=fout)

            # close the file
            if fout:
                print('Output file closed!')
                fout.close()

            # Stop & Close all devices
            OphirCOM.StopAllStreams()
            OphirCOM.CloseAll()

            # Release the object
            OphirCOM = None
            print('Ophir power meter disconnected!')
        else:
            print('Sensor is not connected to Ophir Juno!')

            # Release the object
            OphirCOM = None
    else:
        tlPM = TLPM()
        deviceCount = c_uint32()
        try:
            tlPM.findRsrc(byref(deviceCount))
            print('Thorlabs power meter connected!')
            Thorlabs = True
        except NameError as err:
            Thorlabs = False
        if Thorlabs:
            resourceName = create_string_buffer(1024)
            tlPM.getRsrcName(c_int(0), resourceName)
            # print(c_char_p(resourceName.raw).value)
            tlPM.open(resourceName, c_bool(True), c_bool(True))
            thermometer = False;
            tlPM.setWavelength(c_double(float(wavelength)));
            time.sleep(0.1);  # Without this delay the first number is consistently higher than the rest

            # check if temperature sensor is connected
            temperature = c_double();
            try:
                tlPM.measExtNtcTemperature(byref(temperature));
                thermometer = True;
            except NameError as err:
                print("Temperature sensor not connected! ");
                thermometer = False;
                #print(err.args);

            # check if file is empty, if not print headline
            if fout and os.stat(sys.argv[3]).st_size == 0:
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

            time.sleep(1.5)  # Without this delay the first number is consistently higher than the rest

            # set starttime and measurement duration
            start = datetime.now();
            measure_until = start + timedelta(seconds=float(duration))
            average_until = start
            while datetime.now() <= measure_until:
                average_until += timedelta(seconds=float(avgTime));
                average_count = 0;
                total_power = 0;
                total_temperature = 0;

                start_average = datetime.now()
                while (datetime.now() < average_until):
                    power = c_double();
                    try:
                        tlPM.measPower(byref(power));
                    except NameError as err:
                        tlPM.measPower(byref(power));
                    total_power += power.value;
                    if thermometer:
                        tlPM.measExtNtcTemperature(byref(temperature));
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
                        print('\n' + start_average.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3], int(wavelength), power_level,
                              total_power, total_temperature, end='', sep='\t', file=fout)
                else:
                    print('\n' + start_average.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3], int(wavelength), power_level,
                          total_power, end='', sep='\t')
                    if fout:
                        print('\n' + start_average.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3], int(wavelength), power_level,
                              total_power, end='', sep='\t', file=fout)
            if fout:
                print('\nOutput file closed!')
                fout.close
            print('Thorlabs power meter disconnected!')
            tlPM.reset()
            tlPM.close()
            tlPM = None
        else:
            print('No Ophir or Thorlabs power meter connected!')
except OSError as err:
    print("OS error: {0}".format(err))
except:
    traceback.print_exc()



