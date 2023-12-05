This folder is defined in measurementConfig.csv, which will be available in the setup folder. Please follow the instructions provided in it to create the configurations folder and proceed as stated below.

1. Make your own configurations at the microscope, 

2. Use only configurations created at the same system. Even very similar systems might cause compatibility issues.

3. Name them uniformly and meaningfully: e.g. LPM488.czexp

	3.0 Detector windows must not overlap with laser lines
	3.2 Zoom in, use bidirectional scanning
	3.1 "LPM" will be the prefix to parse the useful configurations
	3.2 "488" will be read from the file name and used later to configure the power meter
	3.3 If "LPM488.czexp" uses the 488nm laser, the measurement will correctly

4. Export the configurations into the configuration folder. In this repository the example is "C:\QUAREP\Config\"
