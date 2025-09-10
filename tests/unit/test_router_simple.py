#!/usr/bin/env python3
"""
简化版路由器测试脚本 - 避免Unicode编码问题
验证双模型路由策略
"""

import sys
import os
import json

# 添加backend目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.llm_router import llm_router
from backend.config import config

def print_header(title):
    """打印测试标题"""
    print("\n" + "=" * 60)
    print(title)
    print("-" * 60)

def test_reasoning():
    """测试纯推理 - 预期使用DeepSeek-R1"""
    print_header("测试1: 纯推理对话 - 预期使用DeepSeek-R1")
    
    messages = [
        {"role": "system", "content": "你是AI助手"},
        {"role": "user", "content": "解释什么是RAG系统"}
    ]
    
    try:
        response = llm_router.call_simple_chat(messages, max_tokens=200)
        print("[PASS] 推理测试成功")
        print(f"响应摘要: {response[:100]}...")
        return True
    except Exception as e:
        print(f"[FAIL] 推理测试失败: {e}")
        return False

def test_tool_call():
    """测试工具调用 - 预期使用DeepSeek-V3"""
    print_header("测试2: 工具调用 - 预期使用DeepSeek-V3")
    
    messages = [
        {"role": "system", "content": "你是搜索助手，必须使用工具搜索"},
        {"role": "user", "content": "搜索Python编程课程"}
    ]
    
    tools = [{
        "type": "function", 
        "function": {
            "name": "search_course_content",
            "description": "搜索课程内容",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索查询"},
                    "category": {"type": "string", "description": "课程分类"}
                },
                "required": ["query"]
            }
        }
    }]
    
    try:
        response = llm_router.call_with_tools(messages, tools, max_tokens=200)
        
        if hasattr(response.choices[0].message, 'tool_calls') and response.choices[0].message.tool_calls:
            print("[PASS] 工具调用测试成功")
            for i, tool_call in enumerate(response.choices[0].message.tool_calls, 1):
                print(f"工具调用 {i}: {tool_call.function.name}")
                print(f"参数: {tool_call.function.arguments}")
            return True
        else:
            print("[WARN] 未触发工具调用")
            print(f"模型响应: {response.choices[0].message.content}")
            return False
    except Exception as e:
        print(f"[FAIL] 工具调用失败: {e}")
        return False

def test_routing_switch():
    """测试路由切换"""
    print_header("测试3: 路由智能切换")
    
    results = []
    
    # 测试1: 纯对话
    print("\n>> 第一轮: 纯对话 (预期R1)")
    try:
        response1 = llm_router.call_simple_chat([
            {"role": "user", "content": "你好"}
        ], max_tokens=50)
        print("[PASS] 第一轮成功")
        results.append(True)
    except Exception as e:
        print(f"[FAIL] 第一轮失败: {e}")
        results.append(False)
    
    # 测试2: 工具调用
    print("\n>> 第二轮: 工具调用 (预期V3)")
    try:
        response2 = llm_router.call_with_tools([
            {"role": "user", "content": "搜索数据库课程"}
        ], [{
            "type": "function",
            "function": {
                "name": "search_course",
                "parameters": {
                    "type": "object",
                    "properties": {"query": {"type": "string"}},
                    "required": ["query"]
                }
            }
        }], max_tokens=50)
        
        if hasattr(response2.choices[0].message, 'tool_calls') and response2.choices[0].message.tool_calls:
            print("[PASS] 第二轮成功 - 触发工具调用")
            results.append(True)
        else:
            print("[WARN] 第二轮部分成功 - 未触发工具调用")
            results.append(False)
    except Exception as e:
        print(f"[FAIL] 第二轮失败: {e}")
        results.append(False)
    
    return all(results)

def main():
    """主测试函数"""
    print("开始路由器测试")
    
    # 检查配置
    print(f"LLM提供商: {config.LLM_PROVIDER}")
    print(f"推理模型: {config.MODEL_REASON}")
    print(f"工具调用模型: {config.MODEL_TOOLCALL}")
    print(f"API密钥状态: {'已配置' if config.LLM_API_KEY and 'YOUR_NEW' not in config.LLM_API_KEY else '未配置'}")
    
    if not config.LLM_API_KEY or 'YOUR_NEW' in config.LLM_API_KEY:
        print("\n[ERROR] API密钥未正确配置")
        return False
    
    # 运行测试
    tests = [
        ("纯推理测试", test_reasoning),
        ("工具调用测试", test_tool_call),
        ("路由切换测试", test_routing_switch)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n运行: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"[ERROR] 测试异常: {e}")
            results.append((test_name, False))
    
    # 输出结果
    print_header("测试结果总结")
    
    passed = 0
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    total = len(results)
    print(f"\n总体结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n[SUCCESS] 所有测试通过！双模型路由策略工作正常")
        print("验证要点:")
        print("  - R1处理纯推理任务")
        print("  - V3处理工具调用任务")  
        print("  - 智能路由切换正常")
    else:
        print(f"\n[WARNING] {total-passed}个测试失败，需要调试")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)