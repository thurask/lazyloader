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

# Get 64 or 32 bit
def is64Bit():
	amd64 = platform.machine().endswith("64")
	return amd64

# Set 7z executable based on bit type
def getSevenZip():
	if is64Bit() == True:
		return "7za64.exe"
	else:
		return "7za.exe"
	
# Get corecount, with fallback 
def getCoreCount():
	cores = str(os.cpu_count())  # thank you Python 3.4
	if os.cpu_count() == None:
		cores = str(1)
	return cores

# Extract bars with 7z
def extractBar(filepath):
	for file in os.listdir(filepath):
		if file.endswith(".bar"):
			try:
				subprocess.call(getSevenZip() + " x " + '"' + file + '" *.signed -aos', shell=True)
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
	version = "2015-04-12-A"  # update as needed
	release = "https://github.com/thurask/lazyloader/releases/latest"
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
				subprocess.call("cap.exe create " + os_ti + " " + radio_z10_ti + " Z10_" + osversion + "_STL100-1.exe", shell=True)
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
				subprocess.call("cap.exe create " + os_8960 + " " + radio_z10_qcm + " Z10_" + osversion + "_STL100-2-3.exe", shell=True)
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
				subprocess.call("cap.exe create " + os_8960 + " " + radio_z10_vzw + " Z10_" + osversion + "_STL100-4.exe", shell=True)
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
				subprocess.call("cap.exe create " + os_8960 + " " + radio_q10 + " Q10_" + osversion + "_SQN100-1-2-3-4-5.exe", shell=True)
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
				subprocess.call("cap.exe create " + os_8960 + " " + radio_z30 + " Z30_" + osversion + "_STA100-1-2-3-4-5-6.exe", shell=True)
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
				subprocess.call("cap.exe create " + os_8x30 + " " + radio_z3 + " Z3_" + osversion + "_STJ100-1-2.exe", shell=True)
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
				subprocess.call("cap.exe create " + os_8974 + " " + radio_8974 + " Passport_" + osversion + "_SQW100-1-2-3.exe", shell=True)
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
		parser = argparse.ArgumentParser(description="Create one autoloader for personal use.", usage="%(prog)s OSVERSION RADIOVERSION SWVERSION DEVICE", epilog = "http://github.com/thurask/lazyloader")
		parser.add_argument("os", help="OS version, 10.x.y.zzzz")
		parser.add_argument("radio", help="Radio version, 10.x.y.zzzz")
		parser.add_argument("swrelease", help="Software version, 10.x.y.zzzz")
		parser.add_argument("device", type=deviceRange, help="0=STL100-1\n1=STL100-2/3/P9983\n2=STL100-4\n3=Q10/Q5/P9983\n4=Z30/CLASSIC/LEAP\n5=Z3\n6=PASSPORT")
		parser.add_argument("--run-loader", dest="autoloader", help="Run autoloader after creation", action="store_true", default=False)
		args = parser.parse_args(sys.argv[1:])
		
		doMagic(args.os, args.radio, args.swrelease, args.device, os.getcwd(), args.autoloader)
	else:
		localdir = os.getcwd()
		osversion = input("OS VERSION: ")
		radioversion = input("RADIO VERSION: ")
		softwareversion = input("SOFTWARE RELEASE: ")
		device = int(input("SELECTED DEVICE (0=STL100-1; 1=STL100-2/3/P9983; 2=STL100-4; 3=Q10/Q5/P9983; \n4=Z30/CLASSIC/LEAP; 5=Z3; 6=PASSPORT): "))
		autoloader = str2bool(input("RUN AUTOLOADER (Y/N)?: "))
		print(" ")
		doMagic(osversion, radioversion, softwareversion, device, localdir, autoloader)
