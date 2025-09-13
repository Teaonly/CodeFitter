from abc import ABC, abstractmethod
from loguru import logger

class LLMProviderBase(ABC):
    @abstractmethod
    def response_with_functions(self, dialogue, functions=None):
        """
        Returns: generator that yields either text tokens or a special function call token
        """
        pass
        
