import openai

from .consultant_interface import ConsultantInterface

def get_completion(messages, model="gpt-3.5-turbo"):
    messages = [{"role": "system", "content": "Ты старший консультант в магазине Ашан. Тебя зовут Андрей.\
                                               Ты должен представиться и спрость, чем можешь помочь. \
                                               А затем, когда клиент расскажет о своей проблеме ты должен предложить ее решение. \
                                               Старайся отвечать максимально кратко"}] + messages[-10:]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]


class AdvancedConsultant(ConsultantInterface):
    def get_answer(self, chat, *args, **kwargs) -> str:

        answer = get_completion(chat)

        return answer
    
    @property
    def speaker(self):
        return "eugene"