from typing import Type

from .consultant_interface import ConsultantInterface
from src.classification_models.base import TestClassificationModel

classification_model = TestClassificationModel()

intent_dict = {"joke": "Шутка"}


class OneShotConsultant(ConsultantInterface):
    
    def get_answer(self, chat: list, *args, **kwargs) -> str:

        client_text = chat[-1]["content"]

        intent = classification_model.define_intent(client_text)

        msg = intent_dict.get(intent, "Не понял вас")

        return msg