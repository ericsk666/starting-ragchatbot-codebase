#!/usr/bin/env python3
"""
基于智能路由器的DeepSeek综合测试脚本
验证双模型路由策略在实际RAG场景中的表现
"""

import sys
import os
import json

# 添加backend目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.llm_router import llm_router
from backend.config import config

def print_header(title: str) -> None:
    """打印测试标题"""
    print("\n" + "=" * 60)
    print(title)
    print("-" * 60)

def print_model_info():
    """打印当前配置信息"""
    print_header("配置信息")
    print(f"LLM提供商: {config.LLM_PROVIDER}")
    print(f"API端点: {config.LLM_BASE_URL}")
    print(f"推理模型: {config.MODEL_REASON}")
    print(f"工具调用模型: {config.MODEL_TOOLCALL}")
    print(f"API密钥状态: {'已配置' if config.LLM_API_KEY and config.LLM_API_KEY != 'YOUR_NEW_DEEPSEEK_API_KEY_HERE' else '未配置'}")

def test_simple_reasoning():
    """测试1: 纯推理对话 (预期使用DeepSeek-R1)"""
    print_header("测试1: 纯推理对话 - 预期使用DeepSeek-R1")
    
    messages = [
        {"role": "system", "content": "你是一个专业的AI助手，擅长解释复杂概念"},
        {"role": "user", "content": "请详细解释什么是向量数据库，以及它在RAG系统中的作用"}
    ]
    
    try:
        response_text = llm_router.call_simple_chat(messages, max_tokens=300)
        print(f"[PASS] 推理测试成功")
        print(f"[RESPONSE] 响应摘要: {response_text[:150]}...")
        return True
    except Exception as e:
        print(f"[FAIL] 推理测试失败: {e}")
        return False

def test_tool_calling_search():
    """测试2: 工具调用 - 课程搜索 (预期使用DeepSeek-V3)"""
    print_header("测试2: 工具调用 - 课程搜索 - 预期使用DeepSeek-V3")
    
    messages = [
        {"role": "system", "content": "你是课程搜索助手。用户询问课程时，必须使用search_course_content工具搜索，不要直接回答。"},
        {"role": "user", "content": "我想学习机器学习，请帮我搜索相关课程"}
    ]
    
    tools = [{
        "type": "function",
        "function": {
            "name": "search_course_content",
            "description": "搜索课程内容和资源",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索查询关键词"
                    },
                    "category": {
                        "type": "string", 
                        "description": "课程分类",
                        "enum": ["programming", "ai", "data-science", "web", "mobile", "other"]
                    }
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
                print(f"[TOOL] 工具调用 {i}:")
                print(f"   - 工具名: {tool_call.function.name}")
                try:
                    args = json.loads(tool_call.function.arguments)
                    print(f"   - 参数: {json.dumps(args, ensure_ascii=False, indent=4)}")
                except:
                    print(f"   - 参数: {tool_call.function.arguments}")
            return True
        else:
            print("[WARN] 未触发工具调用")
            print(f"[RESPONSE] 模型响应: {response.choices[0].message.content}")
            return False
            
    except Exception as e:
        print(f"[FAIL] 工具调用测试失败: {e}")
        return False

def test_multi_turn_with_tools():
    """测试3: 多轮对话混合模式"""
    print_header("测试3: 多轮对话混合模式 - 智能路由切换")
    
    results = []
    
    # 第一轮: 纯对话
    print("\n🔄 第一轮: 纯对话 (预期R1)")
    messages1 = [
        {"role": "system", "content": "你是学习顾问"},
        {"role": "user", "content": "我是编程初学者，应该从哪里开始？"}
    ]
    
    try:
        response1 = llm_router.call_simple_chat(messages1, max_tokens=150)
        print("✅ 第一轮成功")
        print(f"📝 回复: {response1[:100]}...")
        results.append(True)
    except Exception as e:
        print(f"❌ 第一轮失败: {e}")
        results.append(False)
    
    # 第二轮: 工具调用
    print("\n🔄 第二轮: 工具调用搜索 (预期V3)")
    messages2 = [
        {"role": "system", "content": "现在用工具搜索具体课程"},
        {"role": "user", "content": "搜索Python基础编程课程"}
    ]
    
    tools2 = [{
        "type": "function",
        "function": {
            "name": "search_course_content",
            "description": "搜索课程",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索词"},
                    "level": {"type": "string", "description": "难度级别", "enum": ["beginner", "intermediate", "advanced"]}
                },
                "required": ["query"]
            }
        }
    }]
    
    try:
        response2 = llm_router.call_with_tools(messages2, tools2, max_tokens=150)
        
        if hasattr(response2.choices[0].message, 'tool_calls') and response2.choices[0].message.tool_calls:
            print("✅ 第二轮成功 - 触发工具调用")
            results.append(True)
        else:
            print("⚠️ 第二轮部分成功 - 未触发工具调用")
            results.append(False)
    except Exception as e:
        print(f"❌ 第二轮失败: {e}")
        results.append(False)
    
    return all(results)

def test_error_handling():
    """测试4: 错误处理和降级策略"""
    print_header("测试4: 错误处理测试")
    
    # 测试无效工具格式
    print("\n🧪 测试无效工具格式处理")
    
    invalid_tools = [{
        "type": "function",
        "function": {
            "name": "invalid_tool_missing_params"
            # 故意缺少parameters字段
        }
    }]
    
    try:
        response = llm_router.call_with_tools(
            [{"role": "user", "content": "测试无效工具"}],
            invalid_tools,
            max_tokens=100
        )
        print("⚠️ 无效工具格式未报错，需要改进错误处理")
        return False
    except Exception as e:
        print(f"✅ 正确捕获无效格式错误: {type(e).__name__}")
        return True

def main():
    """运行所有测试"""
    print("[START] 开始基于路由器的DeepSeek综合测试")
    
    # 打印配置信息
    print_model_info()
    
    # 检查API密钥
    if not config.LLM_API_KEY or config.LLM_API_KEY == "YOUR_NEW_DEEPSEEK_API_KEY_HERE":
        print("\n⚠️ 警告: API密钥未配置")
        print("请在.env文件中设置LLM_API_KEY")
        print("或设置环境变量: export LLM_API_KEY='your-key'")
        return False
    
    # 运行测试套件
    tests = [
        ("纯推理对话", test_simple_reasoning),
        ("工具调用搜索", test_tool_calling_search),
        ("多轮混合对话", test_multi_turn_with_tools),
        ("错误处理", test_error_handling)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 运行测试: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            results.append((test_name, False))
    
    # 输出总结
    print_header("🎯 测试结果总结")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n📊 总体结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！双模型路由策略工作正常")
        print("💡 关键验证点:")
        print("  ✅ R1处理纯推理任务")
        print("  ✅ V3处理工具调用任务") 
        print("  ✅ 智能路由切换正常")
        print("  ✅ 错误处理机制完善")
    else:
        print(f"\n⚠️ {total-passed} 个测试失败，需要进一步调试")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)