import yaml
import os
import sys

def main():
    ## 加载配置文件
    code_path = os.path.dirname( os.path.abspath(__file__) )
    lore_path = os.path.join(code_path, "lore/write.yaml")
    with open(lore_path, "r") as file:
        lore = yaml.safe_load(file)
    
    ## 解析命令行，支持分支命令
    ## TODO 支持 -i [[file1] [file2]] -o [file1]
    

if __name__ == "__main__":
    main()
