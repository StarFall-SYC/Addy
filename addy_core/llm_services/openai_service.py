# addy_core/llm_services/openai_service.py

import json
import requests
from .base_llm_service import BaseLLMService

class OpenAIService(BaseLLMService):
    """
    OpenAI LLM服务实现。
    使用OpenAI API进行意图识别和响应生成。
    """
    
    def __init__(self, config, llm_config_section_name='LLM_Service'):
        """
        初始化OpenAI服务。

        Args:
            config: 配置对象。
            llm_config_section_name (str): LLM服务在配置文件中的节名。
        """
        if not config.has_section(llm_config_section_name):
            raise ValueError(f"Configuration section '[{llm_config_section_name}]' not found.")

        llm_config = config[llm_config_section_name]

        self.api_key = llm_config.get('api_key', fallback=None)
        self.model = llm_config.get('model', fallback='gpt-3.5-turbo')
        # 对于OpenAI兼容服务，api_base通常是必须的，但如果用户使用官方OpenAI且未指定，则默认为官方地址
        # 如果api_type明确是openai_compatible且api_base未提供，则使用官方地址
        # 如果api_type是其他（例如自定义的openai_compatible），则api_base应该由用户提供
        default_api_base = 'https://api.openai.com/v1'
        self.api_base = llm_config.get('api_base')
        if not self.api_base and llm_config.get('api_type', '').lower() in ['openai_compatible', 'openai']:
             self.api_base = default_api_base
        elif not self.api_base: # 如果api_base仍未设置（例如自定义类型但未提供base_url）
            # 根据实际需求，这里可以抛出错误或记录警告
            print(f"Warning: 'api_base' not specified in '[{llm_config_section_name}]' and api_type is not 'openai_compatible' with default. Service might not work.")
            # self.api_base = default_api_base # 或者仍然使用默认，但这可能不适用于所有兼容服务
        self.log_func = None  # 可选的日志记录函数
        self.tool_manager = None # 初始化工具管理器
        self.openai_tools_json = [] # 用于OpenAI原生Function Calling的工具列表
        self.custom_tools_json_for_prompt = "[]" # 用于自定义JSON格式的工具描述
        
        # 意图识别的系统提示
        self.intent_system_prompt_template = (
            "你是一个专门用于意图识别和工具调用的AI助手。分析用户输入，提取意图和实体，并判断是否需要调用工具。"
            "如果需要调用工具，请在返回的JSON中包含 'tool_call' 字段，其中包含 'tool_name' 和 'tool_input'。"
            "'tool_input' 应该是一个包含工具所需参数的字典。"
            "返回JSON格式，包含'intent', 'entities', 和可选的 'tool_call' 字段。"
            "支持的意图包括：open_application, search_web, get_time, greeting, exit_assistant, "
            "capture_screen, move_mouse, click_mouse, type_text, press_key, hotkey, "
            "activate_window, minimize_window, maximize_window, close_window, list_windows。"
            "如果无法识别意图，将intent设为'unknown'。"
            "可用的工具如下：\n{available_tools_json}"
        )
        self.intent_system_prompt = self.intent_system_prompt_template.format(available_tools_json="[]") # 初始为空列表
        
        # 意图识别的系统提示
        self.intent_system_prompt_base = (
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
            self.log_func(f"OpenAIService: {message}")
        else:
            print(f"OpenAIService: {message}")

    def set_tool_manager(self, tool_manager):
        """
        设置工具管理器实例，并更新系统提示以包含可用的工具信息。
        
        Args:
            tool_manager: ToolManager的实例。
        """
        self.tool_manager = tool_manager
        if self.tool_manager:
            available_tools = self.tool_manager.get_available_tools()
            # 构建工具描述，以便LLM理解每个工具的功能和参数
            tools_description_for_llm = []
            for tool_info in available_tools:
                # 这里可以根据需要进一步细化工具的描述，例如参数说明等
                # 目前简单地使用工具名称和描述
                tools_description_for_llm.append({
                    "name": tool_info['name'],
                    "description": tool_info['description'],
                    "supported_intents": tool_info.get('supported_intents', []) # 确保存在
                })
            self.custom_tools_json_for_prompt = json.dumps(tools_description_for_llm, ensure_ascii=False, indent=2)
            self.intent_system_prompt = self.intent_system_prompt_template.format(
                available_tools_json=self.custom_tools_json_for_prompt
            )
            self.openai_tools_json = self._convert_tools_to_openai_format(available_tools)
            self._log(f"Tool manager set. Prepared {len(tools_description_for_llm)} tools for custom JSON and {len(self.openai_tools_json)} for OpenAI native format.")
        else:
            self.custom_tools_json_for_prompt = "[]"
            self.intent_system_prompt = self.intent_system_prompt_template.format(available_tools_json=self.custom_tools_json_for_prompt)
            self.openai_tools_json = []
            self._log("Tool manager is None. Using default intent system prompt and no tools prepared.")

    def _convert_tools_to_openai_format(self, available_tools):
        """
        将ToolManager提供的工具信息转换为OpenAI Function Calling所需的格式。
        """
        openai_tools = []
        if not available_tools:
            return openai_tools
            
        for tool_info in available_tools:
            parameters_schema = {
                "type": "object",
                "properties": {},
                "required": tool_info.get("required_parameters", [])
            }
            if tool_info.get('parameters'):
                for param_name, param_details in tool_info['parameters'].items():
                    parameters_schema["properties"][param_name] = {
                        "type": param_details.get('type', 'string'),
                        "description": param_details.get('description', '')
                    }
                    # OpenAI schema doesn't directly support 'enum' at parameter level like this,
                    # but description can mention it. For true enum, type should be string and enum list provided.
                    if param_details.get('enum'):
                         parameters_schema["properties"][param_name]['enum'] = param_details['enum']

            openai_tools.append({
                "type": "function",
                "function": {
                    "name": tool_info['name'],
                    "description": tool_info['description'],
                    "parameters": parameters_schema
                }
            })
        return openai_tools

    def get_supported_tool_protocols(self):
        """
        返回此LLM服务支持的工具调用协议列表。
        """
        return ["openai_function_calling", "custom_json"]
    
    def get_intent_and_entities(self, text):
        """
        使用OpenAI API分析用户输入，提取意图和实体。
        
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
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            messages = [
                {"role": "user", "content": text}
            ]
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.1
            }

            # 优先尝试OpenAI原生Function Calling
            if self.tool_manager and self.openai_tools_json and "openai_function_calling" in self.get_supported_tool_protocols():
                self._log(f"Attempting OpenAI native function calling with {len(self.openai_tools_json)} tools.")
                payload['tools'] = self.openai_tools_json
                payload['tool_choice'] = "auto"
                # 对于原生工具调用，系统提示可以更通用，或者专注于指导模型如何选择和使用工具
                # 使用不包含工具列表的基础提示，因为工具定义已通过 'tools' 参数传递
                messages.insert(0, {"role": "system", "content": self.intent_system_prompt_base})
            elif self.tool_manager: # 回退到自定义JSON格式
                self._log("Using custom JSON format for tool calling.")
                # intent_system_prompt 已经包含了自定义格式的工具列表
                messages.insert(0, {"role": "system", "content": self.intent_system_prompt})
            else: # 没有工具管理器或没有工具
                self._log("No tool manager or no tools available. Using basic intent recognition.")
                messages.insert(0, {"role": "system", "content": self.intent_system_prompt_base})
            
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                response_data = response.json()
                message = response_data['choices'][0]['message']

                # 检查是否有工具调用请求 (OpenAI原生格式)
                if message.get("tool_calls"):
                    tool_call_data = message["tool_calls"][0] # 假设只处理第一个工具调用
                    function_call = tool_call_data["function"]
                    tool_name = function_call["name"]
                    tool_arguments_str = function_call["arguments"]
                    try:
                        tool_arguments = json.loads(tool_arguments_str)
                    except json.JSONDecodeError as e:
                        self._log(f"Error decoding tool arguments JSON: {e}. Arguments string: {tool_arguments_str}")
                        return json.dumps({'intent': 'unknown', 'entities': {'error': 'Failed to parse tool arguments'}})

                    # 将OpenAI的function call格式转换为我们内部的tool_call格式
                    # 同时，我们需要一个意图。对于工具调用，意图可以就是工具名称，或者一个更通用的“execute_tool”
                    # 这里我们简单地将工具名作为意图，参数作为实体
                    parsed_content = {
                        "intent": tool_name, # 或者 "execute_tool"
                        "entities": tool_arguments, # 或者 {'tool_name': tool_name, 'tool_arguments': tool_arguments}
                        "tool_call": {
                            "name": tool_name,
                            "arguments": tool_arguments
                        }
                    }
                    self._log(f"OpenAI native tool call detected: {tool_name} with args {tool_arguments}")
                    return json.dumps(parsed_content)
                else:
                    # 处理自定义JSON格式的响应 (或者没有工具调用的普通意图识别)
                    content = message.get('content', '')
                    try:
                        if content.strip().startswith('```json') and content.strip().endswith('```'):
                            content = content.strip()[7:-3].strip()
                        elif content.strip().startswith('{') and content.strip().endswith('}'):
                            content = content.strip()
                        
                        parsed_content = json.loads(content)
                        if 'intent' not in parsed_content:
                             # 如果LLM只返回了tool_call（自定义格式），我们尝试填充intent
                            if 'tool_call' in parsed_content and 'name' in parsed_content['tool_call']:
                                parsed_content['intent'] = parsed_content['tool_call']['name']
                                if 'entities' not in parsed_content:
                                     parsed_content['entities'] = parsed_content['tool_call'].get('arguments', {})
                            else:
                                raise ValueError("返回的JSON缺少'intent'字段")
                        
                        # 确保entities存在
                        if 'entities' not in parsed_content:
                            parsed_content['entities'] = {}

                        self._log(f"Custom JSON response parsed: {parsed_content}")
                        return json.dumps(parsed_content)
                    except (json.JSONDecodeError, ValueError) as e:
                        self._log(f"解析OpenAI响应 (custom JSON) 时出错: {e}. 原始响应: {content}")
                        return json.dumps({
                            'intent': 'unknown',
                            'entities': {'raw_response': content, 'error': str(e)}
                        })
            else:
                self._log(f"OpenAI API请求失败: {response.status_code} - {response.text}")
                return json.dumps({'intent': 'unknown', 'entities': {}})
                
        except Exception as e:
            self._log(f"调用OpenAI API时出错: {e}")
            return json.dumps({'intent': 'unknown', 'entities': {}})
    
    def generate_response(self, text, context=None):
        """
        使用OpenAI API生成对用户输入的自然语言响应。
        
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
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            messages = []
            
            # 添加系统提示
            messages.append({
                "role": "system",
                "content": "你是Addy，一个友好的中文语音助手。提供简洁、有用的回答。"
            })
            
            # 添加对话历史上下文（如果有）
            if context:
                for msg in context:
                    messages.append(msg)
            
            # 添加当前用户输入
            messages.append({"role": "user", "content": text})
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.7
            }
            
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                response_data = response.json()
                return response_data['choices'][0]['message']['content']
            else:
                self._log(f"OpenAI API请求失败: {response.status_code} - {response.text}")
                return "抱歉，我在处理您的请求时遇到了问题。"
                
        except Exception as e:
            self._log(f"调用OpenAI API时出错: {e}")
            return "抱歉，我在处理您的请求时遇到了技术问题。"
    
    def is_available(self):
        """
        检查OpenAI服务是否可用。
        
        Returns:
            bool: 服务可用返回True，否则返回False。
        """
        if not self.api_key:
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # 使用一个简单的请求来测试API连接
            response = requests.get(
                f"{self.api_base}/models",
                headers=headers
            )
            
            return response.status_code == 200
        except Exception:
            return False