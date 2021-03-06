import os
import glob
import shutil
import platform
import hashlib
import requests
from requests.packages import urllib3
import time
import queue
import threading
import binascii
import math
import sys
import argparse
import webbrowser
import subprocess
import zipfile

_version = "2015-04-14-A"
_release = "https://github.com/thurask/archivist/releases/latest"

def ghettoConvert(intsize):
	hexsize = format(intsize, '08x')  # '00AABBCC'
	newlist = [hexsize[i:i + 2] for i in range(0, len(hexsize), 2)]  # ['00', 'AA','BB','CC']
	while "00" in newlist:
		newlist.remove("00")  # extra padding
	newlist.reverse()
	ghettoHex = "".join(newlist)  # 'CCBBAA'
	ghettoHex = ghettoHex.rjust(16, '0')
	return binascii.unhexlify(bytes(ghettoHex.upper(), 'ascii'))

def makeOffset(cap, firstfile, secondfile="", thirdfile="", fourthfile="", fifthfile="", sixthfile="", folder=os.getcwd()):
	filecount = 0
	filelist = [firstfile, secondfile, thirdfile, fourthfile, fifthfile, sixthfile]
	for i in filelist:
		if i:
			filecount += 1
	# immutable things
	separator = binascii.unhexlify("6ADF5D144E4B4D4E474F46464D4E532B170A0D1E0C14532B372A2D3E2C34522F3C534F514F514F514F534E464D514E4947514E51474F70709CD5C5979CD5C5979CD5C597") #3.11.0.18
	password = binascii.unhexlify("0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000")
	singlepad = binascii.unhexlify("00")
	doublepad = binascii.unhexlify("0000")
	signedpad = binascii.unhexlify("0000000000000000")
	filepad = binascii.unhexlify(bytes(str(filecount).rjust(2, '0'), 'ascii'))  # between 01 and 06
	trailermax = int(7 - int(filecount))
	trailermax = trailermax * 2
	trailer = "0" * trailermax  # 00 repeated between 1 and 6 times
	trailers = binascii.unhexlify(trailer)
		
	capfile = str(glob.glob(cap)[0])
	capsize = os.path.getsize(capfile)  # size of cap.exe, in bytes
	
	first = str(glob.glob(firstfile)[0])
	firstsize = os.path.getsize(first)  # required
	if (filecount >= 2):
		second = str(glob.glob(secondfile)[0])
		secondsize = os.path.getsize(second)
	if (filecount >= 3):
		third = str(glob.glob(thirdfile)[0])
		thirdsize = os.path.getsize(third)
	if (filecount >= 4):
		fourth = str(glob.glob(fourthfile)[0])
		fourthsize = os.path.getsize(fourth)
	if (filecount >= 5):
		fifth = str(glob.glob(fifthfile)[0])
		fifthsize = os.path.getsize(fifth)
		
	
	firstoffset = len(separator) + len(password) + 64 + capsize  # start of first file; length of cap + length of offset
	firststart = ghettoConvert(firstoffset)
	if (filecount >= 2):
		secondoffset = firstoffset + firstsize  # start of second file
		secondstart = ghettoConvert(secondoffset)
	if (filecount >= 3):
		thirdoffset = secondstart + secondsize  # start of third file
		thirdstart = ghettoConvert(thirdoffset)
	if (filecount >= 4):
		fourthoffset = thirdoffset + thirdsize  # start of fourth file
		fourthstart = ghettoConvert(fourthoffset)
	if (filecount >= 5):
		fifthoffset = fourthstart + fourthsize  # start of fifth file
		fifthstart = ghettoConvert(fifthoffset)
	if (filecount == 6):
		sixthoffset = fifthoffset + fifthsize  # start of sixth file
		sixthstart = ghettoConvert(sixthoffset)
		
	with open(os.path.join(folder, "offset.hex"), "w+b") as file:
		file.write(separator)
		file.write(password)
		file.write(filepad)
		file.write(doublepad)
		file.write(firststart)
		file.write(singlepad)
		if (filecount >= 2):
			file.write(secondstart)
		else:
			file.write(signedpad)
		file.write(singlepad)
		if (filecount >= 3):
			file.write(thirdstart)
		else:
			file.write(signedpad)
		file.write(singlepad)
		if (filecount >= 4):
			file.write(fourthstart)
		else:
			file.write(signedpad)
		file.write(singlepad)
		if (filecount >= 5):
			file.write(fifthstart)
		else:
			file.write(signedpad)
		file.write(singlepad)
		if (filecount == 6):
			file.write(sixthstart)
		else:
			file.write(signedpad)
		file.write(singlepad)
		file.write(doublepad)
		file.write(trailers)
		
def makeAutoloader(filename, cap, firstfile, secondfile="", thirdfile="", fourthfile="", fifthfile="", sixthfile="", folder=os.getcwd()):
	makeOffset(cap, firstfile, secondfile, thirdfile, fourthfile, fifthfile, sixthfile, folder)
	
	filecount = 0
	filelist = [firstfile, secondfile, thirdfile, fourthfile, fifthfile, sixthfile]
	for i in filelist:
		if i:
			filecount += 1
	try:
		with open(os.path.join(os.path.abspath(folder), filename), "wb") as autoloader:
			try:
				with open(os.path.normpath(cap), "rb") as capfile:
					print("WRITING CAP.EXE...")
					while True:
						chunk = capfile.read(4096)  # 4k chunks
						if not chunk:
							break
						autoloader.write(chunk)
			except IOError as e:
				print("Operation failed:", e.strerror)
			try:
				with open(os.path.join(folder, "offset.hex"), "rb") as offset:
					print("WRITING MAGIC OFFSET...")
					autoloader.write(offset.read())
			except IOError as e:
				print("Operation failed:", e.strerror)
			try:
				with open(firstfile, "rb") as first:
					print("WRITING SIGNED FILE #1...\n", firstfile)
					while True:
						chunk = first.read(4096)  # 4k chunks
						if not chunk:
							break
						autoloader.write(chunk)
			except IOError as e:
				print("Operation failed:", e.strerror)
			if (filecount >= 2):
				try:
					print("WRITING SIGNED FILE #2...\n", secondfile)
					with open(secondfile, "rb") as second:
						while True:
							chunk = second.read(4096)  # 4k chunks
							if not chunk:
								break
							autoloader.write(chunk)
				except IOError as e:
					print("Operation failed:", e.strerror)
			if (filecount >= 3):
				try:
					print("WRITING SIGNED FILE #3...\n", thirdfile)
					with open(thirdfile, "rb") as third:
						while True:
							chunk = third.read(4096)  # 4k chunks
							if not chunk:
								break
							autoloader.write(chunk)
				except IOError as e:
					print("Operation failed:", e.strerror)
			if (filecount >= 4):
				try:
					print("WRITING SIGNED FILE #5...\n", fourthfile)
					with open(fourthfile, "rb") as fourth:
						while True:
							chunk = fourth.read(4096)  # 4k chunks
							if not chunk:
								break
							autoloader.write(chunk)
				except IOError as e:
					print("Operation failed:", e.strerror)
			if (filecount >= 5):
				try:
					print("WRITING SIGNED FILE #5...\n", fifthfile)
					with open(fifthfile, "rb") as fifth:
						while True:
							chunk = fifth.read(4096)  # 4k chunks
							if not chunk:
								break
							autoloader.write(chunk)
				except IOError as e:
					print("Operation failed:", e.strerror)
			if (filecount == 6):
				try:
					print("WRITING SIGNED FILE #6...\n", sixthfile)
					with open(sixthfile, "rb") as sixth:
						while True:
							chunk = sixth.read(4096)  # 4k chunks
							if not chunk:
								break
							autoloader.write(chunk)
				except IOError as e:
					print("Operation failed:", e.strerror)
	except IOError as e:
		print("Operation failed:", e.strerror)
		
	print(filename, "FINISHED!\n")
	os.remove(os.path.join(folder, "offset.hex"))

def deviceRange(argument):
	device = int(argument)
	if device < 0 or device > 6:
		raise argparse.ArgumentTypeError("%s is an invalid device" % device)
	return device

def updateCheck(version):
	update = False
	updatesite = "https://raw.githubusercontent.com/thurask/thurask.github.io/master/lazyloader.version"
	print("LOCAL VERSION:", version)
	urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  #silence warnings about no SSL
	get = requests.get(updatesite, verify=False)  # don't use SSL until I figure it out
	remote = str(get.text).strip()
	print("REMOTE VERSION:", remote)
	if (get.status_code != 404):
		if version != remote:
				update = True
		else:
			update = False
	return update

#http://pipe-devnull.com/2012/09/13/queued-threaded-http-downloader-in-python.html
#Modified to work with Python 3:
#Downloader class - reads queue and downloads each file in succession
class Downloader(threading.Thread):
	def __init__(self, queue, output_directory):
		threading.Thread.__init__(self,name= binascii.hexlify(os.urandom(8)))
		self.queue = queue
		self.output_directory = output_directory
	def run(self):
		while True:
			# gets the url from the queue
			url = self.queue.get()
			# download the file
			self.download(url)
			# send a signal to the queue that the job is done
			self.queue.task_done()
	def download(self, url):
		t_start = time.clock()
		local_filename = url.split('/')[-1]
		print("Downloading:", local_filename)
		r = requests.get(url, stream=True)
		if (r.status_code != 404): #200 OK
			fname = self.output_directory + "/" + os.path.basename(url)
			with open(fname, "wb") as f:
				for chunk in r.iter_content(chunk_size=1024): 
					if chunk: # filter out keep-alive new chunks
						f.write(chunk)
						f.flush()
			t_elapsed = time.clock() - t_start
			t_elapsed_proper = math.ceil(t_elapsed*100)/100
			print("Downloaded " + url + " in " + str(t_elapsed_proper) + " seconds")
			f.close()
		else:
			print("* Thread: " + self.name + " Bad URL: " + url)
			return

# Spawns dowloader threads and manages URL downloads queue
class DownloadManager():
	def __init__(self, download_dict, output_directory, thread_count=5):
		self.thread_count = thread_count
		self.download_dict = download_dict
		self.output_directory = output_directory
	# Start the downloader threads, fill the queue with the URLs and
	# then feed the threads URLs via the queue
	def begin_downloads(self):
		dlqueue = queue.Queue()
		# Create i thread pool and give them a queue
		for t in range(self.thread_count):
			t = Downloader(dlqueue, self.output_directory)
			t.setDaemon(True)
			t.start()
		# Load the queue from the download dict
		for linkname in self.download_dict:
			# print uri
			dlqueue.put(self.download_dict[linkname])

		# Wait for the queue to finish
		dlqueue.join()
		return

# Handle bools
def str2bool(v):
	return str(v).lower() in ("yes", "true", "t", "1", "y")
	
# Get OS type
def isWindows():
	windows = platform.system() == "Windows"
	return windows

# Extract bars with 7z
def extractBar(filepath):
	for file in os.listdir(filepath):
		if file.endswith(".bar"):
			try:
				z = zipfile.ZipFile(file, 'r')
				names = z.namelist()
				for name in names:
					if str(name).endswith(".signed"):
						z.extract(name, filepath)
			except Exception:
				print("EXTRACTION FAILURE")
				print("DID IT DOWNLOAD PROPERLY?")
				return
			
# Check if URL has HTTP 200 or HTTP 300-308 status code			 
def availability(url):
	try:
		av = requests.head(str(url))
	except requests.ConnectionError:
		return False
	else:
		status = int(av.status_code)
		if (status == 200) or (300 < status <= 308):
			return True
		else:
			return False

def doMagic(osversion, radioversion, softwareversion, device, localdir, autoloader):
	version = _version
	release = _release
	devicelist = ["STL100-1", "STL100-2/3/P9982", "STL100-4", "Q10/Q5/P9983", "Z30/CLASSIC/LEAP", "Z3", "PASSPORT"]
	print("~~~LAZYLOADER VERSION", version + "~~~")
	print("OS VERSION:", osversion)
	print("RADIO VERSION:", radioversion)
	print("SOFTWARE VERSION:", softwareversion)
	print("DEVICE:", devicelist[device])
	
	print("\nCHECKING FOR UPDATES...")
	update = updateCheck(version)
	if update == True:
		print("UPDATE AVAILABLE!")
		invoke = str2bool(input("DOWNLOAD UPDATE? Y/N: "))
		if invoke == True:
			webbrowser.open(release)
			print("CLOSING...")
			raise SystemExit  # bye
		else:
			pass
	else:
		print("NO UPDATE AVAILABLE...")
	
	# hash SW release
	sha1 = hashlib.sha1(softwareversion.encode('utf-8'))
	hashedsoftwareversion = sha1.hexdigest()
	
	baseurl = "http://cdn.fs.sl.blackberry.com/fs/qnx/production/" + hashedsoftwareversion
	
	if device == 0:
		osurl = baseurl + "/winchester.factory_sfi.desktop-" + osversion + "-nto+armle-v7+signed.bar"
		radiourl = baseurl + "/m5730-" + radioversion + "-nto+armle-v7+signed.bar"
	elif device == 1:
		osurl = baseurl + "/qc8960.factory_sfi.desktop-" + osversion + "-nto+armle-v7+signed.bar"
		radiourl = baseurl + "/qc8960-" + radioversion + "-nto+armle-v7+signed.bar"
	elif device == 2:
		osurl = baseurl + "/qc8960.factory_sfi.desktop-" + osversion + "-nto+armle-v7+signed.bar"
		radiourl = baseurl + "/qc8960.omadm-" + radioversion + "-nto+armle-v7+signed.bar"
	elif device == 3:
		osurl = baseurl + "/qc8960.factory_sfi.desktop-" + osversion + "-nto+armle-v7+signed.bar"
		radiourl = baseurl + "/qc8960.wtr-" + radioversion + "-nto+armle-v7+signed.bar"
	elif device == 4:
		osurl = baseurl + "/qc8960.factory_sfi.desktop-" + osversion + "-nto+armle-v7+signed.bar"
		radiourl = baseurl + "/qc8960.wtr5-" + radioversion + "-nto+armle-v7+signed.bar"
	elif device == 5:
		osurl = baseurl + "/qc8960.factory_sfi_hybrid_qc8x30.desktop-" + osversion + "-nto+armle-v7+signed.bar"
		radiourl = baseurl + "/qc8930.wtr5-" + radioversion + "-nto+armle-v7+signed.bar"
	elif device == 6:
		osurl = baseurl + "/qc8960.factory_sfi_hybrid_qc8974.desktop-" + osversion + "-nto+armle-v7+signed.bar"
		radiourl = baseurl + "/qc8974.wtr2-" + radioversion + "-nto+armle-v7+signed.bar"
	else:
		return
	
	# Check availability of software release
	av = availability(baseurl)
	if(av == True):
		print("\nSOFTWARE RELEASE", softwareversion, "EXISTS")
	else:
		print("\nSOFTWARE RELEASE", softwareversion, "NOT FOUND")
		cont = str2bool(input("CONTINUE? Y/N "))
		if (cont == True):
			pass
		else:
			print("\nEXITING...")
			raise SystemExit  # bye bye

	print("\nDOWNLOADING...")
	dldict = dict(osurl=osurl, radiourl=radiourl)
	download_manager = DownloadManager(dldict, localdir, 3)
	download_manager.begin_downloads()
	
	print("\nEXTRACTING...")
	extractBar(localdir)

	# Make dirs
	if not os.path.exists(os.path.join(localdir, 'bars')):
		os.mkdir(os.path.join(localdir, 'bars'))
	bardir = os.path.join(localdir, 'bars')
	if not os.path.exists(os.path.join(bardir, osversion)):
		os.mkdir(os.path.join(bardir, osversion))
	bardir_os = os.path.join(bardir, osversion)
	if not os.path.exists(os.path.join(bardir, radioversion)):
		os.mkdir(os.path.join(bardir, radioversion))
	bardir_radio = os.path.join(bardir, radioversion)

	if not os.path.exists(os.path.join(localdir, 'loaders')):
		os.mkdir(os.path.join(localdir, 'loaders'))
	loaderdir = os.path.join(localdir, 'loaders')
	if not os.path.exists(os.path.join(loaderdir, osversion)):
		os.mkdir(os.path.join(loaderdir, osversion))
	loaderdir_os = os.path.join(loaderdir, osversion)
	
	print("\nMOVING .bar FILES...")
	for files in os.listdir(localdir):
		if files.endswith(".bar"):
			print("MOVING: " + files)
			bardest_os = os.path.join(bardir_os, files)
			bardest_radio = os.path.join(bardir_radio, files)
			if os.path.getsize(files) > 90000000:  # even the fattest radio is less than 90MB
				try:
					shutil.move(files, bardir_os)
				except shutil.Error:
					os.remove(bardest_os)
			else:
				try:
					shutil.move(files, bardir_radio)
				except shutil.Error:
					os.remove(bardest_radio)
					
	cap="cap.exe"
	
	print("\nCREATING LOADER...")
	if device == 0:
		try:
			os_ti = str(glob.glob("*winchester*.signed")[0])
		except IndexError:
			print("No OMAP image found")
			return
		try:
			radio_z10_ti = str(glob.glob("*radio.m5730*.signed")[0])
		except IndexError:
			print("No OMAP radio found")
			return
		else:
			print("Creating OMAP Z10 OS...")
			try:
				makeAutoloader(filename="Z10_" + osversion + "_STL100-1.exe", cap=cap, firstfile=os_ti, secondfile=radio_z10_ti, thirdfile="", fourthfile="", fifthfile="", sixthfile="", folder=localdir)
			except Exception:
				print("Could not create STL100-1 OS/radio loader")
				return
	elif device == 1:
		try:
			os_8960 = str(glob.glob("*qc8960*_sfi.desktop*.signed")[0])
		except IndexError:
			print("No 8960 image found")
			return
		try:
			radio_z10_qcm = str(glob.glob("*radio.qc8960.BB*.signed")[0])
		except IndexError:
			print("No 8960 radio found")
			return
		else:
			print("Creating Qualcomm Z10 OS...")
			try:
				makeAutoloader("Z10_" + osversion + "_STL100-2-3.exe", cap, os_8960, radio_z10_qcm, folder=localdir)
			except Exception:
				print("Could not create Qualcomm Z10 OS/radio loader")
				return
	elif device == 2:
		try:
			os_8960 = str(glob.glob("*qc8960*_sfi.desktop*.signed")[0])
		except IndexError:
			print("No 8960 image found")
			return
		try:
			radio_z10_vzw = str(glob.glob("*radio.qc8960*omadm*.signed")[0])
		except IndexError:
			print("No Verizon 8960 radio found")
			return
		else:
			print("Creating Verizon Z10 OS...")
			try:
				makeAutoloader("Z10_" + osversion + "_STL100-4.exe", cap, os_8960, radio_z10_vzw, folder=localdir)
			except Exception:
				print("Could not create Verizon Z10 OS/radio loader")
				return
	elif device == 3:
		try:
			os_8960 = str(glob.glob("*qc8960*_sfi.desktop*.signed")[0])
		except IndexError:
			print("No 8960 image found")
			return
		try:
			radio_q10 = str(glob.glob("*8960*wtr.*.signed")[0])
		except IndexError:
			print("No Q10/Q5 radio found")
			return
		else:
			print("Creating Q10/Q5 OS...")
			try:
				makeAutoloader("Q10_" + osversion + "_SQN100-1-2-3-4-5.exe", cap, os_8960, radio_q10, folder=localdir)
			except Exception:
				print("Could not create Q10/Q5 OS/radio loader")
				return
	elif device == 4:
		try:
			os_8960 = str(glob.glob("*qc8960*_sfi.desktop*.signed")[0])
		except IndexError:
			print("No 8960 image found")
			return
		try:
			radio_z30 = str(glob.glob("*8960*wtr5*.signed")[0])
		except IndexError:
			print("No Z30/Classic radio found")
			return
		else:
			print("Creating Z30/Classic OS...")
			try:
				makeAutoloader("Z30_" + osversion + "_STA100-1-2-3-4-5-6.exe", cap, os_8960, radio_z30, folder=localdir)
			except Exception:
				print("Could not create Z30/Classic OS/radio loader")
				return
	elif device == 5:
		try:
			os_8x30 = str(glob.glob("*qc8x30*desktop*.signed")[0])
		except IndexError:
			print("No 8x30 image found")
			return
		try:
			radio_z3 = str(glob.glob("*8930*wtr5*.signed")[0])
		except IndexError:
			print("No Z3 radio found")
			return
		else:
			print("Creating Z3 OS...")
			try:
				makeAutoloader("Z3_" + osversion + "_STJ100-1-2.exe", cap, os_8x30, radio_z3, folder=localdir)
			except Exception:
				print("Could not create Z3 OS/radio loader")
				return
	elif device == 6:
		try:
			os_8974 = str(glob.glob("*qc8974*desktop*.signed")[0])
		except IndexError:
			print("No 8974 image found")
			return
		try:
			radio_8974 = str(glob.glob("*8974*wtr2*.signed")[0])
		except IndexError:
			print("No Passport radio found")
			return
		else:
			print("Creating Passport OS...")
			try:
				makeAutoloader("Passport_" + osversion + "_SQW100-1-2-3.exe", cap, os_8974, radio_8974, folder=localdir)
			except Exception:
				print("Could not create Passport OS/radio loader")
				return
	else:
		return

	print("\nREMOVING .signed FILES...")
	for file in os.listdir(localdir):
		if file.endswith(".signed"):
			print("REMOVING: " + file)
			os.remove(file)

	print("\nMOVING LOADERS...")
	for files in os.listdir(localdir):
		if files.endswith(".exe") and files.startswith(("Q10", "Z10", "Z30", "Z3", "Passport")):
			loaderdest_os = os.path.join(loaderdir_os, files)
			print("MOVING: " + files)
			try:
				shutil.move(files, loaderdir_os)
			except shutil.Error:
				os.remove(loaderdest_os)

	print("\nCREATION FINISHED!")
	if autoloader == True:
		os.chdir(loaderdir_os)
		if device == 0:
			loaderfile = str(glob.glob("Z10*STL100-1*")[0])
		elif device == 1:
			loaderfile = str(glob.glob("Z10*STL100-2-3*")[0])
		elif device == 2:
			loaderfile = str(glob.glob("Z10*STL100-4*")[0])
		elif device == 3:
			loaderfile = str(glob.glob("Q10*")[0])
		elif device == 4:
			loaderfile = str(glob.glob("Z30*")[0])
		elif device == 5:
			loaderfile = str(glob.glob("Z3*")[0])
		elif device == 6:
			loaderfile = str(glob.glob("Passport*")[0])
		else:
			return
		if len(loaderfile) > 0:
			subprocess.call(loaderfile)
			print("\nFINISHED!!!")
		else:
			print("Error!")
			return
	else:
		print("\nFINISHED!!!")

if __name__ == '__main__':
	if len(sys.argv) > 1:
		parser = argparse.ArgumentParser(description="Create one autoloader for personal use.", epilog = "http://github.com/thurask/lazyloader")
		parser.add_argument("-v", "--version", action="version", version="%(prog)s " + _version)
		parser.add_argument("os", help="OS version, 10.x.y.zzzz")
		parser.add_argument("radio", help="Radio version, 10.x.y.zzzz")
		parser.add_argument("swrelease", help="Software version, 10.x.y.zzzz")
		devgroup = parser.add_argument_group("devices", "Device to load (one required)")
		compgroup = devgroup.add_mutually_exclusive_group(required=True)
		compgroup.add_argument("--stl100-1", dest="device", help="STL100-1", action="store_const", const=0)
		compgroup.add_argument("--stl100-x", dest="device", help="STL100-2/3, P'9982", action="store_const", const=1)
		compgroup.add_argument("--stl100-4", dest="device", help="STL100-4", action="store_const", const=2)
		compgroup.add_argument("--q10", dest="device", help="Q10, Q5, P'9983", action="store_const", const=3)
		compgroup.add_argument("--z30", dest="device", help="Z30, Classic, Leap", action="store_const", const=4)
		compgroup.add_argument("--z3", dest="device", help="Z3", action="store_const", const=5)
		compgroup.add_argument("--passport", dest="device", help="Passport", action="store_const", const=6)
		parser.add_argument("--run-loader", dest="autoloader", help="Run autoloader after creation", action="store_true", default=False)
		args = parser.parse_args(sys.argv[1:])
		if not isWindows():
			args.autoloader = False
		doMagic(args.os, args.radio, args.swrelease, args.device, os.getcwd(), args.autoloader)
	else:
		localdir = os.getcwd()
		osversion = input("OS VERSION: ")
		radioversion = input("RADIO VERSION: ")
		softwareversion = input("SOFTWARE RELEASE: ")
		device = int(input("SELECTED DEVICE (0=STL100-1; 1=STL100-2/3/P9983; 2=STL100-4; 3=Q10/Q5/P9983; \n4=Z30/CLASSIC/LEAP; 5=Z3; 6=PASSPORT): "))
		if isWindows():
			autoloader = str2bool(input("RUN AUTOLOADER (WILL WIPE YOUR DEVICE!)(Y/N)?: "))
		else:
			autoloader = False
		print(" ")
		doMagic(osversion, radioversion, softwareversion, device, localdir, autoloader)
