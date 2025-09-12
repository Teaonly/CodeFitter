from abc import ABC, abstractmethod
from loguru import logger

class LLMProviderBase(ABC):
    def response_no_stream(self, system_prompt, user_prompt):
        try:
            # 构造对话格式
            dialogue = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            result = ""
            for part in self.response(dialogue):
                result += part
            return result

        except Exception as e:
            logger.error(f"Error in Ollama response generation: {e}")
            return "【LLM服务响应异常】"

    @abstractmethod
    def response(self, dialogue):
        """
        Returns: generator that yields either text tokens
        """
        pass

    @abstractmethod
    def response_with_functions(self, dialogue, functions=None):
        """
        Returns: generator that yields either text tokens or a special function call token
        """
        pass
        
