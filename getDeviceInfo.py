import wmi
import os
import sys
import threading
import time
import json

def getpath():
    if getattr(sys, "frozen", False):
        application_path = sys.executable
    elif __file__:
        application_path = os.path.abspath(__file__)
    return application_path

save_path = os.path.join(os.path.dirname(getpath()), "info")
try:
    if not os.path.isdir(save_path):
        os.makedirs(save_path)
except Exception as err:
    print(err)

def list_files(startpath):
    try:
        file_dict = {}
        for root, dirs, files in os.walk(startpath):
            for f in files:
                file_path = os.path.join(root, f)
                file_dict[file_path] = None
        return file_dict
    except Exception as err:
        print(err)
        return {}

def save_disk_info(added_disk):
    try:
        print(f'\033[0mNew disk detected: \033[1;32m[{getattr(added_disk, "Caption", None)}]')
        
        info = {
            "Access": getattr(added_disk, "Access", None), 
            "VolumeName": getattr(added_disk, "VolumeName", None), 
            "Description": getattr(added_disk, "Description", None), 
            "FileSystem": getattr(added_disk, "FileSystem", None), 
            "Size": getattr(added_disk, "Size", None), 
            "FreeSpace": getattr(added_disk, "FreeSpace", None), 
            "Files": list_files(getattr(added_disk, "Caption", None))
        }

        for i in info:
            if not i in ["Files"]:
                print(f"\033[0m{i}: \033[1;32m{info[i]}")

        with open(os.path.join(save_path, f"{added_disk.VolumeName}_{int(time.time())}.json"), "w") as f:
            json.dump(info, f, ensure_ascii=True, indent=4)
            print(f'\033[0mSaved disk info: \033[1;32m[{getattr(added_disk, "Caption", None)}]')
    except Exception as err:
        print(err)
    print()

c = wmi.WMI()

watcher = c.watch_for(
    notification_type="Creation",
    wmi_class="Win32_LogicalDisk",
    delay_secs=1
)

while True:
    try:
        added_disk = watcher()

        save_disk_info_thread = threading.Thread(target=save_disk_info, args=(added_disk,))
        save_disk_info_thread.start()
    except wmi.x_wmi_timed_out:
        pass
