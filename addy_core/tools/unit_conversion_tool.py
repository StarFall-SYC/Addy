"""单位转换工具

提供常用的单位转换功能，例如长度、重量、温度等。
"""

from typing import Dict, Any, List
from .base_tool import BaseTool

class UnitConversionTool(BaseTool):
    """单位转换工具类"""

    def __init__(self, config=None, logger=None, speak_func=None):
        super().__init__(config, logger)
        self.speak = speak_func or (lambda x: print(f"[UnitConversionTool] {x}"))
        # 定义单位转换的映射关系和转换函数
        # 为了简化，这里只实现长度和重量的简单转换
        self.conversions = {
            # 长度
            ('米', '厘米'): lambda x: x * 100,
            ('厘米', '米'): lambda x: x / 100,
            ('米', '千米'): lambda x: x / 1000,
            ('千米', '米'): lambda x: x * 1000,
            ('英寸', '厘米'): lambda x: x * 2.54,
            ('厘米', '英寸'): lambda x: x / 2.54,
            ('英尺', '米'): lambda x: x * 0.3048,
            ('米', '英尺'): lambda x: x / 0.3048,
            # 重量
            ('克', '千克'): lambda x: x / 1000,
            ('千克', '克'): lambda x: x * 1000,
            ('磅', '千克'): lambda x: x * 0.453592,
            ('千克', '磅'): lambda x: x / 0.453592,
        }

    def get_name(self) -> str:
        return "单位转换工具"

    def get_description(self) -> str:
        return "提供常用的单位转换功能，例如长度、重量等。"

    def get_supported_intents(self) -> List[str]:
        return [
            'convert_unit'
        ]

    def execute(self, intent: str, entities: Dict[str, Any], original_text: str) -> str:
        """执行单位转换操作"""
        if intent == 'convert_unit':
            return self._convert_unit(entities)
        else:
            return f"不支持的单位转换操作: {intent}"

    def _convert_unit(self, entities: Dict[str, Any]) -> str:
        """执行单位转换"""
        validation_error = self.validate_entities(['value', 'from_unit', 'to_unit'], entities)
        if validation_error:
            self.speak(validation_error)
            return f"error: {validation_error}"

        try:
            value = float(entities['value'])
            from_unit = entities['from_unit'].lower()
            to_unit = entities['to_unit'].lower()

            # 标准化单位名称
            unit_mapping = {
                "公里": "千米",
                "公斤": "千克"
            }
            from_unit = unit_mapping.get(from_unit, from_unit)
            to_unit = unit_mapping.get(to_unit, to_unit)

            # 尝试直接转换
            if (from_unit, to_unit) in self.conversions:
                result = self.conversions[(from_unit, to_unit)](value)
                self.speak(f"{value} {from_unit} 等于 {result:.2f} {to_unit}")
                return f"conversion_result: {result:.2f} {to_unit}"
            # 尝试通过中间单位（例如米或千克）进行转换
            else:
                # 查找通用的基本单位（例如长度的'米'，重量的'千克'）
                base_unit_found = False
                # 尝试转换为基本单位
                for (u1, u2), func in self.conversions.items():
                    if u1 == from_unit and (u2 == '米' or u2 == '千克'): # 假设米和千克是基本单位
                        value_in_base = func(value)
                        # 尝试从基本单位转换为目标单位
                        for (bu1, bu2), func2 in self.conversions.items():
                            if bu1 == u2 and bu2 == to_unit:
                                result = func2(value_in_base)
                                self.speak(f"{value} {from_unit} 等于 {result:.2f} {to_unit}")
                                return f"conversion_result: {result:.2f} {to_unit}"
                        base_unit_found = True
                        break

            # 如果直接和间接转换都失败
            self.speak(f"抱歉，不支持从 {from_unit} 到 {to_unit} 的转换。")
            return f"error: unsupported_conversion: {from_unit}_to_{to_unit}"

        except ValueError:
            self.speak("输入的值无效，请输入数字。")
            return "error: invalid_value_for_conversion"
        except Exception as e:
            error_msg = f"单位转换失败: {str(e)}"
            self.speak(error_msg)
            self.logger.error(error_msg)
            return f"error: {str(e)}"