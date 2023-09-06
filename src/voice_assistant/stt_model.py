import queue
import sounddevice as sd
from pathlib import Path
from typing import Optional

from vosk import Model, KaldiRecognizer
import wave


class STTModel:
    """ 
    Модель перевода речи в текст
    
    Parameters
    ----------
    model_path: Path - путь до модели
    device: str or None - Устройство вывода (id устройства вывода), если нет, то устройство по умолчанию.
    """
    def __init__(self, model_path: Path, device: Optional[int] = None):
        self.model = Model(str(model_path.absolute()))
        self.device = device
        device_info = sd.query_devices(device, "input")
        self.samplerate = device_info["default_samplerate"]

        self.q = queue.Queue()

    
    def callback(self, indata, *args, **kwargs):
        """This is called (from a separate thread) for each audio block."""
        self.q.put(bytes(indata))

    def  phrase_to_str(self) -> str:
        """ Метод перевода речи в текст. Вызов модели запускает выбранный микрофон на считывание
        
        Returns
        --------
        text: str - Фраза, которую распознала модель.
        """

        with sd.RawInputStream(samplerate=self.samplerate, blocksize = 8000, device=self.device,
                    dtype="int16", channels=1, callback=self.callback):
            
            rec = KaldiRecognizer(self.model, self.samplerate)

            while True:
                data = self.q.get()
                if rec.AcceptWaveform(data):
                    break
            
            return eval(rec.FinalResult())["text"]
        
    def file_to_str(self, file: Path) -> str:
        """ Метод перевода речи в текст. Вызов модели запускает выбранный микрофон на считывание

        Parameters
        ----------
        file: Path - путь до записи

        
        Returns
        --------
        text: str - Фраза, которую распознала модель. 
        
        """

        results = ""
        
        with wave.open(str(file), "rb") as wf:

            recognizer = KaldiRecognizer(self.model, wf.getframerate())
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if recognizer.AcceptWaveform(data):
                    recognizerResult = eval(recognizer.Result())["text"]
                    results = results + " " + recognizerResult

            recognizerResult = eval(recognizer.FinalResult())["text"]
            results = results + " " + recognizerResult



        return results


            
if __name__ == "__main__":
    model = STTModel(Path("data/models/vosk-model-small"))

    # test file
    print(model.file_to_str(Path("data/raw_data/test.wav")))


    # test micro
    while True:
        text = model.phrase_to_str()
        print(text)
