import queue
import sounddevice as sd
from pathlib import Path
from typing import Optional

from vosk import Model, KaldiRecognizer


class STTModel:
    def __init__(self, model_path: Path, device: Optional[int] = None):
        self.model = Model(str(model_path.absolute()))
        self.device = device
        device_info = sd.query_devices(device, "input")
        self.samplerate = device_info["default_samplerate"]

        self.q = queue.Queue()

    
    def callback(self, indata, *args, **kwargs):
        """This is called (from a separate thread) for each audio block."""
        self.q.put(bytes(indata))

    def  phrase_to_str(self) -> None:

        with sd.RawInputStream(samplerate=self.samplerate, blocksize = 8000, device=self.device,
                    dtype="int16", channels=1, callback=self.callback):
            
            rec = KaldiRecognizer(self.model, self.samplerate)

            while True:
                data = self.q.get()
                if rec.AcceptWaveform(data):
                    break
            
            return eval(rec.Result())["text"]
            
if __name__ == "__main__":
    model = STTModel(Path("data/models/vosk-model-small"))
    while True:
        text = model.phrase_to_str()
        print(text)
