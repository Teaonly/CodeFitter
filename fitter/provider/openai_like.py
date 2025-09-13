import json
import os
from httpx import Client
from loguru import logger

from provider.base import LLMProviderBase

class LLMProvider(LLMProviderBase):
    def __init__(self, config):
        self.model_name = config.get("model_name")
        self.base_url = config.get("base_url")
        api_key_env = config.get("api_key")
        self.api_key = os.getenv(api_key_env)
        if self.api_key == None:
            raise Exception("从环境变量中，无法获取 API_KEY")
        self.client = Client()

    def _build_request(self, dialogue, functions = None):
        url = self.base_url + "/chat/completions"
        payload =  {
            "model": self.model_name,
            "messages" : dialogue,
            "stream": True,
            "enable_thinking": False,
            "temperature": 0.2,
            "response_format": {"type": "text"},
        };
        headers = {
            "Authorization": "Bearer " + self.api_key, # type: ignore
            "Content-Type": "application/json"
        };

        if functions != None :
            payload["tools"] = functions;

        return url, payload, headers

    def response_with_functions(self, dialogue, functions=None):
        firstFlag = True
        try:
            url, payload, headers = self._build_request(dialogue, functions);
            with self.client.stream('POST', url , headers = headers, json = payload, timeout=5.0 ) as response:
                if response.status_code == 400:
                    response.read()
                    logger.error(f"{response.json()}")
                for line in response.iter_lines():
                    lj = line[6:];
                    if lj.startswith("{"):
                        lj = json.loads(lj)
                        token = None
                        if "content" in lj["choices"][0]["delta"]:
                            token = lj["choices"][0]["delta"]["content"]

                        fcall = None
                        if "tool_calls" in lj["choices"][0]["delta"]:
                            fcall = lj["choices"][0]["delta"]["tool_calls"]
                        
                        if (token != None) or (fcall != None):
                            firstFlag = False
                            yield token, fcall

        except Exception as e:
            logger.error(f"Error in response generation: {e}")
        
        if firstFlag :
            yield None, None
            

