"""工具管理器

统一管理所有工具的注册、调用和协调。
"""

import logging
from typing import Dict, Any, List, Optional
from .base_tool import BaseTool
from .file_tool import FileTool
from .system_tool import SystemTool
from .web_tool import WebTool
from .calculator_tool import CalculatorTool
from .weather_tool import WeatherTool
from .email_tool import EmailTool
from .calendar_tool import CalendarTool
from .unit_conversion_tool import UnitConversionTool

class ToolManager:
    """工具管理器类"""
    
    def __init__(self, config=None, logger=None, speak_func=None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.speak = speak_func or (lambda x: print(f"[ToolManager] {x}"))
        
        # 工具注册表
        self.tools: Dict[str, BaseTool] = {}
        
        # 意图到工具的映射
        self.intent_tool_map: Dict[str, str] = {}
        
        # 初始化所有工具
        self._initialize_tools()
        
    def _initialize_tools(self):
        """初始化所有工具"""
        try:
            # 创建工具实例
            tools_to_register = [
                ('file', FileTool(self.config, self.logger, self.speak)),
                ('system', SystemTool(self.config, self.logger, self.speak)),
                ('web', WebTool(self.config, self.logger, self.speak)),
                ('calculator', CalculatorTool(self.config, self.logger, self.speak)),
                ('weather', WeatherTool(self.config, self.logger, self.speak)),
                ('email', EmailTool(self.config, self.logger, self.speak)),
                ('calendar', CalendarTool(self.config, self.logger, self.speak)),
                ('unit_conversion', UnitConversionTool(self.config, self.logger, self.speak))
            ]
            
            # 注册工具
            for tool_name, tool_instance in tools_to_register:
                self.register_tool(tool_name, tool_instance)
                
            self.logger.info(f"工具管理器初始化完成，共注册 {len(self.tools)} 个工具")
            
        except Exception as e:
            self.logger.error(f"工具管理器初始化失败: {e}")
            
    def register_tool(self, tool_name: str, tool: BaseTool):
        """注册工具"""
        try:
            # 检查工具是否启用
            if not tool.is_enabled():
                self.logger.info(f"工具 {tool_name} 已禁用，跳过注册")
                return
                
            # 注册工具
            self.tools[tool_name] = tool
            
            # 注册工具支持的意图
            for intent in tool.get_supported_intents():
                if intent in self.intent_tool_map:
                    self.logger.warning(f"意图 {intent} 已被工具 {self.intent_tool_map[intent]} 注册，现在被工具 {tool_name} 覆盖")
                self.intent_tool_map[intent] = tool_name
                
            self.logger.info(f"工具 {tool_name} ({tool.get_name()}) 注册成功，支持 {len(tool.get_supported_intents())} 个意图")
            
        except Exception as e:
            self.logger.error(f"注册工具 {tool_name} 失败: {e}")
            
    def unregister_tool(self, tool_name: str):
        """注销工具"""
        if tool_name in self.tools:
            tool = self.tools[tool_name]
            
            # 移除意图映射
            intents_to_remove = []
            for intent, mapped_tool in self.intent_tool_map.items():
                if mapped_tool == tool_name:
                    intents_to_remove.append(intent)
                    
            for intent in intents_to_remove:
                del self.intent_tool_map[intent]
                
            # 移除工具
            del self.tools[tool_name]
            
            self.logger.info(f"工具 {tool_name} 已注销")
        else:
            self.logger.warning(f"工具 {tool_name} 不存在，无法注销")
            
    def execute_intent(self, intent: str, entities: Dict[str, Any], original_text: str) -> str:
        """执行意图"""
        self.logger.debug(f"ToolManager.execute_intent called with intent: {intent} (type: {type(intent)}), entities: {entities} (type: {type(entities)}), original_text: {original_text} (type: {type(original_text)})")
        try:
            # 查找处理该意图的工具
            tool_name = self.intent_tool_map.get(intent)
            
            if not tool_name:
                self.logger.warning(f"未找到处理意图 {intent} 的工具")
                return f"unsupported_intent: {intent}"
                
            tool = self.tools.get(tool_name)
            if not tool:
                self.logger.error(f"工具 {tool_name} 不存在")
                return f"tool_not_found: {tool_name}"
                
            # 检查工具是否可以处理该意图
            if not tool.can_handle(intent):
                self.logger.warning(f"工具 {tool_name} 无法处理意图 {intent}")
                return f"tool_cannot_handle: {intent}"
                
            # 执行工具
            self.logger.info(f"使用工具 {tool_name} 执行意图 {intent}")
            result = tool.execute(intent, entities, original_text)
            
            # 记录执行结果
            if result.startswith('error:'):
                self.logger.error(f"工具 {tool_name} 执行意图 {intent} 失败: {result}")
            else:
                self.logger.info(f"工具 {tool_name} 执行意图 {intent} 成功: {result}")
                
            return result
            
        except Exception as e:
            error_msg = f"执行意图 {intent} 时发生异常: {str(e)}"
            self.logger.error(error_msg)
            return f"execution_error: {str(e)}"
            
    def get_available_tools(self) -> List[Dict[str, str]]:
        """获取可用工具列表"""
        tools_info = []
        for tool_name, tool in self.tools.items():
            if tool.is_enabled():
                tools_info.append({
                    'name': tool_name,
                    'display_name': tool.get_name(),
                    'description': tool.get_description(),
                    'supported_intents': tool.get_supported_intents()
                })
        return tools_info
        
    def get_supported_intents(self) -> List[str]:
        """获取所有支持的意图列表"""
        return list(self.intent_tool_map.keys())
        
    def get_tool_for_intent(self, intent: str) -> Optional[str]:
        """获取处理指定意图的工具名称"""
        return self.intent_tool_map.get(intent)
        
    def enable_tool(self, tool_name: str) -> bool:
        """启用工具"""
        if tool_name in self.tools:
            tool = self.tools[tool_name]
            tool.set_enabled(True)
            
            # 重新注册意图映射
            for intent in tool.get_supported_intents():
                self.intent_tool_map[intent] = tool_name
                
            self.logger.info(f"工具 {tool_name} 已启用")
            return True
        else:
            self.logger.warning(f"工具 {tool_name} 不存在")
            return False
            
    def disable_tool(self, tool_name: str) -> bool:
        """禁用工具"""
        if tool_name in self.tools:
            tool = self.tools[tool_name]
            tool.set_enabled(False)
            
            # 移除意图映射
            intents_to_remove = []
            for intent, mapped_tool in self.intent_tool_map.items():
                if mapped_tool == tool_name:
                    intents_to_remove.append(intent)
                    
            for intent in intents_to_remove:
                del self.intent_tool_map[intent]
                
            self.logger.info(f"工具 {tool_name} 已禁用")
            return True
        else:
            self.logger.warning(f"工具 {tool_name} 不存在")
            return False
            
    def get_tool_status(self) -> Dict[str, Dict[str, Any]]:
        """获取所有工具的状态"""
        status = {}
        for tool_name, tool in self.tools.items():
            status[tool_name] = {
                'name': tool.get_name(),
                'description': tool.get_description(),
                'enabled': tool.is_enabled(),
                'supported_intents_count': len(tool.get_supported_intents()),
                'supported_intents': tool.get_supported_intents()
            }
        return status
        
    def search_tools_by_capability(self, capability: str) -> List[str]:
        """根据能力搜索工具"""
        matching_tools = []
        capability_lower = capability.lower()
        
        for tool_name, tool in self.tools.items():
            if not tool.is_enabled():
                continue
                
            # 在工具名称、描述和支持的意图中搜索
            if (capability_lower in tool.get_name().lower() or
                capability_lower in tool.get_description().lower() or
                any(capability_lower in intent.lower() for intent in tool.get_supported_intents())):
                matching_tools.append(tool_name)
                
        return matching_tools
        
    def get_tool_recommendations(self, user_input: str) -> List[Dict[str, Any]]:
        """根据用户输入推荐合适的工具"""
        recommendations = []
        user_input_lower = user_input.lower()
        
        # 关键词到工具的映射
        keyword_tool_map = {
            '文件': ['file'],
            '系统': ['system'],
            '网络': ['web'],
            '计算': ['calculator'],
            '天气': ['weather'],
            '邮件': ['email'],
            '日历': ['calendar'],
            '时间': ['calendar'],
            '提醒': ['calendar'],
            '下载': ['web', 'file'],
            '搜索': ['web', 'file'],
            '发送': ['email'],
            '查询': ['weather', 'web', 'system'],
            '创建': ['file', 'calendar'],
            '删除': ['file', 'calendar'],
            '复制': ['file'],
            '移动': ['file'],
            '重命名': ['file'],
            '关机': ['system'],
            '重启': ['system'],
            '音量': ['system'],
            '进程': ['system'],
            '内存': ['system'],
            'cpu': ['system'],
            '磁盘': ['system']
        }
        
        # 根据关键词匹配工具
        matched_tools = set()
        for keyword, tools in keyword_tool_map.items():
            if keyword in user_input_lower:
                matched_tools.update(tools)
                
        # 为匹配的工具生成推荐
        for tool_name in matched_tools:
            if tool_name in self.tools and self.tools[tool_name].is_enabled():
                tool = self.tools[tool_name]
                recommendations.append({
                    'tool_name': tool_name,
                    'display_name': tool.get_name(),
                    'description': tool.get_description(),
                    'confidence': 0.8  # 简单的置信度评分
                })
                
        # 按置信度排序
        recommendations.sort(key=lambda x: x['confidence'], reverse=True)
        
        return recommendations[:5]  # 返回前5个推荐
        
    def validate_tool_configuration(self) -> Dict[str, List[str]]:
        """验证工具配置"""
        validation_results = {
            'valid_tools': [],
            'invalid_tools': [],
            'warnings': []
        }
        
        for tool_name, tool in self.tools.items():
            try:
                # 检查工具基本功能
                if hasattr(tool, 'validate_configuration'):
                    if tool.validate_configuration():
                        validation_results['valid_tools'].append(tool_name)
                    else:
                        validation_results['invalid_tools'].append(tool_name)
                else:
                    validation_results['valid_tools'].append(tool_name)
                    validation_results['warnings'].append(f"工具 {tool_name} 没有配置验证方法")
                    
            except Exception as e:
                validation_results['invalid_tools'].append(tool_name)
                validation_results['warnings'].append(f"工具 {tool_name} 验证失败: {str(e)}")
                
        return validation_results
        
    def get_tool_usage_stats(self) -> Dict[str, Dict[str, int]]:
        """获取工具使用统计（需要在实际使用中记录）"""
        # 这里返回模拟数据，实际实现需要持久化统计信息
        stats = {}
        for tool_name, tool in self.tools.items():
            stats[tool_name] = {
                'total_calls': 0,
                'successful_calls': 0,
                'failed_calls': 0,
                'avg_execution_time': 0.0
            }
        return stats
        
    def reload_tools(self):
        """重新加载所有工具"""
        self.logger.info("开始重新加载工具...")
        
        # 清空现有工具
        self.tools.clear()
        self.intent_tool_map.clear()
        
        # 重新初始化
        self._initialize_tools()
        
        self.logger.info("工具重新加载完成")
        
    def shutdown(self):
        """关闭工具管理器"""
        self.logger.info("正在关闭工具管理器...")
        
        # 清理资源
        for tool_name, tool in self.tools.items():
            try:
                if hasattr(tool, 'cleanup'):
                    tool.cleanup()
            except Exception as e:
                self.logger.error(f"清理工具 {tool_name} 时发生错误: {e}")
                
        self.tools.clear()
        self.intent_tool_map.clear()
        
        self.logger.info("工具管理器已关闭")