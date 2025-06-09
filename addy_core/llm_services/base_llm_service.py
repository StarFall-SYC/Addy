# addy_core/llm_services/base_llm_service.py

from abc import ABC, abstractmethod

class BaseLLMService(ABC):
    """
    抽象基类，定义所有LLM服务需要实现的接口。
    所有具体的LLM服务实现（如OpenAI、Claude等）都应继承此类。
    """
    
    @abstractmethod
    def __init__(self, config):
        """
        初始化LLM服务。
        
        Args:
            config: 配置对象，包含API密钥等必要信息。
        """
        pass
    
    @abstractmethod
    def get_intent_and_entities(self, text):
        """
        分析用户输入文本，提取意图和实体。
        
        Args:
            text (str): 用户输入的文本。
            
        Returns:
            str: 包含意图、实体以及可能的工具调用信息的JSON字符串。
                 如果需要调用工具，期望格式包含 'tool_call': {'name': 'tool_name', 'arguments': {...}}。
                 例如: '{"intent": "some_intent", "entities": {...}, "tool_call": {"name": "calculator", "arguments": {"expression": "2+2"}}}'
                 如果不需要工具调用，则 'tool_call' 字段可以省略或为 null。
        """
        pass
    
    @abstractmethod
    def generate_response(self, text, context=None):
        """
        生成对用户输入的自然语言响应。
        
        Args:
            text (str): 用户输入的文本。
            context (list, optional): 对话历史上下文。
            
        Returns:
            str: 生成的响应文本。
        """
        pass
    
    @abstractmethod
    def is_available(self):
        """
        检查服务是否可用（API密钥有效、服务可访问等）。
        
        Returns:
            bool: 服务可用返回True，否则返回False。
        """
        pass

    def set_tool_manager(self, tool_manager):
        """
        设置工具管理器实例，以便LLM服务可以访问可用的工具信息。
        
        Args:
            tool_manager (ToolManager): 工具管理器实例。
        """
        self.tool_manager = tool_manager # 存储tool_manager实例

    @abstractmethod
    def get_supported_tool_protocols(self):
        """
        返回此LLM服务支持的工具调用协议列表。
        例如: ['custom_json', 'openai_function_calling']
        
        Returns:
            list[str]: 支持的协议名称列表。
        """
        pass