#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Patched DeepSeek API test script with robust tool-calling fallbacks & diagnostics.
- Reads OPENAI_BASE_URL and OPENAI_API_KEY from environment (recommended).
- Adds model listing & capability check.
- Tries three strategies for tool calling: (A) tools + "auto" (string), (B) tools + {"type": "auto"} (object), (C) legacy "functions" + function_call.
- Prints detailed server error info when 5xx happens.
"""

import os
import sys
import json
from typing import Any, Dict, List

# ---------- Configuration ----------
# Strongly recommended to set environment variables:
#   export OPENAI_BASE_URL="https://llm.chutes.ai/v1"
#   export OPENAI_API_KEY="..."
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://llm.chutes.ai/v1")

# NOTE: Avoid hardcoding secrets. This will fallback to empty if env var not set.
API_KEY = os.getenv("OPENAI_API_KEY", "")

# Original model under test. You can override via env var MODEL.
MODEL = os.getenv("MODEL", "deepseek-ai/DeepSeek-R1")

# Optional alternative model candidates that may support tool-calling better.
ALT_MODELS = [
    os.getenv("TOOLCALL_MODEL", "deepseek-ai/DeepSeek-V3"),
    "deepseek-ai/DeepSeek-Chat"
]

TIMEOUT_SECS = int(os.getenv("OPENAI_TIMEOUT", "90"))

# ---------- Utilities ----------
def _pp(label: str, data: Any) -> None:
    print(f"\n{label}:")
    try:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    except Exception:
        print(str(data))

def _print_header(title: str) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("-" * 60)

def _print_exception(ctx: str, e: Exception) -> None:
    print(f"\n[ERROR] {ctx} 失败: {type(e).__name__}: {str(e)}")
    # Try to extract richer info from OpenAI client exceptions
    for attr in ["status_code", "status", "request_id"]:
        if hasattr(e, attr):
            print(f"- {attr}: {getattr(e, attr)}")
    resp = getattr(e, "response", None)
    if resp:
        try:
            # new client may expose .response.json() or .response.text
            if hasattr(resp, "json"):
                _pp("服务器响应JSON", resp.json())
            elif hasattr(resp, "text"):
                print("服务器响应文本:")
                print(resp.text)
            else:
                _pp("服务器响应对象", resp)
        except Exception as _:
            pass

# ---------- Tests ----------
def list_models() -> List[str]:
    """List available models and verify the target model exists."""
    _print_header("测试0: 列出可用模型")
    try:
        from openai import OpenAI
        client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
        models = client.models.list()
        ids = [m.id for m in models.data]
        print(f"[OK] 共返回 {len(ids)} 个模型。")
        print("（前20个）", ids[:20])
        if MODEL in ids:
            print(f"[CHECK] 目标模型存在: {MODEL}")
        else:
            print(f"[WARN] 未找到目标模型: {MODEL}，可能需要改用下面候选模型之一: {ALT_MODELS}")
        return ids
    except Exception as e:
        _print_exception("列出模型", e)
        return []

def test_basic_chat(model: str) -> bool:
    """基础对话"""
    _print_header(f"测试1: 基础对话功能（模型: {model}）")
    try:
        from openai import OpenAI
        client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是一个有帮助的AI助手"},
                {"role": "user", "content": "你好，请简单介绍一下什么是RAG系统"}
            ],
            temperature=0,
            max_tokens=200,
            timeout=TIMEOUT_SECS
        )
        print("\n[PASS] API连接成功！")
        print("\n响应内容:")
        print("-" * 40)
        print(response.choices[0].message.content)
        print("-" * 40)
        print(f"- Model: {response.model}")
        print(f"- Usage: {response.usage}")
        return True
    except Exception as e:
        _print_exception("基础对话", e)
        return False

def test_function_calling(model: str) -> bool:
    """工具调用，包含三种策略的回退"""
    _print_header(f"测试2: 工具调用功能（模型: {model}）")
    try:
        from openai import OpenAI
        client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

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

        # Legacy "functions" format for compatibility
        functions = [{
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
        }]

        messages = [
            {"role": "system", "content": "你是课程搜索助手；当用户询问课程时，优先调用工具。"},
            {"role": "user", "content": "搜索关于Python编程的课程"}
        ]

        attempts: List[Dict[str, Any]] = [
            {"label": 'tools + "auto"(string)',
             "payload": {"tools": tools, "tool_choice": "auto"}},
            {"label": 'tools + {"type":"auto"}(object)',
             "payload": {"tools": tools, "tool_choice": {"type": "auto"}}},
            {"label": 'legacy functions + function_call="auto"',
             "payload": {"functions": functions, "function_call": "auto"}},
        ]

        for attempt in attempts:
            label = attempt["label"]
            payload = attempt["payload"]
            print(f"\n>>> 尝试: {label}")
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0,
                    max_tokens=128,
                    timeout=TIMEOUT_SECS,
                    **payload
                )
                msg = response.choices[0].message
                tool_calls = getattr(msg, "tool_calls", None)
                if tool_calls:
                    print("\n[PASS] 工具调用功能支持！")
                    print("\n工具调用详情:")
                    for tc in tool_calls:
                        print(f"- 工具名称: {tc.function.name}")
                        print(f"- 参数: {tc.function.arguments}")
                    return True
                else:
                    print("\n[WARNING] 模型未触发工具调用。返回内容：")
                    print(getattr(msg, "content", ""))
            except Exception as e:
                _print_exception(f"尝试（{label}）", e)

        print("\n[FAIL] 所有策略均未成功触发工具调用。")
        return False

    except Exception as e:
        _print_exception("工具调用（外层）", e)
        return False

def test_context_handling(model: str) -> bool:
    """上下文处理"""
    _print_header(f"测试3: 上下文处理（模型: {model}）")
    try:
        from openai import OpenAI
        client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

        messages = [
            {"role": "system", "content": "你是课程材料助手"},
            {"role": "user", "content": "我想了解MCP课程"},
            {"role": "assistant", "content": "MCP（Model Context Protocol）是一个关于模型上下文协议的课程，它介绍了如何有效地管理和使用AI模型的上下文。"},
            {"role": "user", "content": "它主要包含哪些内容？"}
        ]

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0,
            max_tokens=200,
            timeout=TIMEOUT_SECS
        )

        print("\n[PASS] 上下文处理成功！")
        print("\n响应内容:")
        print("-" * 40)
        print(response.choices[0].message.content)
        print("-" * 40)
        return True

    except Exception as e:
        _print_exception("上下文处理", e)
        return False

def main() -> bool:
    print("\n开始测试 DeepSeek API 连接（增强诊断版）\n")
    print(f"API端点: {BASE_URL}")
    print(f"模型: {MODEL}")
    print("=" * 60)

    # Check SDK
    try:
        import openai
        print(f"[OK] OpenAI SDK已安装 (版本: {openai.__version__})")
    except ImportError:
        print("[ERROR] 未安装OpenAI SDK。请先执行: pip install --upgrade openai")
        return False

    # Guard rails for secrets
    if not API_KEY:
        print("[WARN] 未从环境变量读取到 OPENAI_API_KEY。为安全起见，建议通过环境变量提供密钥。")
        print("       示例: export OPENAI_API_KEY='your_key'")
        # 允许继续执行，以便只做连通性排查。

    # 0) list models (best-effort)
    list_models()

    results = []
    # 1) basic chat on target model
    results.append(("基础对话", test_basic_chat(MODEL)))
    # 2) tool calling on target model
    results.append(("工具调用", test_function_calling(MODEL)))

    # 2b) If tool-calling failed on target model, try alternatives
    if not results[-1][1]:
        for alt in ALT_MODELS:
            print(f"\n--- 尝试候选模型以测试工具调用: {alt} ---")
            ok = test_function_calling(alt)
            results.append((f"工具调用（候选: {alt}）", ok))
            if ok:
                break

    # 3) context
    results.append(("上下文处理", test_context_handling(MODEL)))

    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    all_passed = True
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{test_name}: {status}")
        all_passed = all_passed and result

    if all_passed:
        print("\n[SUCCESS] 所有测试通过！API可以正常使用。")
    else:
        print("\n[WARNING] 部分测试未通过，请根据上面的错误信息排查。")
        print("常见原因：")
        print("1) 当前模型不支持 tool calling 或网关未正确转发相关字段；")
        print("2) 仅支持旧版 functions 规范；")
        print("3) 供应商在该模型上关闭了工具调用；")
        print("4) 临时服务端 5xx（如“exhausted all available targets to no avail”负载均衡/上游健康检查失败）。")

    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
