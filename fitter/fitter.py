import os
import sys
import json
import uuid
import tempfile
from io import StringIO
from abc import ABC
from loguru import logger
from patch_ng import fromstring
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

def dump_diff_content(diff_content):
    ## 彩色打印 git diff/patch 格式的内容
    print_formatted_text(HTML(f'<violet>==</violet>'))
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
    
    print_formatted_text(HTML(f'<violet>==================</violet>\n'))

def content_from_input(info):
    print_formatted_text(HTML(f'<violet>{info}</violet>'))
    while True:
        try:
            content = prompt(">", vi_mode=True,   multiline=True)
            break
        except EOFError:
            continue

    return content

def confirm_from_input(info):
    color_print(info)
    while True:
        try:
            confirm = prompt(">").strip().lower()
            if confirm in ['y', 'yes']:
                return True
            elif confirm in ['n', 'no']:
                return False
            else:
                color_print('请输入 y/yes 或 n/no')
        except EOFError:
            continue

def apply_patch(file_path, diff_content):
    """使用patch-ng库应用patch/diff格式的内容到目标文件"""
    try:
        # 确保文件存在
        if not os.path.exists(file_path):
            return False, f"目标文件不存在: {file_path}"
        
        # 创建临时目录用于补丁应用
        with tempfile.TemporaryDirectory() as temp_dir:
            # 复制原文件到临时目录
            import shutil
            temp_file_path = os.path.join(temp_dir, os.path.basename(file_path))
            shutil.copy2(file_path, temp_file_path)
            
            # 切换到临时目录
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # 使用patch-ng解析并应用补丁
                patch_set = fromstring(diff_content.encode('utf-8'))
                if not patch_set:
                    return False, "无法解析patch内容"
                
                # 应用补丁
                result = patch_set.apply(strip=0)
                if not result:
                    return False, "应用patch失败"
                
                # 将修改后的文件复制回原位置
                shutil.copy2(temp_file_path, file_path)
                return True, None

            finally:
                # 恢复原始工作目录
                os.chdir(original_cwd)
                
    except Exception as e:
        return False, f"应用patch失败: {e}"



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
        print("\n\n 调用模型...")
        thinking, talking, fcall = self.llm.response(allMessages, allTools)

        new_message = {
            'role': "assistant",
            'content': talking,
            'reasoning_content': thinking,
            'tool_calls': [fcall]
        }
        


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
            try:
                fname = fcall["function"]["name"]
                callid = fcall["id"]
                color_print(f'>>>>>>工具：{fname}', True)
                
                arguments = fcall["function"]["arguments"]            
                arguments = json.loads(arguments)
                diff_content = arguments["diff_content"]
                dump_diff_content(diff_content)
            
            except Exception as e:
                color_print(f'解析工具失败{e}, 重新调用')
                return self.chat_loop(allMessages)
            
            confirm = confirm_from_input(f"是否确认覆盖修改 {arguments["file_name"]}？(y/n)")
            if confirm == True:
                ## 根据获得 path/diff 字符串，修改目标文件
                success, msg = apply_patch(arguments["file_name"], diff_content)
                if success :
                    color_print(f'已经完成文件: {arguments["file_name"]}的修改，退出程序！')
                    sys.exit(0)
                    return
                
                response = f"修改文件失败：{msg}，重新调用模型！"
                color_print(response)
                call_result = {
                    'role' : 'tool',
                    'tool_call_id': callid,
                    'content': response
                }
                allMessages.append(new_message)
                allMessages.append(call_result)
                return self.chat_loop(allMessages)


            ## 用户输入反馈，继续下一轮次调用
            response = content_from_input("输入反馈意见：")
            response = f"用户拒绝了修改，反馈如下：{response}"
            call_result = {
                'role' : 'tool',
                'tool_call_id': callid,
                'content': response
            }
            allMessages.append(new_message)
            allMessages.append(call_result)
            return self.chat_loop(allMessages)

    