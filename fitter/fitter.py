import os
import sys
import json
import uuid
import tempfile
import html
from io import StringIO
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

def dump_diff_content(diff_content):
    ## 彩色打印 git diff/patch 格式的内容
    print_formatted_text(HTML(f'<violet>==</violet>'))
    lines = diff_content.split('\n')
    for line in lines:
        ## 将 line 字符串中的 HTML 特殊字符转义，避免错误打印
        escaped_line = html.escape(line)
        
        if line.startswith('+++') or line.startswith('---'):
            print_formatted_text(HTML(f'<ansicyan>{escaped_line}</ansicyan>'))
        elif line.startswith('@@'):
            print_formatted_text(HTML(f'<ansiyellow>{escaped_line}</ansiyellow>'))
        elif line.startswith('+'):
            print_formatted_text(HTML(f'<ansigreen>{escaped_line}</ansigreen>'))
        elif line.startswith('-'):
            print_formatted_text(HTML(f'<ansired>{escaped_line}</ansired>'))
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
    """解析 diff_content 格式，实现对 file_path 修改，返回 (success, error_message)"""
    try:
        # 确保文件存在
        if not os.path.exists(file_path):
            return False, f"目标文件不存在: {file_path}"
        
        # 读取原文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            original_lines = f.readlines()
        
        # 解析diff内容
        diff_lines = diff_content.split('\n')
        new_lines = []
        i = 0
        original_line_num = 0
        in_hunk = False
        
        while i < len(diff_lines):
            line = diff_lines[i]
            
            # 跳过文件头信息
            if line.startswith('+++') or line.startswith('---'):
                i += 1
                continue
            
            # 处理hunk头部 (@@ line)
            if line.startswith('@@'):
                # 格式: @@ -original_start,original_count +new_start,new_count @@
                parts = line.split(' ')
                if len(parts) >= 3:
                    original_part = parts[1]
                    if ',' in original_part:
                        original_start = int(original_part[1:].split(',')[0])
                    else:
                        original_start = int(original_part[1:])
                    original_line_num = original_start - 1  # 转换为0-based索引
                in_hunk = True
                i += 1
                continue
            
            # 处理实际的修改内容
            if in_hunk:
                if line.startswith('+'):
                    # 新增行
                    new_lines.append(line[1:] + '\n')
                    i += 1
                elif line.startswith('-'):
                    # 删除行 - 跳过原文件中对应的行
                    if original_line_num < len(original_lines):
                        original_line_num += 1
                    i += 1
                elif line.startswith(' '):
                    # 未修改的行
                    if original_line_num < len(original_lines):
                        new_lines.append(original_lines[original_line_num])
                        original_line_num += 1
                    i += 1
                elif line.strip() == '':
                    # 空行
                    new_lines.append('\n')
                    i += 1
                else:
                    # 未知格式，跳过
                    i += 1
            else:
                i += 1
        
        # 如果没有hunk信息，简单替换整个文件内容
        if not in_hunk:
            # 尝试提取diff中的实际内容
            content_start = -1
            for j, line in enumerate(diff_lines):
                if line.startswith('+') and not line.startswith('+++'):
                    content_start = j
                    break
            
            if content_start >= 0:
                # 提取所有以+开头的内容（除了文件头）
                new_lines = []
                for line in diff_lines[content_start:]:
                    if line.startswith('+') and not line.startswith('+++'):
                        new_lines.append(line[1:] + '\n')
            else:
                return False, "无法解析diff格式"
        
        # 写入修改后的内容
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        return True, None
        
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
            'tool_calls': [fcall] if fcall is not None else None
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
        
        ## 如果没有工具调用
        if fcall is None:
            confirm = confirm_from_input(f"模型没有发起工具调用，是否退出(y/n)")
            if confirm:
                sys.exit(0)
            return

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
                    response = f"用户认可，并且确认已经完成文件 {arguments["file_name"]} 的修改。"
                else:
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

    