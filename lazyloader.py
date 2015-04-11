import os
import glob
import shutil
import platform
import hashlib
import urllib.request

def doMagic():
    localdir = os.getcwd()
    osversion = input("OS VERSION: ")
    radioversion = input("RADIO VERSION: ")
    softwareversion = input("SOFTWARE RELEASE: ")
    device = int(input("SELECTED DEVICE (0=STL100-1; 1=STL100-2/3/P9983; 2=STL100-4; 3=Q10/Q5/P9983; 4=Z30/CLASSIC/LEAP; 5=Z3; 6=PASSPORT): "))
    
    # hash SW release
    sha1 = hashlib.sha1(softwareversion.encode('utf-8'))
    hashedsoftwareversion = sha1.hexdigest()
    
    if device == 0:
        osurl = "http://cdn.fs.sl.blackberry.com/fs/qnx/production/" + hashedsoftwareversion + "/winchester.factory_sfi.desktop-" + osversion + "-nto+armle-v7+signed.bar"
        radiourl = "http://cdn.fs.sl.blackberry.com/fs/qnx/production/" + hashedsoftwareversion + "/m5730-" + radioversion + "-nto+armle-v7+signed.bar"
    elif device == 1:
        osurl = "http://cdn.fs.sl.blackberry.com/fs/qnx/production/" + hashedsoftwareversion + "/qc8960.factory_sfi.desktop-" + osversion + "-nto+armle-v7+signed.bar"
        radiourl = "http://cdn.fs.sl.blackberry.com/fs/qnx/production/" + hashedsoftwareversion + "/qc8960-" + radioversion + "-nto+armle-v7+signed.bar"
    elif device == 2:
        osurl = "http://cdn.fs.sl.blackberry.com/fs/qnx/production/" + hashedsoftwareversion + "/qc8960.factory_sfi.desktop-" + osversion + "-nto+armle-v7+signed.bar"
        radiourl = "http://cdn.fs.sl.blackberry.com/fs/qnx/production/" + hashedsoftwareversion + "/qc8960.omadm-" + radioversion + "-nto+armle-v7+signed.bar"
    elif device == 3:
        osurl = "http://cdn.fs.sl.blackberry.com/fs/qnx/production/" + hashedsoftwareversion + "/qc8960.factory_sfi.desktop-" + osversion + "-nto+armle-v7+signed.bar"
        radiourl = "http://cdn.fs.sl.blackberry.com/fs/qnx/production/" + hashedsoftwareversion + "/qc8960.wtr-" + radioversion + "-nto+armle-v7+signed.bar"
    elif device == 4:
        osurl = "http://cdn.fs.sl.blackberry.com/fs/qnx/production/" + hashedsoftwareversion + "/qc8960.factory_sfi.desktop-" + osversion + "-nto+armle-v7+signed.bar"
        radiourl = "http://cdn.fs.sl.blackberry.com/fs/qnx/production/" + hashedsoftwareversion + "/qc8960.wtr5-" + radioversion + "-nto+armle-v7+signed.bar"
    elif device == 5:
        osurl = "http://cdn.fs.sl.blackberry.com/fs/qnx/production/" + hashedsoftwareversion + "/qc8960.factory_sfi_hybrid_qc8x30.desktop-" + osversion + "-nto+armle-v7+signed.bar"
        radiourl = "http://cdn.fs.sl.blackberry.com/fs/qnx/production/" + hashedsoftwareversion + "/qc8930.wtr5-" + radioversion + "-nto+armle-v7+signed.bar"
    elif device == 6:
        osurl = "http://cdn.fs.sl.blackberry.com/fs/qnx/production/" + hashedsoftwareversion + "/qc8960.factory_sfi_hybrid_qc8974.desktop-" + osversion + "-nto+armle-v7+signed.bar"
        radiourl = "http://cdn.fs.sl.blackberry.com/fs/qnx/production/" + hashedsoftwareversion + "/qc8974.wtr2-" + radioversion + "-nto+armle-v7+signed.bar"
    else:
        return("PICK A REAL DEVICE!")
    
    # Get OS type, set 7z
    amd64 = platform.machine().endswith("64")
    if amd64 == True:
        sevenzip = "7za64.exe"
    else:
        sevenzip = "7za.exe"

    # Extract bars with 7z
    def extract():
        print("EXTRACTING...")
        for file in os.listdir(localdir):
            if file.endswith(".bar"):
                print("\nEXTRACTING: " + file + "\n")
                os.system(sevenzip + " x " + '"' + file + '" *.signed -aos')

    def download(url):
        file_name = url.split('/')[-1]
        u = urllib.request.urlopen(url)
        f = open(file_name, 'wb')
        file_size = int(u.getheader("Content-Length"))
        print("\nDownloading: {0}\nBytes: {1}".format(url, file_size))

        file_size_dl = 0
        block_sz = 524288 #0.5 MB; larger chunks crap out easily
        while file_size_dl < file_size:
            buffer = u.read(block_sz)
            if not buffer:
                break
        
            file_size_dl += len(buffer)
            f.write(buffer)
            p = float(file_size_dl) / file_size
            status = r"{0} MB  [{1:.2%}]".format((file_size_dl/1048576), p)
            status = status + chr(8)*(len(status)+1)
            print(status)
            
        f.close()

    download(osurl)
    print("\n")
    download(radiourl)
    
    extract()

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
    
    if device == 0:
        try:
            os_ti = str(glob.glob("qcfm.image.com.qnx.coreos.qcfm.os.factory_sfi.desktop.*.signed")[0])
        except IndexError:
            print("No OMAP image found, trying 10.3.1 name\n")
            try:
                os_ti = str(glob.glob("*winchester*.signed")[0])
            except IndexError:
                print("No OMAP image found\n")
                return
        try:
            radio_z10_ti = str(glob.glob("*radio.m5730*.signed")[0])
        except IndexError:
            print("No OMAP radio found\n")
            return
        else:
            print("Creating OMAP Z10 OS...\n")
            try:
                os.system("cap.exe create " + os_ti + " " + radio_z10_ti + " Z10_" + osversion + "_STL100-1.exe")
            except Exception:
                print("Could not create STL100-1 OS/radio loader\n")
                return
    elif device == 1:
        try:
            os_8960 = str(glob.glob("*qc8960*_sfi.desktop*.signed")[0])
        except IndexError:
            print("\nNo 8960 image found\n")
            return
        try:
            radio_z10_qcm = str(glob.glob("*radio.qc8960.BB*.signed")[0])
        except IndexError:
            print("No 8960 radio found\n")
            return
        else:
            print("Creating Qualcomm Z10 OS...\n")
            try:
                os.system("cap.exe create " + os_8960 + " " + radio_z10_qcm + " Z10_" + osversion + "_STL100-2-3.exe")
            except Exception:
                print("Could not create Qualcomm Z10 OS/radio loader\n")
                return
    elif device == 2:
        try:
            os_8960 = str(glob.glob("*qc8960*_sfi.desktop*.signed")[0])
        except IndexError:
            print("\nNo 8960 image found\n")
            return
        try:
            radio_z10_vzw = str(glob.glob("*radio.qc8960*omadm*.signed")[0])
        except IndexError:
            print("No Verizon 8960 radio found\n")
            return
        else:
            print("Creating Verizon Z10 OS...\n")
            try:
                os.system("cap.exe create " + os_8960 + " " + radio_z10_vzw + " Z10_" + osversion + "_STL100-4.exe")
            except Exception:
                print("Could not create Verizon Z10 OS/radio loader\n")
                return
    elif device == 3:
        try:
            os_8960 = str(glob.glob("*qc8960*_sfi.desktop*.signed")[0])
        except IndexError:
            print("\nNo 8960 image found\n")
            return
        try:
            radio_q10 = str(glob.glob("*8960*wtr.*.signed")[0])
        except IndexError:
            print("No Q10/Q5 radio found\n")
            return
        else:
            print("Creating Q10/Q5 OS...\n")
            try:
                os.system("cap.exe create " + os_8960 + " " + radio_q10 + " Q10_" + osversion + "_SQN100-1-2-3-4-5.exe")
            except Exception:
                print("Could not create Q10/Q5 OS/radio loader\n")
                return
    elif device == 4:
        try:
            os_8960 = str(glob.glob("*qc8960*_sfi.desktop*.signed")[0])
        except IndexError:
            print("\nNo 8960 image found\n")
            return
        try:
            radio_z30 = str(glob.glob("*8960*wtr5*.signed")[0])
        except IndexError:
            print("No Z30/Classic radio found\n")
            return
        else:
            print("Creating Z30/Classic OS...\n")
            try:
                os.system("cap.exe create " + os_8960 + " " + radio_z30 + " Z30_" + osversion + "_STA100-1-2-3-4-5-6.exe")
            except Exception:
                print("Could not create Z30/Classic OS/radio loader\n")
                return
    elif device == 5:
        try:
            os_8x30 = str(glob.glob("*qc8x30*desktop*.signed")[0])
        except IndexError:
            print("No 8x30 image found\n")
            return
        try:
            radio_z3 = str(glob.glob("*8930*wtr5*.signed")[0])
        except IndexError:
            print("No Z3 radio found\n")
            return
        else:
            print("Creating Z3 OS...\n")
            try:
                os.system("cap.exe create " + os_8x30 + " " + radio_z3 + " Z3_" + osversion + "_STJ100-1-2.exe")
            except Exception:
                print("Could not create Z3 OS/radio loader\n")
                return
    elif device == 6:
        try:
            os_8974 = str(glob.glob("*qc8974*desktop*.signed")[0])
        except IndexError:
            print("No 8974 image found\n")
            return
        try:
            radio_8974 = str(glob.glob("*8974*wtr2*.signed")[0])
        except IndexError:
            print("No Passport radio found\n")
            return
        else:
            print("Creating Passport OS...\n")
            try:
                os.system("cap.exe create " + os_8974 + " " + radio_8974 + " Passport_" + osversion + "_SQW100-1-2-3.exe")
            except Exception:
                print("Could not create Passport OS/radio loader\n")
                return
    else:
        return("PICK A REAL DEVICE!")   

    print("REMOVING .signed FILES...\n")
    for file in os.listdir(localdir):
        if file.endswith(".signed"):
            print("REMOVING: " + file)
            os.remove(file)

    print("\nMOVING...\n")
    for files in os.listdir(localdir):
        if files.endswith(".bar"):
            print("MOVING: " + files)
            if os.path.getsize(files) > 90000000:  # even the fattest radio is less than 90MB
                shutil.move(files, bardir_os)
            else:
                shutil.move(files, bardir_radio)
        if files.endswith(".exe") and files.startswith(("Q10", "Z10", "Z30", "Z3", "Passport")):
            print("MOVING: " + files)
            shutil.move(files, loaderdir_os)

    print("\nCREATION FINISHED!\n")
    
    autoloader = input("RUN AUTOLOADER (Y/N)?: ")
    if autoloader == "y" or autoloader == "Y" or autoloader == "yes":
        os.chdir(loaderdir_os)
        if device == 0:
            loaderfile = str(glob.glob("Z10*STL100-1*")[0])
            os.system(loaderfile)
        elif device == 1:
            loaderfile = str(glob.glob("Z10*STL100-2-3*")[0])
            os.system(loaderfile)
        elif device == 2:
            loaderfile = str(glob.glob("Z10*STL100-4*")[0])
            os.system(loaderfile)
        elif device == 3:
            loaderfile = str(glob.glob("Q10*")[0])
            os.system(loaderfile)
        elif device == 4:
            loaderfile = str(glob.glob("Z30*")[0])
            os.system(loaderfile)
        elif device == 5:
            loaderfile = str(glob.glob("Z3*")[0])
            os.system(loaderfile)
        elif device == 6:
            loaderfile = str(glob.glob("Passport*")[0])
            os.system(loaderfile)
        else:
            return("UH OH, NO AUTOLOADERS?")
    else:
        pass

if __name__ == '__main__':
    doMagic()
    smeg = input("Press Enter to exit")
