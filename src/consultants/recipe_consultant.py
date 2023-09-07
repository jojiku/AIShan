import openai

from .consultant_interface import ConsultantInterface

def get_completion(messages, model="gpt-3.5-turbo"):
    messages = [{"role": "system", "content": "Ты консультант по приготовлению еды в магазине Ашан. Тебя зовут Мария.\
                                               Ты должена представиться и спрость, какие пожелания есть у клиентов в еде. \
                                               А затем, когда клиент расскажет какую еду он любит - предложи ему, \
                                               что приготовить и какие продукты ему нужно купить в Ашане. \
                                               Старайся отвечать максимально кратко"}] + messages[-10:]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0.2, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]

def get_simple_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]


class RecipeConsultant(ConsultantInterface):
    def get_answer(self, chat, *args, **kwargs) -> str:

        answer = get_completion(chat)

        return answer
    
    @property
    def speaker(self):
        return "baya"
    

    def find_ingridients(self, text: str):
        prompt = f"""Identify the products for cookings from the text.\
            The review is delimited with triple backticks.

            Text: ```{text}```

            The answer should be a list of words separated by commas
            """
        
        return get_simple_completion(prompt)

