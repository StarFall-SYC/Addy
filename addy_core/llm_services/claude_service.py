# addy_core/llm_services/claude_service.py

import json
import requests
from .base_llm_service import BaseLLMService

class ClaudeService(BaseLLMService):
    """
    Claude LLM服务实现。
    使用Anthropic的Claude API进行意图识别和响应生成。
    """
    
    def __init__(self, config, llm_config_section_name='LLM_Service'):
        """
        初始化Claude服务。

        Args:
            config: 配置对象。
            llm_config_section_name (str): LLM服务在配置文件中的节名。
        """
        if not config.has_section(llm_config_section_name):
            raise ValueError(f"Configuration section '[{llm_config_section_name}]' not found.")

        llm_config = config[llm_config_section_name]

        self.api_key = llm_config.get('api_key', fallback=None)
        self.model = llm_config.get('model', fallback='claude-3-haiku-20240307')
        self.api_base = llm_config.get('api_base', fallback='https://api.anthropic.com/v1')
        # Claude 可能需要特定的 anthropic_version，可以从配置中读取
        self.anthropic_version = llm_config.get('anthropic_version', fallback='2023-06-01')
        self.log_func = None  # 可选的日志记录函数
        
        # 意图识别的系统提示
        self.intent_system_prompt = (
            "你是一个专门用于意图识别的AI助手。分析用户输入，提取意图和实体。"
            "返回JSON格式，包含'intent'和'entities'字段。"
            "支持的意图包括：open_application, search_web, get_time, greeting, exit_assistant, "
            "capture_screen, move_mouse, click_mouse, type_text, press_key, hotkey, "
            "activate_window, minimize_window, maximize_window, close_window, list_windows。"
            "如果无法识别意图，将intent设为'unknown'。"
        )
    
    def set_logger(self, log_func):
        """
        设置日志记录函数。
        
        Args:
            log_func: 接受字符串参数的日志记录函数。
        """
        self.log_func = log_func
    
    def _log(self, message):
        """
        记录日志消息。
        
        Args:
            message (str): 要记录的消息。
        """
        if self.log_func:
            self.log_func(f"ClaudeService: {message}")
        else:
            print(f"ClaudeService: {message}")
    
    def get_intent_and_entities(self, text):
        """
        使用Claude API分析用户输入，提取意图和实体。
        
        Args:
            text (str): 用户输入的文本。
            
        Returns:
            str: 包含意图和实体的JSON字符串。
        """
        if not self.api_key:
            self._log("错误：未配置API密钥")
            return json.dumps({'intent': 'unknown', 'entities': {}})
        
        try:
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "max_tokens": 1000,
                "temperature": 0.1,  # 低温度以获得更确定性的结果
                "system": self.intent_system_prompt,
                "messages": [
                    {"role": "user", "content": text}
                ]
            }
            
            response = requests.post(
                f"{self.api_base}/messages",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                response_data = response.json()
                content = response_data['content'][0]['text']
                
                # 尝试解析返回的JSON
                try:
                    # 如果返回的内容被包裹在代码块中，提取JSON部分
                    if content.strip().startswith('```json') and content.strip().endswith('```'):
                        content = content.strip()[7:-3].strip()
                    elif content.strip().startswith('{') and content.strip().endswith('}'):
                        content = content.strip()
                    
                    parsed_content = json.loads(content)
                    # 验证返回的JSON格式是否正确
                    if 'intent' not in parsed_content or 'entities' not in parsed_content:
                        raise ValueError("返回的JSON缺少必要字段")
                    
                    return json.dumps(parsed_content)
                except (json.JSONDecodeError, ValueError) as e:
                    self._log(f"解析Claude响应时出错: {e}. 原始响应: {content}")
                    # 返回一个默认响应
                    return json.dumps({
                        'intent': 'unknown',
                        'entities': {'raw_response': content}
                    })
            else:
                self._log(f"Claude API请求失败: {response.status_code} - {response.text}")
                return json.dumps({'intent': 'unknown', 'entities': {}})
                
        except Exception as e:
            self._log(f"调用Claude API时出错: {e}")
            return json.dumps({'intent': 'unknown', 'entities': {}})
    
    def generate_response(self, text, context=None):
        """
        使用Claude API生成对用户输入的自然语言响应。
        
        Args:
            text (str): 用户输入的文本。
            context (list, optional): 对话历史上下文。
            
        Returns:
            str: 生成的响应文本。
        """
        if not self.api_key:
            self._log("错误：未配置API密钥")
            return "抱歉，我无法处理您的请求，因为API密钥未配置。"
        
        try:
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            
            messages = []
            
            # 添加对话历史上下文（如果有）
            if context:
                for msg in context:
                    messages.append(msg)
            
            # 添加当前用户输入
            messages.append({"role": "user", "content": text})
            
            payload = {
                "model": self.model,
                "max_tokens": 1000,
                "temperature": 0.7,
                "system": "你是Addy，一个友好的中文语音助手。提供简洁、有用的回答。",
                "messages": messages
            }
            
            response = requests.post(
                f"{self.api_base}/messages",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                response_data = response.json()
                return response_data['content'][0]['text']
            else:
                self._log(f"Claude API请求失败: {response.status_code} - {response.text}")
                return "抱歉，我在处理您的请求时遇到了问题。"
                
        except Exception as e:
            self._log(f"调用Claude API时出错: {e}")
            return "抱歉，我在处理您的请求时遇到了技术问题。"
    
    def is_available(self):
        """
        检查Claude服务是否可用。
        
        Returns:
            bool: 服务可用返回True，否则返回False。
        """
        if not self.api_key:
            return False
        
        try:
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            
            # 使用一个简单的请求来测试API连接
            payload = {
                "model": self.model,
                "max_tokens": 10,
                "temperature": 0.1,
                "system": "You are a helpful assistant.",
                "messages": [
                    {"role": "user", "content": "Hello"}
                ]
            }
            
            response = requests.post(
                f"{self.api_base}/messages",
                headers=headers,
                json=payload
            )
            
            return response.status_code == 200
        except Exception:
            return False