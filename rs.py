from pathlib import Path

def ls_user():
    home = Path.home()
    
    for f in home.rglob("*"):
        # 1. skip fichiers cachés: .cache .config .local etc
        if any(part.startswith(".") for part in f.parts):
            continue
        
        # 2. skip si c'est un dossier, garde que fichiers
        if not f.is_file():
            continue
            
        print(f)

ls_user()
