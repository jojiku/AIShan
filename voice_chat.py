
from pathlib import Path
from openai.error import RateLimitError

from src.consultants.one_shot_consultant import OneShotConsultant, ConsultantInterface
from src.voice_assistant import STTModel, TTSModel

from time import sleep


messages = []
consultant = OneShotConsultant()
speaker = consultant.speaker
tts_model = TTSModel(Path("data/models/model.pt"))
stt_model = STTModel(Path("data/models/vosk-model-small"))

def add_message(role: str, content: str) -> None:
    messages.append({"role": role, "content": content})


def get_bot_answer(chat: list) -> str:

    global consultant, speaker, messages

    response = consultant.get_answer(chat)

    if isinstance(response, str):
        return response
    elif callable(response):
        return response()
    elif isinstance(response, ConsultantInterface):
        tts_model.str_to_phrase("Перевожу вас к другому консультанту", speaker)
        messages = []
        consultant = response
        speaker = response.speaker

        return get_bot_answer(messages)
    else:
        return "Что-то пошло не так"
    

if __name__ == "__main__":

    tts_model.str_to_phrase("Здравствуйте, я голосовой помошник Ксения. Чем вам помочь? ")

    while True:
        text = stt_model.phrase_to_str()
        print(text)
        add_message("user", text)
        
        try:
            answer = get_bot_answer(messages)
            print(answer)
            add_message("assistant", answer)

            tts_model.str_to_phrase(answer, speaker)
        except RateLimitError:
            tts_model.str_to_phrase("Подаждите пожалуйста", speaker)
            sleep(20)
    
