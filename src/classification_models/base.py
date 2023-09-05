from abc import ABC, abstractmethod


class BaseClassificationModel(ABC):

    @abstractmethod
    def define_intent(self, text: str, *args, **kwargs) -> str:
        """ По тексту запроса определить намерение """
        pass


class TestClassificationModel(ABC):
    def define_intent(self, text: str, *args, **kwargs) -> str:
        return text
