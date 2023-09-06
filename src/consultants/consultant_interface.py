from abc import ABC, abstractmethod, abstractproperty

class ConsultantInterface(ABC):
    
    @abstractmethod
    def get_answer(self, chat, *args, **kwargs) -> str:
        pass

    @abstractproperty
    def speaker(self):
        pass