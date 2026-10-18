import cv2
import sounddevice as sd
import numpy as np
import asyncio
from scipy.io.wavfile import write as write_wav
from datetime import datetime
from pathlib import Path
import subprocess

async def record_webcam_async(duration=10, output_dir="."):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        base = Path(output_dir) / f"record_{timestamp}"
        
        video_tmp = str(base) + "_video.mp4"
        audio_tmp = str(base) + "_audio.wav"
        final_file = str(base) + ".mp4"

        samplerate = 44100
        audio_data = []

        def audio_callback(indata, frames, time, status):
            audio_data.append(indata.copy())

        def _blocking_capture():
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                return {"error": "webcam"}

            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = 20.0
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(video_tmp, fourcc, fps, (width, height))

            stream = sd.InputStream(samplerate=samplerate, channels=2, callback=audio_callback)
            stream.start()

            frames_to_capture = int(duration * fps)
            for _ in range(frames_to_capture):
                ret, frame = cap.read()
                if not ret:
                    break
                out.write(frame)

            stream.stop()
            stream.close()
            cap.release()
            out.release()
            return True

        # Le gros travail bloquant passe en thread sans bloquer l'event loop
        result = await asyncio.to_thread(_blocking_capture)

        if isinstance(result, dict):
            return result

        if len(audio_data) == 0:
            return "error: pas d'audio"

        # save audio et merge en async aussi
        audio_np = np.concatenate(audio_data, axis=0)
        await asyncio.to_thread(write_wav, audio_tmp, samplerate, audio_np)

        cmd = ["ffmpeg", "-y", "-i", video_tmp, "-i", audio_tmp, "-c:v", "copy", "-c:a", "aac", final_file]
        await asyncio.to_thread(subprocess.run, cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        Path(video_tmp).unlink(missing_ok=True)
        Path(audio_tmp).unlink(missing_ok=True)

        return final_file

    except Exception as e:
        return f"error:{e}"
