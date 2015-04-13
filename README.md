lazyloader
=========
A Python 3 script to download bars, turn them into autoloaders and then load them.

## Requirements
### Operation
Requires [7za.exe](http://www.7-zip.org/download.html) (32-bit and 64-bit) and [cap.exe](https://drive.bitcasa.com/send/Lrb0VC6NsOEX5BNSDmGVn2mkeiSDklghCXlYuQk_YkRE) in the same folder as the script. 32-bit 7za.exe should be included as 7za.exe and 64-bit 7za.exe should be included as 7za64.exe, since the script reads the OS bit setup and uses the 64/32 bit 7-Zip executable accordingly. Because 32-bit Windows is just as annoyingly persistent as Windows XP.

If you're using just the .py file, make sure to have Python =>3.4.2 in your PATH and the support executables in the local folder. Or, if you're using the release .exe, extract everything into any one folder (all .exes, .pyds and .dlls).

### Redistribution
Those listed in Operation, plus (preferably) conversion to executable formats via [cx_freeze](http://cx-freeze.readthedocs.org/en/latest/index.html).

## What It Does
1. Ask for OS/radio/software versions, device type
2. Download the right OS/radio bar based on above input
3. Extract bars
4. Create autoloader
5. Ask to load autoloader

## Command Line Arguments
### Help

	> lazyloader -h
	
	usage: lazyloader.exe OSVERSION RADIOVERSION SWVERSION DEVICE
	
	Create one autoloader for personal use.
	
	positional arguments:
		os          OS version, 10.x.y.zzzz
		radio       Radio version, 10.x.y.zzzz
		swrelease   Software version, 10.x.y.zzzz
		device      0=STL100-1 1=STL100-2/3/P9983 2=STL100-4 3=Q10/Q5/P9983
	              4=Z30/CLASSIC/LEAP 5=Z3 6=PASSPORT
	
	optional arguments:
		-h, --help  show this help message and exit
		--run-loader  Run autoloader after creation
	
### Example

		> lazyloader 10.3.1.2726 10.3.1.2727 10.3.1.1877 6
	would make an autoloader for OS 10.3.1.2726/radio 10.3.1.2727 (software release 10.3.1.1877) for Passport (device 6).
	
## License
No fancy licensing here, just fork this and do whatever.
Although, if you figure out something interesting, please do try to put it upstream via pull request.

## Authors
* Thurask [(@thuraski)](http://www.twitter.com/thuraski)
* Viewers Like You
