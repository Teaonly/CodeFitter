import os
import json
import uuid
from abc import ABC
from loguru import logger
from fitter.provider.modules_factory import create_provider
from prompt_toolkit import prompt, print_formatted_text, HTML

COLOR = ["ansired", "ansigreen", "skyblue", "seagreen", "violet"]
_color_ = 0


## LLM 工具描述
allTools = [
    {
        "type": "function",
        "function": {
            "name": "ReadFile",
            "description": "Reading file, return text content of file.",
            "strict" : True,
            "parameters": {
                "type": "object",
                "properties": {
                    "file_name": {
                        "description": "file name of reading",
                        "type": "string"
                    }
                },
                "required": ["file_name"],
            }            
        }
    },
    {
        "type": "function",
        "function": {
            "name": "WriteFile",
            "description": "Writing content to file.",
            "strict" : True,
            "parameters": {
                "type": "object",
                "properties": {
                    "file_name": {
                        "description": "file name of output/writing",
                        "type": "string"
                    },
                    "file_content" : {
                        "description": "content of output",
                        "type": "string"
                    }
                },
                "required": ["file_name", "file_content"],
            }            
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ModifyFile",
            "description": "Modify file, output diff content using 'patch format'.",
            "strict" : True,
            "parameters": {
                "type": "object",
                "properties": {
                    "file_name": {
                        "description": "file name of modify",
                        "type": "string"
                    },
                    "diff_content" : {
                        "description": "content of output, using 'patch format'",
                        "type": "string"
                    }
                },
                "required": ["file_name", "diff_content"],
            }            
        }
    }
]

def color_print(text, changeColor=False):
    global _color_, COLOR
    if changeColor:
        _color_ = (_color_ + 1) % len(COLOR)
    
    color = COLOR[_color_]
    print_formatted_text(HTML(f'<{color}>{text}</{color}>'))

def content_from_input(info):
    print_formatted_text(HTML(f'<violet>{info}</violet>'))
    while True:
        try:
            content = prompt(">", vi_mode=True,   multiline=True)
            break
        except EOFError:
            continue

    return content

class CodeFitter(ABC):
    def __init__(self, config):
        self.config = config
        self.llm = create_provider(config)

    def fitter(self, task, inputs, output):
        ## 初始消息队列
        allMessages = [
            {
                'role': "system",
                'content': self.config["SystemPrompt"] 
            },
            {
                'role': "user",
                'content': task,
            }
        ]

        ## 自动加载输入文件内容
        for infile in inputs:
            if not os.path.exists(infile):
                raise Exception(f"无法打开文件：{infile}")
            
            argument = {
                "file_name" : infile
            }
            callid = str(uuid.uuid4())[:6]
            fcall = {
                "type": "function", 
                "id":  callid,
                "function": {
                    "name": "ReadFile",
                    "arguments": json.dumps(argument)
                }
            }
            ## 模拟一次 function call 的 assistant 的消息
            allMessages.append({
                'role': "assistant",
                'content': None,
                'tool_calls': [fcall]
            })
            
            ## 模拟 function call 的结果
            with open(infile, 'r', encoding='utf-8') as f:
                file_content = f.read()
                ## 构造 function call 的返回消息
                call_result = {
                    'role' : 'tool',
                    'tool_call_id': callid,
                    'content': file_content
                }
                allMessages.append(call_result)

        ## 消息已经准备完成
        self.chat_loop(allMessages)
        

    def chat_loop(self, allMessages):
        thinking, talking, fcall = self.llm.response(allMessages, allTools)

        ## 显示LLM响应消息
        if thinking is not None and thinking.strip() != "":
            color_print('>>>>>>思考....', True)
            print(thinking)
            color_print('------------------------\n')

        if talking is not None and talking.strip() != "":
            color_print('>>>>>>输出', True)
            print_formatted_text(HTML(f'<seagreen>输出:</seagreen>'))
            print(talking)
            color_print('------------------------\n')
            
        ## 处理相关的命令
        if fcall["function"]["name"] == "ModifyFile":
            fname = fcall["function"]["name"]
            color_print(f'>>>>>>工具：{fname}', True)
            arguments = fcall["function"]["arguments"]
            arguments = json.loads(arguments)
            color_print(f">>目标文件：{arguments["file_name"]}", True)
            
            ## 彩色打印 git diff/patch 格式的内容
            diff_content = arguments["diff_content"]
            lines = diff_content.split('\n')
            
            for line in lines:
                if line.startswith('+++') or line.startswith('---'):
                    print_formatted_text(HTML(f'<ansicyan>{line}</ansicyan>'))
                elif line.startswith('@@'):
                    print_formatted_text(HTML(f'<ansiyellow>{line}</ansiyellow>'))
                elif line.startswith('+'):
                    print_formatted_text(HTML(f'<ansigreen>{line}</ansigreen>'))
                elif line.startswith('-'):
                    print_formatted_text(HTML(f'<ansired>{line}</ansired>'))
                else:
                    print(line)

            color_print('------------------------\n')
            

        uinput = content_from_input("用户输入")

