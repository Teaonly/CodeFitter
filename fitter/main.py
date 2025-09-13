import yaml
import os
import argparse
from dotenv import load_dotenv
from loguru import logger

from fitter.fitter import CodeFitter, content_from_input

def get_args_from_command():
    ## 解析命令行参数
    parser = argparse.ArgumentParser(description='CodeFitter - 命令行编码智能体')
    parser.add_argument('-i', '--inputs', nargs='*', default=[], help='输入文件')
    parser.add_argument('-o', '--output', required=False, default=None, help='输出文件')

    args = parser.parse_args()
    return args

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

    agent = CodeFitter(config)

    args = get_args_from_command()
    
    #task = content_from_input("输入你任务描述")
    task = "完成 test/simple.py 中的 TODO 的部分"

    agent.fitter(task, args.inputs, args.output)


if __name__ == "__main__":
    main()
