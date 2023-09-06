from typing import Union, Callable, Type

from .consultant_interface import ConsultantInterface
from src.classification_models.base import TestClassificationModel
from src.actions import tell_joke

classification_model = TestClassificationModel()

intent_dict = {"joke": tell_joke}


class OneShotConsultant(ConsultantInterface):
    
    def get_answer(self, chat: list, *args, **kwargs) -> Union[str, Callable, Type[ConsultantInterface]]:

        client_text = chat[-1]["content"]

        intent = classification_model.define_intent(client_text)

        response = intent_dict.get(intent, "Не понял вас")

        return response
