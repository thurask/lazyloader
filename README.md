lazyloader
=========

# HEY, READ THIS!

**This has been superseded. Please go [here](https://github.com/thurask/bbarchivist)**.

A Python 3 script to download bars, turn them into autoloaders and then load them.

Loading autoloaders is Windows-only (obviously), but the rest can be performed on Mac/Linux.

## Requirements
### Operation
Requires [cap.exe](https://drive.bitcasa.com/send/Lrb0VC6NsOEX5BNSDmGVn2mkeiSDklghCXlYuQk_YkRE) in the same folder as the script.

If you're using this as a .py file, it requires Python =>3.4.2. It also requires the [requests](http://docs.python-requests.org/en/latest/user/install/) library installed somehow.
To install requests really easily, using pip:
	
	> pip install -r \path\to\requirements.txt
	
To use [pip-win](https://sites.google.com/site/pydatalog/python/pip-for-windows), just put that (corrected, of course) into pip-win's Command field and hit Run. It'll automatically download whichever pypi packages are dependencies of this one.
If you downloaded the requirements.txt file in this repository, of course.

Or, if you're using the release .exe, extract everything into any one folder (all .exes, .pyds and .dlls).

## What It Does
1. Ask for OS/radio/software versions, device type (if not specified)
2. Download the right OS/radio bar based on above input/specification
3. Extract bars
4. Create autoloader
5. Ask to load autoloader (Windows only)

## Command Line Arguments
### Help

	> lazyloader -h
	
	usage: lazyloader.exe [-h] [-v]
                      (--stl100-1 | --stl100-x | --stl100-4 | --q10 | --z30 | --z3 | --passport)
                      [--run-loader]
                      os radio swrelease

	Create one autoloader for personal use.
	
	positional arguments:
	  os             OS version, 10.x.y.zzzz
	  radio          Radio version, 10.x.y.zzzz
	  swrelease      Software version, 10.x.y.zzzz
	
	optional arguments:
	  -h, --help     show this help message and exit
	  -v, --version  show program's version number and exit
	  --run-loader   Run autoloader after creation
	
	devices:
	  Device to load (one required)
	
	  --stl100-1     STL100-1
	  --stl100-x     STL100-2/3, P'9982
	  --stl100-4     STL100-4
	  --q10          Q10, Q5, P'9983
	  --z30          Z30, Classic, Leap
	  --z3           Z3
	  --passport     Passport
	
	http://github.com/thurask/lazyloader

	
### Example

		> lazyloader 10.3.1.2726 10.3.1.2727 10.3.1.1877 --passport
	would make an autoloader for OS 10.3.1.2726/radio 10.3.1.2727 (software release 10.3.1.1877) for Passport (device 6).
	
## License
No fancy licensing here, just fork this and do whatever.
Although, if you figure out something interesting, please do try to put it upstream via pull request.

## Authors
* Thurask [(@thuraski)](http://www.twitter.com/thuraski)
* Viewers Like You
