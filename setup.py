from setuptools import setup, find_packages

setup(
    name="agenkit",
    version="0.1.0",
    description="HITL SDK for AI Agent Governance and Harness Engineering",
    long_description="""AgenKit - AI Agent 治理与驾驭工程

未来有价值的不是"会用 AI"，而是"会驾驭 AI"。

本项目旨在调研和落地 Harness Engineering（驾驭工程）与 AI Agent 治理相关的技术方案。

核心功能：
- 执行监控与日志记录
- 安全护栏与风险评估
- 人类干预机制
- 执行历史与违规记录
""",
    long_description_content_type="text/markdown",
    author="AgenGit Team",
    author_email="team@agengit.com",
    url="https://github.com/chatabc/AgenGit",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[],
    extras_require={
        "dev": [
            "pytest",
            "black",
            "flake8",
        ],
    },
)