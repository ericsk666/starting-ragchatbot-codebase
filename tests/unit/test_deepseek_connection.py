#!/usr/bin/env python3
"""
DeepSeek API连通性测试脚本
测试基础对话功能，验证API密钥和端点是否正常工作
"""

import os
import sys
import json

# 测试配置
API_KEY = os.getenv("OPENAI_API_KEY", "")
BASE_URL = "https://llm.chutes.ai/v1"
MODEL = "deepseek-ai/DeepSeek-R1"

def test_basic_chat():
    """测试基础对话功能"""
    print("=" * 60)
    print("测试1: 基础对话功能")
    print("-" * 60)
    
    try:
        from openai import OpenAI
        
        client = OpenAI(
            base_url=BASE_URL,
            api_key=API_KEY
        )
        
        print(f"连接到: {BASE_URL}")
        print(f"使用模型: {MODEL}")
        print("发送测试消息...")
        
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "你是一个有帮助的AI助手"},
                {"role": "user", "content": "你好，请简单介绍一下什么是RAG系统"}
            ],
            temperature=0,
            max_tokens=200
        )
        
        print("\n[PASS] API连接成功！")
        print("\n响应内容:")
        print("-" * 40)
        print(response.choices[0].message.content)
        print("-" * 40)
        
        # 打印响应元数据
        print("\n响应元数据:")
        print(f"- Model: {response.model}")
        print(f"- Usage: {response.usage}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        return False

def test_function_calling():
    """测试工具调用功能"""
    print("\n" + "=" * 60)
    print("测试2: 工具调用功能")
    print("-" * 60)
    
    try:
        from openai import OpenAI
        
        client = OpenAI(
            base_url=BASE_URL,
            api_key=API_KEY
        )
        
        # 定义测试工具
        tools = [{
            "type": "function",
            "function": {
                "name": "search_course_content",
                "description": "搜索课程内容",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "搜索查询"
                        },
                        "course_name": {
                            "type": "string",
                            "description": "课程名称"
                        }
                    },
                    "required": ["query"]
                }
            }
        }]
        
        print("发送带工具的测试消息...")
        
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "user", "content": "搜索关于Python编程的课程"}
            ],
            tools=tools,
            tool_choice="auto"
        )
        
        # 检查是否有工具调用
        if hasattr(response.choices[0].message, 'tool_calls') and response.choices[0].message.tool_calls:
            print("\n✅ 工具调用功能支持！")
            print("\n工具调用详情:")
            for tool_call in response.choices[0].message.tool_calls:
                print(f"- 工具名称: {tool_call.function.name}")
                print(f"- 参数: {tool_call.function.arguments}")
            return True
        else:
            print("\n⚠️ 模型没有调用工具，可能需要调整提示词")
            print(f"响应: {response.choices[0].message.content}")
            return False
            
    except Exception as e:
        print(f"\n❌ 工具调用测试失败: {str(e)}")
        return False

def test_context_handling():
    """测试上下文处理能力"""
    print("\n" + "=" * 60)
    print("测试3: 上下文处理")
    print("-" * 60)
    
    try:
        from openai import OpenAI
        
        client = OpenAI(
            base_url=BASE_URL,
            api_key=API_KEY
        )
        
        # 模拟多轮对话
        messages = [
            {"role": "system", "content": "你是课程材料助手"},
            {"role": "user", "content": "我想了解MCP课程"},
            {"role": "assistant", "content": "MCP（Model Context Protocol）是一个关于模型上下文协议的课程，它介绍了如何有效地管理和使用AI模型的上下文。"},
            {"role": "user", "content": "它主要包含哪些内容？"}
        ]
        
        print("测试多轮对话上下文...")
        
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0,
            max_tokens=200
        )
        
        print("\n✅ 上下文处理成功！")
        print("\n响应内容:")
        print("-" * 40)
        print(response.choices[0].message.content)
        print("-" * 40)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 上下文测试失败: {str(e)}")
        return False

def main():
    """运行所有测试"""
    print("\n" + "开始测试DeepSeek API连接" + "\n")
    print(f"API端点: {BASE_URL}")
    print(f"模型: {MODEL}")
    print("=" * 60)
    
    # 检查是否安装了openai库
    try:
        import openai
        print(f"✅ OpenAI SDK已安装 (版本: {openai.__version__})")
    except ImportError:
        print("❌ 未安装OpenAI SDK")
        print("请运行: pip install openai")
        sys.exit(1)
    
    # 运行测试
    results = []
    
    # 测试1：基础对话
    results.append(("基础对话", test_basic_chat()))
    
    # 测试2：工具调用
    results.append(("工具调用", test_function_calling()))
    
    # 测试3：上下文处理
    results.append(("上下文处理", test_context_handling()))
    
    # 输出测试总结
    print("\n" + "=" * 60)
    print("📊 测试总结")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
    
    # 判断是否所有测试都通过
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 所有测试通过！DeepSeek API可以正常使用。")
        print("\n下一步：")
        print("1. 配置环境变量")
        print("2. 修改项目代码")
        print("3. 进行集成测试")
    else:
        print("\n⚠️ 部分测试未通过，请检查问题后再继续。")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)