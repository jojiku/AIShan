from abc import ABC, abstractmethod

class ConsultantInterface(ABC):
    
    @abstractmethod
    def get_answer(self, chat, *args, **kwargs) -> str:
        pass