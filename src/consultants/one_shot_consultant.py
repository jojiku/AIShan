from typing import Union, Callable, Type

from .consultant_interface import ConsultantInterface
from .advanced_consultant import AdvancedConsultant
from .recipe_consultant import RecipeConsultant
from src.classification_models import GPTClassificator
from src.actions import tell_joke

classification_model = GPTClassificator()

intent_dict = {"joke": tell_joke,
               "balance": 'Ваша карта активна. Сейчас на вашей карте: 0 базовых баллов 0 экспресс-баллов 0 купонов',
               "get_points": 'Получайте кешбэк баллами до 70% за покупку товаров со специальными ценниками.\
                              Для накопления и списания баллов покажите карту на кассе перед оплатой покупки.\
                              А еще дарим праздничный кешбэк 10% за неделю до и после Дня рождения.',
               "spend_points": 'Оплачивайте до 100% стоимости покупок баллами во всех магазинах АШАН.\
                                Для списания баллов перед оплатой отсканируйте карту АШАН.\
                                Обратите внимание, что списывать баллы можно только если карта зарегистрирована.',
                "social_status": 'По будням с 7:00 до 12:00 начисляем дополнительный кешбэк 7% баллами клиентам с социальным статусом!\
                                  Как получать социальный кешбэк?\
                                  Зарегистрируйте карту АШАН\
                                  Получите социальный статус карты АШАН\
                                  Покажите карту сотруднику магазина перед оплатой покупки',
                "card_registartion": "для регистрации карты АШАН, пожалуйста, скачайте приложение Мой АШАН по ссылке\
                                      или продиктуйте номер карты",
                "my_orders": "Пока я могу проконсультировать вас только по интернет-заказам. Информацию о покупках в магазинах АШАН и АТАК можно увидеть в личном кабинете на сайте",
                "refunds": "Вернуть товар — ЛЕГКО!\
                            В магазинах АШАН и АТАК:\
                            При покупке в гипермаркете - обратитесь в любой гипермаркет на Пункт обслуживания клиентов",
                "promotions": "Тысячи товаров для вас по суперценам вы можете найти на сайте",
                "store_search": "Назовите свое местоположение",
                "other_consultant": AdvancedConsultant(),
                "recipe_consultant": RecipeConsultant()}


class OneShotConsultant(ConsultantInterface):
    
    def get_answer(self, chat: list, *args, **kwargs) -> Union[str, Callable, Type[ConsultantInterface]]:

        client_text = chat[-1]["content"]

        intent = classification_model.define_intent(client_text)

        response = intent_dict.get(intent, "Не понял вас")

        return response
    
    @property
    def speaker(self):
        return "xenia"
