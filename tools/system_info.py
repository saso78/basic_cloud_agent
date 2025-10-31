# tasks/system_info.py
import shutil

def get_disk_usage():
    total, used, free = shutil.disk_usage("/")
    return f"💾 Disk Usage: {used // (2**30)}GB used / {total // (2**30)}GB total"

