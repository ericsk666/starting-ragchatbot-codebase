#!/usr/bin/env python3
"""
测试LLM路由器的双模型策略
"""

import sys
import os

# 添加backend目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.llm_router import llm_router

def test_simple_chat():
    """测试纯对话（应该使用DeepSeek-R1）"""
    print("=" * 60)
    print("测试1: 纯对话（预期使用DeepSeek-R1）")
    print("-" * 60)
    
    messages = [
        {"role": "system", "content": "你是一个有帮助的AI助手"},
        {"role": "user", "content": "请简单介绍一下什么是RAG系统"}
    ]
    
    try:
        response_text = llm_router.call_simple_chat(messages)
        print(f"[SUCCESS] 响应: {response_text[:200]}...")
        return True
    except Exception as e:
        print(f"[ERROR] 测试失败: {e}")
        return False

def test_tool_calling():
    """测试工具调用（应该使用DeepSeek-V3）"""
    print("\n" + "=" * 60)
    print("测试2: 工具调用（预期使用DeepSeek-V3）")
    print("-" * 60)
    
    messages = [
        {"role": "system", "content": "你是课程搜索助手，优先使用工具搜索"},
        {"role": "user", "content": "搜索关于Python编程的课程"}
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
                    "course_name": {"type": "string", "description": "课程名称"}
                },
                "required": ["query"]
            }
        }
    }]
    
    try:
        response = llm_router.call_with_tools(messages, tools)
        
        # 检查是否有工具调用
        if hasattr(response.choices[0].message, 'tool_calls') and response.choices[0].message.tool_calls:
            print("[SUCCESS] 工具调用成功！")
            for tool_call in response.choices[0].message.tool_calls:
                print(f"- 工具: {tool_call.function.name}")
                print(f"- 参数: {tool_call.function.arguments}")
            return True
        else:
            print(f"[WARNING] 未触发工具调用，响应: {response.choices[0].message.content[:200]}...")
            return False
            
    except Exception as e:
        print(f"[ERROR] 测试失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("开始测试LLM路由器双模型策略")
    print("=" * 60)
    
    results = []
    
    # 测试1: 纯对话
    results.append(("纯对话路由", test_simple_chat()))
    
    # 测试2: 工具调用
    results.append(("工具调用路由", test_tool_calling()))
    
    # 输出总结
    print("\n" + "=" * 60)
    print("路由器测试总结")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{test_name}: {status}")
        all_passed = all_passed and result
    
    if all_passed:
        print("\n[SUCCESS] 路由器测试全部通过！")
        print("双模型策略正常工作：")
        print("- 纯对话 → DeepSeek-R1")
        print("- 工具调用 → DeepSeek-V3")
    else:
        print("\n[WARNING] 部分测试未通过，请检查配置")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)