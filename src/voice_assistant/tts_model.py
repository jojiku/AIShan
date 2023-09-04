import os
import torch
from pathlib import Path
import sounddevice as sd
import time


class TTSModel:
    def __init__(self, 
                 model_path: Path, 
                 sample_rate: int = 48000, 
                 speaker: str = 'baya', 
                 put_accent: bool = True, 
                 put_yo: bool = True, 
                 device: str = "cpu", 
                 num_threads: int = 4):
        
        self.sample_rate = sample_rate
        self.speaker = speaker
        self.put_accent = put_accent
        self.put_yo = put_yo

        self.device = torch.device(device)
        torch.set_num_threads(num_threads)


        if not os.path.isfile(model_path):
            torch.hub.download_url_to_file('https://models.silero.ai/models/tts/ru/v4_ru.pt',
                                           model_path)  

        self.model = torch.package.PackageImporter(model_path).load_pickle("tts_models", "model")
        self.model.to(device)

    def str_to_phrase(self, text: str):

        audio = self.model.apply_tts(text = text,
                                     speaker = self.speaker,
                                     put_accent = self.put_accent,
                                     put_yo = self.put_yo)

        sd.play(audio)
        time.sleep(len(audio) / self.sample_rate)
        sd.stop()

if __name__ == "__main__":
    model = TTSModel(Path("data/models/model.pt"))

    example_text = 'Привет мир!'
    model.str_to_phrase(example_text)
