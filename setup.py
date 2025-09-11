# setup.py
from setuptools import setup, find_packages

setup(
    name="fitter",  # 包名
    version="0.1.0",  # 版本号
    packages=find_packages(),  # 自动发现包
    install_requires=[],  # 依赖项（可根据需要添加）
    entry_points={
        "console_scripts": [
            "fitter=main:main",  # 全局命令名=模块.函数
        ],
    },
    author="Zhou Chang",
    author_email="achang.zhou@gmail.com",
    description="A simple CLI code agent tool",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Teaonly/CodeFitter",  # 项目主页（可选）
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
)
