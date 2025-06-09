"""基础工具抽象类

定义了所有工具必须实现的接口和通用功能。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging

class BaseTool(ABC):
    """所有工具的基础抽象类"""
    
    def __init__(self, config=None, logger=None):
        """初始化工具
        
        Args:
            config: 配置对象
            logger: 日志记录器
        """
        self.config = config
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self.enabled = True
        
    @abstractmethod
    def get_name(self) -> str:
        """获取工具名称"""
        pass
        
    @abstractmethod
    def get_description(self) -> str:
        """获取工具描述"""
        pass
        
    @abstractmethod
    def get_supported_intents(self) -> List[str]:
        """获取支持的意图列表"""
        pass
        
    @abstractmethod
    def execute(self, intent: str, entities: Dict[str, Any], original_text: str) -> str:
        """执行工具功能
        
        Args:
            intent: 意图
            entities: 实体字典
            original_text: 原始文本
            
        Returns:
            执行结果字符串
        """
        pass
        
    def can_handle(self, intent: str) -> bool:
        """检查是否可以处理指定意图
        
        Args:
            intent: 意图字符串
            
        Returns:
            是否可以处理
        """
        return self.enabled and intent in self.get_supported_intents()
        
    def set_enabled(self, enabled: bool):
        """设置工具启用状态
        
        Args:
            enabled: 是否启用
        """
        self.enabled = enabled
        
    def is_enabled(self) -> bool:
        """检查工具是否启用
        
        Returns:
            是否启用
        """
        return self.enabled
        
    def validate_entities(self, required_entities: List[str], entities: Dict[str, Any]) -> Optional[str]:
        """验证必需的实体是否存在
        
        Args:
            required_entities: 必需的实体列表
            entities: 实体字典
            
        Returns:
            如果验证失败，返回错误消息；否则返回None
        """
        missing_entities = []
        for entity in required_entities:
            if entity not in entities or entities[entity] is None:
                missing_entities.append(entity)
                
        if missing_entities:
            return f"缺少必需的参数: {', '.join(missing_entities)}"
            
        return None
        
    def log_execution(self, intent: str, entities: Dict[str, Any], result: str):
        """记录执行日志
        
        Args:
            intent: 意图
            entities: 实体
            result: 执行结果
        """
        self.logger.info(f"Tool {self.get_name()} executed intent '{intent}' with entities {entities}, result: {result}")