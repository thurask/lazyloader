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
