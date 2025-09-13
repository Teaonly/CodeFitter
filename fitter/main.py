import yaml
import os
import argparse
from dotenv import load_dotenv
from loguru import logger

def main():
    ## 初始化logger - 仅通知用户，不做记录
    logger.remove()
    logger.add(lambda msg: print(msg, end=''), format='<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}')
    
    ## 加载环境变量
    load_dotenv()
    
    ## 加载配置文件
    code_path = os.path.dirname( os.path.abspath(__file__) )
    lore_path = os.path.join(code_path, "lore/write.yaml")
    with open(lore_path, "r") as file:
        lore = yaml.safe_load(file)

    ## 解析命令行参数
    parser = argparse.ArgumentParser(description='CodeFitter - 命令行编码智能体')
    parser.add_argument('command', choices=['compose', 'compact'], help='执行命令')
    parser.add_argument('-i', '--input', nargs='*', default=[], help='输入文件')
    parser.add_argument('-o', '--output', required=True, help='输出文件')

    args = parser.parse_args()

    if args.command == 'compose':
        logger.info(f"执行 compose 命令")
        logger.info(f"输入文件: {args.input}")
        logger.info(f"输出文件: {args.output}")
        # TODO: 实现实际的文件组合逻辑

    elif args.command == 'compact':
        logger.info(f"执行 compact 命令")
        logger.info(f"输入文件: {args.input}")
        logger.info(f"输出文件: {args.output}")
        # TODO: 实现实际的文件压缩逻辑

if __name__ == "__main__":
    main()
