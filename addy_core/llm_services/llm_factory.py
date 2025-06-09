# addy_core/llm_services/llm_factory.py

from .openai_service import OpenAIService
from .claude_service import ClaudeService
from .tongyi_service import TongyiService
from .gemini_service import GeminiService

class LLMServiceFactory:
    """
    LLM服务工厂类，用于创建不同的LLM服务实例。
    支持创建OpenAI、Claude、通义千问和Gemini服务。
    """
    
    @staticmethod
    def create_llm_service(config, log_func=None):
        """
        根据配置创建相应的LLM服务实例。

        Args:
            config: 配置对象，包含API密钥等必要信息。
            log_func (callable, optional): 日志记录函数。

        Returns:
            BaseLLMService: LLM服务实例，如果服务类型不支持或配置不正确则返回None。
        """
        service = None
        llm_config_section_name = config.get('NLP', 'llm_service_config_section', fallback='LLM_Service')

        if not config.has_section(llm_config_section_name):
            if log_func:
                log_func(f"Error: LLM configuration section '[{llm_config_section_name}]' not found in config.")
            return None

        llm_config = config[llm_config_section_name]
        api_type = llm_config.get('api_type', '').lower()

        if not api_type:
            if log_func:
                log_func(f"Error: 'api_type' not specified in LLM configuration section '[{llm_config_section_name}]'.")
            return None

        # 传递整个配置对象和特定LLM配置节的名称给服务构造函数
        # 服务内部将负责从 llm_config 中提取所需参数
        if api_type == 'openai_compatible':
            service = OpenAIService(config, llm_config_section_name)
        elif api_type == 'claude':
            service = ClaudeService(config, llm_config_section_name)
        elif api_type == 'tongyi':
            service = TongyiService(config, llm_config_section_name)
        elif api_type == 'gemini':
            service = GeminiService(config, llm_config_section_name)
        # 可以根据需要添加对 'custom' api_type 的处理
        # elif api_type == 'custom':
        #     service = CustomLLMService(config, llm_config_section_name)
        else:
            if log_func:
                log_func(f"Unsupported api_type: {api_type}")

        if service and log_func:
            service.set_logger(log_func)
            
        return service
    
    @staticmethod
    def get_available_services(config, log_func=None):
        """
        获取当前配置的LLM服务实例（如果可用）。
        由于配置已统一，此方法现在只尝试创建并返回一个服务实例。

        Args:
            config: 配置对象，包含API密钥等必要信息。
            log_func (callable, optional): 日志记录函数。

        Returns:
            dict: 如果服务可用，返回包含单个服务实例的字典，键为api_type；否则返回空字典。
        """
        services = {}
        service = LLMServiceFactory.create_llm_service(config, log_func)
        if service and service.is_available():
            llm_config_section_name = config.get('NLP', 'llm_service_config_section', fallback='LLM_Service')
            api_type = config.get(llm_config_section_name, 'api_type', fallback='unknown')
            services[api_type] = service # 使用 api_type 作为键
        return services