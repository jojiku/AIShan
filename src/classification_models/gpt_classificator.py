import openai

from .base import BaseClassificationModel

def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]

class GPTClassificator(BaseClassificationModel):
    def define_intent(self, text: str, *args, **kwargs) -> str:
        
        prompt = f"""
                You're a classification model.\
                According to the text in Russian, you must determine the client's intention from text which is delimited with triple backticks\
                and return one of these classes.\
                Intentions and their description are presented below in the format: "intention: description"

                balance: Клиент хочет узнать баланс на карте лояльности
                get_points: Клиент хочет узнать, как набрать баллы
                spend_points: Клиент хочет узнать, как списать баллы

                social_status: клиент хочет узнать про социальный статус и социальную поддержку
                card_registartion: клиент хочет зарегистрировать карту

                my_orders: клиент хочет узнать про его заказы или их статус
                refunds: Клиент хочет узнать информацию про отказы и возвраты товара

                promotions: Клиент хочет узнать про заказы

                store_search: Клиент хочет найти ближайшие магазины 

                other_consultant: Если клиент хочет вызвать оператора

                joke: Если клиент хочет, чтобы ему рассказали шутку

                recipe_consultant: Если клиент хочет, чтобы ему помогли с едой, ужином, рецептами 
                
                If it is not possible to recognize the intent, then you need to return "other_consultant"

                Text: ```{text}```

                Your answer must be one of this options: \
                [balance, get_points, spend_points, social_status, card_registartion, my_orders, refunds, promotions, store_search, other_consultant, \
                joke, recipe_consultant]

                """

        return get_completion(prompt)