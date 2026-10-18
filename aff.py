import pyfiglet,asyncio
from rich.console import Console
from rich.panel import Panel
from rich.progress import track
import os
import random
import time
c = Console()
async def pogres(texte,n=0.09):
    for i in track(range(100),description=f"[bold red]{texte}[/]"):
        await asyncio.sleep(n)

async def matrix_effect(duration=3):
    clear()
    chars = "01アイウエオカキクケコサシ☠️スセソABCDEFGHIJK☠️LMNOPQRSTUVWXY☠️Z"
    end_time = asyncio.get_event_loop().time() + duration
    while asyncio.get_event_loop().time() < end_time:
        line = "".join(random.choice(chars) for _ in range(60))
        c.print(f"[bold magenta]{line}[/]")
        await asyncio.sleep(0.02)
    c.print(Panel("\n[bold  yellow]            Don't Worry I'm[/][bold red] MR GHOST[/]\n",style="red"))
    await asyncio.sleep(1)
    clear()
"""def matrix_effect(duration=3):
    chars = "01アイウエオカキクケコサシスセソABCDEFGHIJKLMNOPQRSTUVWXYZ"
    end_time = time.time() + duration
    while time.time() < end_time:
        line = "".join(random.choice(chars) for _ in range(60))
        c.print(f"[bold magenta]{line}[/]")
        time.sleep(0.05)

"""
def clear():
    os.system("cls" if os.name == "nt" else "clear")
async def titre(text):
    clear()
    await matrix_effect()
    await asyncio.sleep(0.5)
    c.print(Panel("[bold yellow][WARING][/] [bold blue]cet outil est conçu uniquement à des fins [bold green]éducatif[/] toute utilisation De nos services dans le cadre de [bold red]volé ou d'espionner[/] des gens sans leurs consentement est puni par la [yellow]loi et vous risqueriez une poursuite juduciare[/], nous ne sommes en aucun cas responsable de vos actes. merci à bon entendeur salut. profitez [/]\n",style="red"))
    await pogres("wait")
    clear()
    await asyncio.sleep(1)
    f = pyfiglet.Figlet(font="ansi_shadow")
    r = f.renderText(text)
    c.print(Panel(f"[bold yellow]{r}[/]\n      [bold blue][green]GAN v1.0.1[/] @By G-SOCIETY/DEV/GHOST[/]",style="magenta"))

async def smooth(texte,color="cyan",delay=0.03):
    for char in texte:
        c.print(f"[{color}]{char}[/]",end="")
        await asyncio.sleep(delay)

#asyncio.run(titre("GAN"))
