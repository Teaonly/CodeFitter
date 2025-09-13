import yaml
import os
import argparse
from dotenv import load_dotenv
from loguru import logger
from prompt_toolkit import prompt, print_formatted_text, HTML

from fitter.provider.modules_factory import create_provider


def get_task_from_input():
    print_formatted_text(HTML('<violet>输入你任务描述，如完成某文件的中TODO, Escape followed by Enter 结束！</violet>'))
    while True:
        try:
            task = prompt(">", vi_mode=True,   multiline=True)
            break
        except EOFError:
            continue

    return task

def get_args_from_command():
    ## 解析命令行参数
    parser = argparse.ArgumentParser(description='CodeFitter - 命令行编码智能体')
    parser.add_argument('-i', '--input', nargs='*', default=[], help='输入文件')
    parser.add_argument('-o', '--output', required=False, default=None, help='输出文件')

    args = parser.parse_args()
    return args

def chat(config):
    messages = [
        {
            'role': "system",
            'content': '你是一个小助手！'    
        },
        {
            'role': "user",
            'content': '介绍一下 Python 编程语言！'
        }
    ]
    
    llm = create_provider(config)

    response = llm.response_with_functions(messages)
    for token, fcall in response:
        print(token)

    

def main():
    ## 初始化logger - 仅通知用户，不做记录
    logger.remove()
    logger.add(lambda msg: print(msg, end=''), format='<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}')
    
    ## 加载环境变量
    load_dotenv()
    
    ## 加载配置文件
    code_path = os.path.dirname( os.path.abspath(__file__) )
    lore_path = os.path.join(code_path, "config.yaml")
    with open(lore_path, "r") as file:
        config = yaml.safe_load(file)

    args = get_args_from_command()
    
    #task = get_task_from_input()
    
    chat(config)
    
    
    

if __name__ == "__main__":
    main()
