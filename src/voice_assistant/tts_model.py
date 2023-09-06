import os
import torch
from pathlib import Path
import sounddevice as sd

torch._C._jit_set_profiling_mode(False)


class TTSModel:
    """ 
    Модель перевода текст в речь
    
    Parameters
    ----------
    model_path: Path - путь до модели
    sample_rate: int - Частота дискретизации
    speaker: str  - Говорящий (доступные варианты: aidar, baya, kseniya, xenia, eugene)
    put_accent: bool
    put_yo: bool
    device: str - Устройство работы сети (cpu, cuda и тд.) 
    num_threads: int - Количество потоков для рассчета
    """
    def __init__(self, 
                 model_path: Path = Path("data/models/model.pt"), 
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

    def str_to_phrase(self, text: str, speaker: str | None = None) -> None:
        """ Метод перевода текста в речь.
        
        Parameters
        ----------
        text: str - Текст, который необходимо озвучить
        """
        speaker = speaker if speaker is not None else self.speaker

        audio = self.model.apply_tts(text = text,
                                     speaker = speaker,
                                     put_accent = self.put_accent,
                                     put_yo = self.put_yo)

        sd.play(audio, self.sample_rate)
        sd.wait()
        sd.stop()

    def str_to_file(self, text: str, file: Path, speaker: str | None = None) -> None:
        """ Метод перевода текста в речь.
        
        Parameters
        ----------
        text: str - Текст, который необходимо озвучить

        file: Path - Имя файла, в который записать голос
        """
        speaker = speaker if speaker is not None else self.speaker

        audio = self.model.save_wav(text = text,
                                    speaker = speaker,
                                    put_accent = self.put_accent,
                                    put_yo = self.put_yo,
                                    audio_path=str(file))

        

if __name__ == "__main__":
    model = TTSModel(Path("data/models/model.pt"))

    example_text = 'Привет мир!'
    model.str_to_phrase(example_text)

    model.str_to_file(example_text, Path("data/raw_data/tts_text.wav"))
