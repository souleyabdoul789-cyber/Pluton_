import mss, cv2, numpy as np, asyncio, os, time, datetime
import sounddevice as sd
from scipy.io.wavfile import write
from moviepy.editor import VideoFileClip, AudioFileClip

async def record_screen_with_audio(duree=10, fps=20):
    base = datetime.datetime.now().strftime('%H-%M-%S')
    video_tmp = os.path.join(os.getcwd(), f"tmp_video_{base}.mp4")
    audio_tmp = os.path.join(os.getcwd(), f"tmp_audio_{base}.wav")
    final = os.path.join(os.getcwd(), f"screen_{base}.mp4")

    freq = 44100

    def _record_video():
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            w, h = monitor["width"], monitor["height"]
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            out = cv2.VideoWriter(video_tmp, fourcc, fps, (w, h))
            fin = time.time() + duree
            while time.time() < fin:
                img = np.array(sct.grab(monitor))
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                out.write(img)
            out.release()

    def _record_audio():
        audio = sd.rec(int(duree * freq), samplerate=freq, channels=1, dtype='int16')
        sd.wait()
        write(audio_tmp, freq, audio)


    # lance les 2 en même temps
    await asyncio.gather(
        asyncio.to_thread(_record_video),
        asyncio.to_thread(_record_audio)
    )

    # fusion
    v_clip = VideoFileClip(video_tmp)
    a_clip = AudioFileClip(audio_tmp)
    v_clip = v_clip.set_audio(a_clip)
    v_clip.write_videofile(final, codec='libx264', audio_codec='aac', logger=None)

    # nettoyage
    os.remove(video_tmp)
    os.remove(audio_tmp)
    v_clip.close(); a_clip.close()

    return final

# test
async def main():
    await record_screen_with_audio(duree=10)


def screen_shoot():
    dossier_actuel = os.getcwd() 
    date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nom = f"screen_{date}.png"
    chemin = os.path.join(dossier_actuel, nom)

    with mss.mss() as sct:
        sct.shot(output=chemin)

    return chemin


screen_shoot()

#pip install sounddevice scipy
#pip install mss
