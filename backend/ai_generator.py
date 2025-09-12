"""
多提供商AI生成器 - 支持Claude和DeepSeek的统一接口
使用智能路由器实现双模型策略
"""

import re
import anthropic
from typing import List, Optional, Dict, Any, Union
from config import config
from llm_router import llm_router


class AIGenerator:
    """统一的AI生成器 - 支持Claude和DeepSeek双模型路由"""
    
    # 静态系统提示，避免每次调用重建
    SYSTEM_PROMPT = """You are an AI assistant specialized in course materials and educational content with access to a comprehensive search tool for course information.

Search Tool Usage:
- Use the search tool **only** for questions about specific course content or detailed educational materials
- **One search per query maximum**
- Synthesize search results into accurate, fact-based responses
- If search yields no results, state this clearly without offering alternatives

Response Protocol:
- **General knowledge questions**: Answer using existing knowledge without searching
- **Course-specific questions**: Search first, then answer
- **No meta-commentary**:
 - Provide direct answers only — no reasoning process, search explanations, or question-type analysis
 - Do not mention "based on the search results"

All responses must be:
1. **Brief, Concise and focused** - Get to the point quickly
2. **Educational** - Maintain instructional value
3. **Clear** - Use accessible language
4. **Example-supported** - Include relevant examples when they aid understanding
Provide only the direct answer to what was asked.
"""
    
    def __init__(self, api_key: str = None, model: str = None):
        """
        初始化AI生成器
        
        Args:
            api_key: API密钥（如果未提供则从配置读取）
            model: 模型名称（如果未提供则从配置读取）
        """
        self.provider = config.LLM_PROVIDER
        
        if self.provider == "deepseek":
            # 使用路由器，不需要直接初始化客户端
            self.client = None
            self.model = None
        else:
            # Claude提供商
            self.client = anthropic.Anthropic(
                api_key=api_key or config.ANTHROPIC_API_KEY
            )
            self.model = model or config.ANTHROPIC_MODEL
        
        # 预构建基础参数
        self.base_params = {
            "temperature": 0,
            "max_tokens": 800
        }
    
    def generate_response(self, 
                         query: str,
                         conversation_history: Optional[str] = None,
                         tools: Optional[List] = None,
                         tool_manager=None) -> str:
        """
        生成AI响应，支持工具使用和对话上下文
        
        Args:
            query: 用户的问题或请求
            conversation_history: 对话历史（可选）
            tools: 可用工具列表
            tool_manager: 工具管理器
            
        Returns:
            生成的响应字符串
        """
        if self.provider == "deepseek":
            return self._generate_deepseek_response(
                query, conversation_history, tools, tool_manager
            )
        else:
            return self._generate_claude_response(
                query, conversation_history, tools, tool_manager
            )
    
    def _generate_deepseek_response(self, 
                                   query: str,
                                   conversation_history: Optional[str] = None,
                                   tools: Optional[List] = None,
                                   tool_manager=None) -> str:
        """使用DeepSeek（通过路由器）生成响应"""
        
        # 构建消息列表（OpenAI格式）
        messages = []
        
        # 系统消息
        system_content = self.SYSTEM_PROMPT
        if conversation_history:
            system_content += f"\n\nPrevious conversation:\n{conversation_history}"
        
        messages.append({"role": "system", "content": system_content})
        messages.append({"role": "user", "content": query})
        
        # 处理工具格式 
        openai_tools = None
        if tools:
            # 检查工具是否已经是OpenAI格式（第一个工具有"type": "function"）
            if (tools and isinstance(tools[0], dict) and 
                tools[0].get("type") == "function"):
                # 已经是OpenAI格式，直接使用
                openai_tools = tools
            else:
                # Claude格式，需要转换
                openai_tools = self._convert_tools_to_openai(tools)
        
        try:
            # 使用路由器调用
            if openai_tools:
                response = llm_router.call_with_tools(
                    messages=messages,
                    tools=openai_tools,
                    **self.base_params
                )
            else:
                response_text = llm_router.call_simple_chat(
                    messages=messages,
                    **self.base_params
                )
                # 清理思考内容
                return self._clean_thinking_content(response_text)
            
            # 处理工具调用响应
            if (hasattr(response.choices[0].message, 'tool_calls') and 
                response.choices[0].message.tool_calls and tool_manager):
                return self._handle_openai_tool_execution(
                    response, messages, openai_tools, tool_manager
                )
            
            # 返回普通响应
            content = response.choices[0].message.content or ""
            # 清理思考内容
            return self._clean_thinking_content(content)
            
        except Exception as e:
            print(f"[ERROR] DeepSeek响应生成失败: {e}")
            return f"抱歉，我遇到了一些技术问题。请稍后再试。"
    
    def _clean_thinking_content(self, response_text: str) -> str:
        """
        清理DeepSeek-R1响应中的思考内容
        
        Args:
            response_text: 原始响应文本
            
        Returns:
            清理后的响应文本
        """
        # 检查是否启用清理功能
        if not config.CLEAN_R1_THINKING:
            return response_text
        
        if not response_text:
            return response_text
        
        original_length = len(response_text)
        
        # 步骤1：移除<thinking>标签及其内容
        cleaned = re.sub(r'<thinking>.*?</thinking>', '', response_text, flags=re.DOTALL)
        
        # 步骤2：智能识别答案开始位置
        # 寻找答案的开始标记（通常在思考后有明确的转折）
        # 注意：移除了 "\n\n1." 避免误删编号列表前的答案内容
        answer_markers = [
            "\n\nThe available course materials",
            "\n\nBased on the course materials",
            "\n\nFrom the course content",
            "\n\nAccording to the materials",
            "\n\nThe course covers",
            "\n\n**",  # 粗体标题开始
            "\n\n###",  # Markdown标题
            "\n\n##",
            "\n\nIn the context of",
            "\n\nTo answer your question",
            "\n\nHere's",  # 常见答案开始
            "\n\nRAG",  # 直接定义开始
        ]
        
        # 尝试找到答案的开始位置
        answer_start = -1
        for marker in answer_markers:
            pos = cleaned.find(marker)
            if pos != -1:
                answer_start = pos
                break
        
        # 如果找到了明确的答案开始位置，直接返回答案部分
        if answer_start != -1:
            result = cleaned[answer_start:].strip()
            if result and len(result) >= config.R1_THINKING_MIN_LENGTH:
                # 打印被清理的思考内容用于调试
                cleaned_content = cleaned[:answer_start].strip()
                print(f"\n[DEBUG] ========== 通过答案标记清理的思考内容（{len(cleaned_content)}字符）==========")
                # 按段落显示，更清晰
                cleaned_paragraphs = cleaned_content.split('\n\n')
                for i, para in enumerate(cleaned_paragraphs[:3], 1):
                    preview = para[:200] + "..." if len(para) > 200 else para
                    preview = preview.replace('\n', ' ')  # 清理换行符
                    print(f"思考段落{i}: {preview}")
                if len(cleaned_paragraphs) > 3:
                    print(f"... 共{len(cleaned_paragraphs)}个思考段落被清理")
                print("[DEBUG] ========== 思考内容结束 ==========")
                print(f"[INFO] 找到答案标记，清理了{len(cleaned_content)}字符的思考内容\n")
                return result
        
        # 步骤3：基于段落结构过滤
        paragraphs = cleaned.split('\n\n')
        filtered_paragraphs = []
        skipped_paragraphs = []  # 记录被跳过的段落用于调试
        
        # 用于检测是否已经进入真实答案部分
        found_real_answer = False
        
        for para in paragraphs:
            para_stripped = para.strip()
            para_lower = para_stripped.lower()
            
            # 跳过空段落
            if not para_stripped:
                continue
            
            # 检测真实答案的开始（通常是结构化内容）
            if not found_real_answer:
                # 检查是否是列表项、标题或正式陈述
                # 注意：正式定义（如 "RAG (Retrieval-Augmented Generation)"）也是答案
                if (para_stripped.startswith(('1.', '2.', '3.', '•', '-', '*', '**', '##')) or
                    para_stripped.startswith(('The available', 'Based on the course', 'According to', 
                                            'In the context', 'Key points', 'Core principles')) or
                    # 检测正式定义或技术说明（包含括号解释的术语）
                    ('(' in para_stripped[:100] and ')' in para_stripped[:150] and 
                     not any(ind in para_lower for ind in ['i ', "i'm", "let me"]))):
                    found_real_answer = True
                    filtered_paragraphs.append(para)
                    continue
            
            # 如果已经找到真实答案，继续添加后续段落
            if found_real_answer:
                filtered_paragraphs.append(para)
                continue
            
            # 检测思考内容的特征
            is_thinking = False
            
            # 第一人称检测
            first_person_indicators = ['i ', "i'm", "i'll", "i've", "let me", "i need", "i should", "my "]
            for indicator in first_person_indicators:
                if indicator in para_lower:
                    is_thinking = True
                    break
            
            # 过程性语言检测
            if not is_thinking:
                process_words = ['searching', 'looking', 'checking', 'recalling', 'synthesizing', 
                                'wait', 'hmm', 'okay', 'actually', 'but the user']
                for word in process_words:
                    if word in para_lower:
                        is_thinking = True
                        break
            
            # 额外检查：如果段落是正式的技术定义或说明，不应该被过滤
            # 例如："RAG (Retrieval-Augmented Generation) technology..."
            if is_thinking:
                # 检查是否是技术定义（包含缩写和全称）
                if ('(' in para_stripped[:100] and ')' in para_stripped[:150] and
                    'technology' in para_lower or 'framework' in para_lower or 
                    'system' in para_lower or 'method' in para_lower or
                    'approach' in para_lower or 'technique' in para_lower):
                    is_thinking = False  # 这是技术定义，不是思考内容
            
            # 如果不是思考内容，保留该段落
            if not is_thinking:
                filtered_paragraphs.append(para)
            else:
                skipped_paragraphs.append(para)
        
        # 如果有被跳过的段落，打印调试信息
        if skipped_paragraphs:
            print(f"\n[DEBUG] ========== 通过段落过滤清理的思考内容（共{len(skipped_paragraphs)}个段落）==========")
            # 如果段落数量不多（<=5个），全部显示；否则显示前5个
            display_limit = 5 if len(skipped_paragraphs) > 5 else len(skipped_paragraphs)
            for i, para in enumerate(skipped_paragraphs[:display_limit], 1):
                # 显示段落的前150字符，确保能看到开头内容
                preview = para[:150] + "..." if len(para) > 150 else para
                # 清理换行符，使输出更整洁
                preview = preview.replace('\n', ' ')
                print(f"段落{i}: {preview}")
            
            # 只有当段落数量超过5个时才显示剩余数量
            if len(skipped_paragraphs) > display_limit:
                # 也显示最后一个段落的预览，以便了解结尾内容
                last_para = skipped_paragraphs[-1]
                last_preview = last_para[:150] + "..." if len(last_para) > 150 else last_para
                last_preview = last_preview.replace('\n', ' ')
                print(f"...")
                print(f"段落{len(skipped_paragraphs)}: {last_preview}")
                print(f"（共过滤了 {len(skipped_paragraphs)} 个段落）")
            print("[DEBUG] ========== 思考内容结束 ==========\n")
        
        result = '\n\n'.join(filtered_paragraphs).strip()
        
        # 步骤3：安全检查，避免过度清理
        if not result or len(result) < config.R1_THINKING_MIN_LENGTH:
            print(f"[WARNING] 清理后内容过短（{len(result)}字符，最小要求{config.R1_THINKING_MIN_LENGTH}），返回原文")
            return response_text
        
        # 记录清理效果
        cleaned_chars = original_length - len(result)
        if cleaned_chars > 0:
            print(f"[INFO] 清理了{cleaned_chars}字符的思考内容（{cleaned_chars*100/original_length:.1f}%）")
        
        return result
    
    def _generate_claude_response(self, 
                                 query: str,
                                 conversation_history: Optional[str] = None,
                                 tools: Optional[List] = None,
                                 tool_manager=None) -> str:
        """使用Claude生成响应（保持原有逻辑）"""
        
        # 构建系统内容
        system_content = (
            f"{self.SYSTEM_PROMPT}\n\nPrevious conversation:\n{conversation_history}"
            if conversation_history 
            else self.SYSTEM_PROMPT
        )
        
        # 准备API调用参数
        api_params = {
            "model": self.model,
            "messages": [{"role": "user", "content": query}],
            "system": system_content,
            **self.base_params
        }
        
        # 添加工具（如果可用）
        if tools:
            api_params["tools"] = tools
            api_params["tool_choice"] = {"type": "auto"}
        
        try:
            # 获取Claude响应
            response = self.client.messages.create(**api_params)
            
            # 处理工具执行
            if response.stop_reason == "tool_use" and tool_manager:
                return self._handle_claude_tool_execution(response, api_params, tool_manager)
            
            # 返回直接响应
            return response.content[0].text
            
        except Exception as e:
            print(f"[ERROR] Claude响应生成失败: {e}")
            return f"抱歉，我遇到了一些技术问题。请稍后再试。"
    
    def _convert_tools_to_openai(self, claude_tools: List[Dict]) -> List[Dict]:
        """将Claude工具格式转换为OpenAI格式"""
        openai_tools = []
        
        for tool in claude_tools:
            if not isinstance(tool, dict) or "name" not in tool:
                continue
                
            openai_tool = {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": tool.get("input_schema", {
                        "type": "object",
                        "properties": {},
                        "required": []
                    })
                }
            }
            openai_tools.append(openai_tool)
        
        return openai_tools
    
    def _handle_openai_tool_execution(self, 
                                     initial_response,
                                     messages: List[Dict],
                                     tools: List[Dict],
                                     tool_manager) -> str:
        """处理OpenAI格式的工具执行"""
        
        # 添加AI的工具调用消息
        messages.append({
            "role": "assistant", 
            "content": initial_response.choices[0].message.content or "",
            "tool_calls": initial_response.choices[0].message.tool_calls
        })
        
        # 执行所有工具调用
        for tool_call in initial_response.choices[0].message.tool_calls:
            tool_name = tool_call.function.name
            
            try:
                # 解析参数
                import json
                tool_args = json.loads(tool_call.function.arguments)
                
                # 执行工具
                tool_result = tool_manager.execute_tool(tool_name, **tool_args)
                
                # 添加工具结果消息
                messages.append({
                    "role": "tool",
                    "content": tool_result,
                    "tool_call_id": tool_call.id
                })
                
            except Exception as e:
                # 添加错误消息
                messages.append({
                    "role": "tool", 
                    "content": f"工具执行错误: {str(e)}",
                    "tool_call_id": tool_call.id
                })
        
        # 获取最终响应（不带工具）
        try:
            final_response = llm_router.call_simple_chat(
                messages=messages,
                **self.base_params
            )
            # 清理思考内容
            return self._clean_thinking_content(final_response)
            
        except Exception as e:
            return f"生成最终响应时出错: {str(e)}"
    
    def _handle_claude_tool_execution(self, 
                                     initial_response, 
                                     base_params: Dict[str, Any], 
                                     tool_manager) -> str:
        """处理Claude格式的工具执行（保持原有逻辑）"""
        
        # 开始使用现有消息
        messages = base_params["messages"].copy()
        
        # 添加AI的工具使用响应
        messages.append({"role": "assistant", "content": initial_response.content})
        
        # 执行所有工具调用并收集结果
        tool_results = []
        for content_block in initial_response.content:
            if content_block.type == "tool_use":
                tool_result = tool_manager.execute_tool(
                    content_block.name, 
                    **content_block.input
                )
                
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": content_block.id,
                    "content": tool_result
                })
        
        # 将工具结果作为单个消息添加
        if tool_results:
            messages.append({"role": "user", "content": tool_results})
        
        # 准备最终API调用（不带工具）
        final_params = {
            "model": self.model,
            "messages": messages,
            "system": base_params["system"],
            **self.base_params
        }
        
        # 获取最终响应
        final_response = self.client.messages.create(**final_params)
        return final_response.content[0].text


# 工厂函数，根据配置创建合适的生成器
def create_ai_generator() -> AIGenerator:
    """根据当前配置创建AI生成器"""
    return AIGenerator()