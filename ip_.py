import subprocess, re, platform

def get_hotspot_ip():
    try:
        if platform.system() == "Windows":
            out = subprocess.check_output("ipconfig", encoding="cp850", errors="ignore")
            m = re.search(r"(?:Passerelle|Gateway).*?(\d+\.\d+\.\d+\.\d+)", out)
            if m and m.group(1) != "0.0.0.0":
                return m.group(1)
        else:
            out = subprocess.check_output(["ip", "route"], text=True, stderr=subprocess.DEVNULL)
            m = re.search(r"default via (\d+\.\d+\.\d+\.\d+)", out)
            if m:
                return m.group(1)
    except:
        pass
    return "192.168.43.1" 
