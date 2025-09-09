# 课程材料RAG系统

source: https://github.com/https-deeplearning-ai/starting-ragchatbot-codebase

一个检索增强生成（RAG）系统，旨在使用语义搜索和AI驱动的响应来回答关于课程材料的问题。

## 概述

这是一个全栈Web应用程序，使用户能够查询课程材料并获得智能的、上下文感知的响应。它使用ChromaDB进行向量存储，使用Anthropic的Claude进行AI生成，并提供Web界面进行交互。


## 先决条件

- Python 3.13或更高版本
- uv（Python包管理器）
- Anthropic API密钥（用于Claude AI）
- **Windows用户**：使用Git Bash运行应用程序命令 - [下载Git for Windows](https://git-scm.com/downloads/win)

## 安装

1. **安装uv**（如果尚未安装）
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **安装Python依赖**
   ```bash
   uv sync
   ```

3. **设置环境变量**
   
   在根目录创建`.env`文件：
   ```bash
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

## 运行应用程序

### 快速启动

使用提供的shell脚本：
```bash
chmod +x run.sh
./run.sh
```

### 手动启动

```bash
cd backend
uv run uvicorn app:app --reload --port 8000
```

应用程序可通过以下地址访问：
- Web界面：`http://localhost:8000`
- API文档：`http://localhost:8000/docs`


