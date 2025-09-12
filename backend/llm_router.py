"""
LLM智能路由器 - 实现双模型策略
根据是否需要工具调用，智能选择DeepSeek-R1或DeepSeek-V3
"""

from typing import List, Dict, Any, Optional, Union
from openai import OpenAI
from config import config


class LLMRouter:
    """LLM智能路由器 - 双模型策略实现"""
    
    def __init__(self):
        """初始化OpenAI客户端"""
        if config.LLM_PROVIDER == "deepseek":
            self.client = OpenAI(
                base_url=config.LLM_BASE_URL,
                api_key=config.LLM_API_KEY
            )
        else:
            # 保留Claude支持
            self.client = None
    
    def call_chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0,
        max_tokens: int = 1000,
        **kwargs
    ) -> Any:
        """
        智能路由聊天请求
        
        Args:
            messages: 对话消息列表
            tools: 工具定义列表，如果提供则使用工具调用模型
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数
            
        Returns:
            OpenAI响应对象
        """
        if config.LLM_PROVIDER != "deepseek":
            raise NotImplementedError("Currently only supports DeepSeek provider")
            
        # 路由决策：根据是否需要工具调用选择模型
        if tools and len(tools) > 0:
            # 需要工具调用，使用DeepSeek-V3
            model = config.MODEL_TOOLCALL
            # 支持自定义tool_choice，默认为auto
            tool_choice = kwargs.pop("tool_choice", "auto")
            kwargs.update({
                "tools": tools,
                "tool_choice": tool_choice
            })
            print(f"[ROUTER] 使用工具调用模型: {model}, tool_choice: {tool_choice}")
        else:
            # 纯对话，使用DeepSeek-R1
            model = config.MODEL_REASON
            print(f"[ROUTER] 使用推理模型: {model}")
        
        # 构建请求参数
        request_params = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        # 执行请求
        try:
            response = self.client.chat.completions.create(**request_params)
            print(f"[ROUTER] 请求成功，使用模型: {response.model}")
            return response
        except Exception as e:
            print(f"[ROUTER] 请求失败: {e}")
            raise
    
    def call_simple_chat(
        self,
        messages: List[Dict[str, str]], 
        **kwargs
    ) -> str:
        """
        简单聊天接口，直接返回文本内容
        
        Args:
            messages: 对话消息列表
            **kwargs: 其他参数
            
        Returns:
            AI回复文本
        """
        response = self.call_chat(messages=messages, tools=None, **kwargs)
        return response.choices[0].message.content
    
    def call_with_tools(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]],
        **kwargs
    ) -> Any:
        """
        带工具调用的接口
        
        Args:
            messages: 对话消息列表
            tools: 工具定义列表
            **kwargs: 其他参数
            
        Returns:
            OpenAI响应对象（包含可能的工具调用）
        """
        return self.call_chat(messages=messages, tools=tools, **kwargs)


# 全局路由器实例
llm_router = LLMRouter()