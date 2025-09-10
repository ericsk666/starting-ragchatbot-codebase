#!/usr/bin/env python3
"""
DeepSeek function calling问题排查脚本
"""

import json
from openai import OpenAI

# 配置
API_KEY = os.getenv("OPENAI_API_KEY", "")
BASE_URL = "https://llm.chutes.ai/v1"
MODEL = "deepseek-ai/DeepSeek-R1"

def test_1_minimal_function():
    """测试1: 最简单的工具定义"""
    print("=" * 60)
    print("测试1: 最简单的工具定义")
    print("-" * 60)
    
    client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
    
    tools = [{
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取天气信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名称"}
                },
                "required": ["city"]
            }
        }
    }]
    
    try:
        print("发送请求...")
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": "北京的天气怎么样？"}],
            tools=tools,
            tool_choice="auto",
            temperature=0
        )
        
        print("[SUCCESS] 请求成功")
        print("响应:", response.choices[0].message.content)
        
        if hasattr(response.choices[0].message, 'tool_calls') and response.choices[0].message.tool_calls:
            print("工具调用:", response.choices[0].message.tool_calls)
            return True
        else:
            print("没有工具调用")
            return False
            
    except Exception as e:
        print(f"[ERROR] 请求失败: {e}")
        return False

def test_2_without_tool_choice():
    """测试2: 不指定tool_choice"""
    print("\n" + "=" * 60)
    print("测试2: 不指定tool_choice")
    print("-" * 60)
    
    client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
    
    tools = [{
        "type": "function",
        "function": {
            "name": "search_info",
            "description": "搜索信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索查询"}
                },
                "required": ["query"]
            }
        }
    }]
    
    try:
        print("发送请求...")
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": "搜索Python编程相关信息"}],
            tools=tools,
            temperature=0
        )
        
        print("[SUCCESS] 请求成功")
        print("响应:", response.choices[0].message.content)
        
        if hasattr(response.choices[0].message, 'tool_calls') and response.choices[0].message.tool_calls:
            print("工具调用:", response.choices[0].message.tool_calls)
            return True
        else:
            print("没有工具调用")
            return False
            
    except Exception as e:
        print(f"[ERROR] 请求失败: {e}")
        return False

def test_3_force_tool_call():
    """测试3: 强制工具调用"""
    print("\n" + "=" * 60)
    print("测试3: 强制工具调用")
    print("-" * 60)
    
    client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
    
    tools = [{
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "执行数学计算",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "数学表达式"}
                },
                "required": ["expression"]
            }
        }
    }]
    
    try:
        print("发送请求...")
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": "计算 2 + 3"}],
            tools=tools,
            tool_choice={"type": "function", "function": {"name": "calculate"}},
            temperature=0
        )
        
        print("[SUCCESS] 请求成功")
        print("响应:", response.choices[0].message.content)
        
        if hasattr(response.choices[0].message, 'tool_calls') and response.choices[0].message.tool_calls:
            print("工具调用:", response.choices[0].message.tool_calls)
            return True
        else:
            print("没有工具调用")
            return False
            
    except Exception as e:
        print(f"[ERROR] 请求失败: {e}")
        return False

def test_4_check_model_info():
    """测试4: 检查模型信息"""
    print("\n" + "=" * 60)
    print("测试4: 检查模型信息和支持的功能")
    print("-" * 60)
    
    client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
    
    try:
        print("检查可用模型...")
        models = client.models.list()
        print("可用模型:")
        for model in models.data:
            print(f"- {model.id}")
            
        print(f"\n当前使用模型: {MODEL}")
        return True
        
    except Exception as e:
        print(f"[ERROR] 检查模型失败: {e}")
        return False

def test_5_simple_request():
    """测试5: 不带工具的简单请求作为对比"""
    print("\n" + "=" * 60)
    print("测试5: 简单请求对比")
    print("-" * 60)
    
    client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
    
    try:
        print("发送简单请求...")
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": "你好，请介绍一下自己"}],
            temperature=0,
            max_tokens=100
        )
        
        print("[SUCCESS] 简单请求成功")
        print("响应:", response.choices[0].message.content)
        print("模型:", response.model)
        print("使用量:", response.usage)
        return True
        
    except Exception as e:
        print(f"[ERROR] 简单请求失败: {e}")
        return False

def main():
    """运行所有排查测试"""
    print("开始function calling问题排查")
    print("API端点:", BASE_URL)
    print("模型:", MODEL)
    
    tests = [
        ("最简单工具定义", test_1_minimal_function),
        ("不指定tool_choice", test_2_without_tool_choice), 
        ("强制工具调用", test_3_force_tool_call),
        ("检查模型信息", test_4_check_model_info),
        ("简单请求对比", test_5_simple_request)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"测试 {test_name} 异常: {e}")
            results.append((test_name, False))
    
    # 输出总结
    print("\n" + "=" * 60)
    print("排查结果总结")
    print("=" * 60)
    
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{test_name}: {status}")
    
    # 分析结果
    print("\n" + "-" * 60)
    print("问题分析:")
    
    simple_works = results[-1][1]  # 简单请求是否成功
    any_tool_works = any(result for name, result in results[:-2])  # 任何工具调用是否成功
    
    if simple_works and not any_tool_works:
        print("- 基础API工作正常")
        print("- 所有工具调用都失败")
        print("- 可能是llm.chutes.ai对DeepSeek-R1的function calling支持问题")
        print("- 建议: 联系服务提供商或考虑替代方案")
    elif not simple_works:
        print("- 基础API都有问题")
        print("- 需要检查网络连接和API密钥")
    elif any_tool_works:
        print("- 部分工具调用成功")
        print("- 需要分析成功和失败的差异")

if __name__ == "__main__":
    main()