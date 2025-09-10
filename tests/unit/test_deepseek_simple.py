#!/usr/bin/env python3
"""
DeepSeek API简单测试脚本
"""

import os
import sys

# 测试配置
API_KEY = os.getenv("OPENAI_API_KEY", "")
BASE_URL = "https://llm.chutes.ai/v1"
MODEL = "deepseek-ai/DeepSeek-R1"

print("="*60)
print("DeepSeek API Connection Test")
print("="*60)
print(f"Endpoint: {BASE_URL}")
print(f"Model: {MODEL}")
print("-"*60)

# 检查OpenAI库
try:
    from openai import OpenAI
    print("[OK] OpenAI SDK installed")
except ImportError:
    print("[ERROR] OpenAI SDK not installed")
    print("Please run: pip install openai")
    sys.exit(1)

# 测试API连接
try:
    print("\n[TEST] Basic Chat...")
    
    client = OpenAI(
        base_url=BASE_URL,
        api_key=API_KEY
    )
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, please explain what is RAG in one sentence."}
        ],
        temperature=0,
        max_tokens=100
    )
    
    print("[SUCCESS] API connection successful!")
    print("\nResponse:")
    print("-"*40)
    print(response.choices[0].message.content)
    print("-"*40)
    
    print(f"\nModel used: {response.model}")
    print(f"Tokens used: {response.usage}")
    
except Exception as e:
    print(f"[ERROR] Test failed: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("Test completed successfully!")
print("API is ready to use.")
print("="*60)