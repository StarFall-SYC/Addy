"""计算器工具

提供基础数学计算、科学计算、单位转换等功能。
"""

import math
import re
from typing import Dict, Any, List
from .base_tool import BaseTool

class CalculatorTool(BaseTool):
    """计算器工具类"""
    
    def __init__(self, config=None, logger=None, speak_func=None):
        super().__init__(config, logger)
        self.speak = speak_func or (lambda x: print(f"[CalculatorTool] {x}"))
        
    def get_name(self) -> str:
        return "计算器工具"
        
    def get_description(self) -> str:
        return "提供基础数学计算、科学计算、单位转换等功能"
        
    def get_supported_intents(self) -> List[str]:
        return [
            'calculate',
            'calculate_basic',
            'calculate_scientific',
            'convert_units',
            'convert_temperature',
            'convert_currency',
            'calculate_percentage',
            'calculate_area',
            'calculate_volume',
            'solve_equation',
            'generate_random',
            'calculate_statistics'
        ]
        
    def execute(self, intent: str, entities: Dict[str, Any], original_text: str) -> str:
        """执行计算操作"""
        try:
            if intent in ['calculate', 'calculate_basic']:
                return self._calculate_basic(entities)
            elif intent == 'calculate_scientific':
                return self._calculate_scientific(entities)
            elif intent == 'convert_units':
                return self._convert_units(entities)
            elif intent == 'convert_temperature':
                return self._convert_temperature(entities)
            elif intent == 'convert_currency':
                return self._convert_currency(entities)
            elif intent == 'calculate_percentage':
                return self._calculate_percentage(entities)
            elif intent == 'calculate_area':
                return self._calculate_area(entities)
            elif intent == 'calculate_volume':
                return self._calculate_volume(entities)
            elif intent == 'solve_equation':
                return self._solve_equation(entities)
            elif intent == 'generate_random':
                return self._generate_random(entities)
            elif intent == 'calculate_statistics':
                return self._calculate_statistics(entities)
            else:
                return f"不支持的计算操作: {intent}"
                
        except Exception as e:
            error_msg = f"计算失败: {str(e)}"
            self.speak(error_msg)
            self.logger.error(error_msg)
            return f"error: {str(e)}"
            
    def _calculate_basic(self, entities: Dict[str, Any]) -> str:
        """基础数学计算"""
        expression = entities.get('expression') or entities.get('text')
        
        if not expression:
            self.speak("请提供要计算的表达式")
            return "error: missing_expression"
            
        try:
            # 清理表达式，只保留安全的字符
            safe_expression = re.sub(r'[^0-9+\-*/().\s]', '', expression)
            safe_expression = safe_expression.replace('×', '*').replace('÷', '/')
            
            # 使用eval进行计算（注意：这里只允许安全的数学表达式）
            result = eval(safe_expression)
            
            self.speak(f"计算结果: {expression} = {result}")
            return f"calculation_result: {result}"
            
        except (ValueError, SyntaxError, ZeroDivisionError) as e:
            error_msg = f"计算表达式错误: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _calculate_scientific(self, entities: Dict[str, Any]) -> str:
        """科学计算"""
        function = entities.get('function')
        value = entities.get('value')
        
        if not function or value is None:
            self.speak("请指定计算函数和数值")
            return "error: missing_function_or_value"
            
        try:
            value = float(value)
            
            if function in ['sin', 'sine']:
                result = math.sin(math.radians(value))
                self.speak(f"sin({value}°) = {result}")
            elif function in ['cos', 'cosine']:
                result = math.cos(math.radians(value))
                self.speak(f"cos({value}°) = {result}")
            elif function in ['tan', 'tangent']:
                result = math.tan(math.radians(value))
                self.speak(f"tan({value}°) = {result}")
            elif function in ['log', 'logarithm']:
                result = math.log10(value)
                self.speak(f"log({value}) = {result}")
            elif function in ['ln', 'natural_log']:
                result = math.log(value)
                self.speak(f"ln({value}) = {result}")
            elif function in ['sqrt', 'square_root']:
                result = math.sqrt(value)
                self.speak(f"√{value} = {result}")
            elif function in ['exp', 'exponential']:
                result = math.exp(value)
                self.speak(f"e^{value} = {result}")
            elif function in ['factorial']:
                if value != int(value) or value < 0:
                    self.speak("阶乘只能计算非负整数")
                    return "error: invalid_factorial_input"
                result = math.factorial(int(value))
                self.speak(f"{int(value)}! = {result}")
            else:
                self.speak(f"不支持的科学计算函数: {function}")
                return f"error: unsupported_function: {function}"
                
            return f"scientific_calculation_result: {result}"
            
        except (ValueError, OverflowError) as e:
            error_msg = f"科学计算错误: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _convert_units(self, entities: Dict[str, Any]) -> str:
        """单位转换"""
        value = entities.get('value')
        from_unit = entities.get('from_unit')
        to_unit = entities.get('to_unit')
        
        if not all([value, from_unit, to_unit]):
            self.speak("请提供数值、源单位和目标单位")
            return "error: missing_conversion_parameters"
            
        try:
            value = float(value)
            
            # 长度转换
            length_units = {
                'mm': 0.001, 'cm': 0.01, 'm': 1, 'km': 1000,
                'inch': 0.0254, 'ft': 0.3048, 'yard': 0.9144, 'mile': 1609.34
            }
            
            # 重量转换
            weight_units = {
                'mg': 0.001, 'g': 1, 'kg': 1000, 'ton': 1000000,
                'oz': 28.3495, 'lb': 453.592
            }
            
            # 面积转换
            area_units = {
                'mm2': 0.000001, 'cm2': 0.0001, 'm2': 1, 'km2': 1000000,
                'inch2': 0.00064516, 'ft2': 0.092903
            }
            
            # 体积转换
            volume_units = {
                'ml': 0.001, 'l': 1, 'm3': 1000,
                'cup': 0.236588, 'pint': 0.473176, 'quart': 0.946353, 'gallon': 3.78541
            }
            
            # 选择合适的转换表
            if from_unit in length_units and to_unit in length_units:
                conversion_table = length_units
                unit_type = "长度"
            elif from_unit in weight_units and to_unit in weight_units:
                conversion_table = weight_units
                unit_type = "重量"
            elif from_unit in area_units and to_unit in area_units:
                conversion_table = area_units
                unit_type = "面积"
            elif from_unit in volume_units and to_unit in volume_units:
                conversion_table = volume_units
                unit_type = "体积"
            else:
                self.speak(f"不支持从 {from_unit} 到 {to_unit} 的转换")
                return f"error: unsupported_conversion: {from_unit} -> {to_unit}"
                
            # 执行转换
            base_value = value * conversion_table[from_unit]
            result = base_value / conversion_table[to_unit]
            
            self.speak(f"{unit_type}转换: {value} {from_unit} = {result} {to_unit}")
            return f"unit_conversion_result: {result} {to_unit}"
            
        except (ValueError, KeyError) as e:
            error_msg = f"单位转换错误: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _convert_temperature(self, entities: Dict[str, Any]) -> str:
        """温度转换"""
        value = entities.get('value')
        from_unit = entities.get('from_unit', '').lower()
        to_unit = entities.get('to_unit', '').lower()
        
        if not all([value, from_unit, to_unit]):
            self.speak("请提供温度值、源单位和目标单位")
            return "error: missing_temperature_parameters"
            
        try:
            value = float(value)
            
            # 转换为摄氏度
            if from_unit in ['c', 'celsius', '摄氏度']:
                celsius = value
            elif from_unit in ['f', 'fahrenheit', '华氏度']:
                celsius = (value - 32) * 5/9
            elif from_unit in ['k', 'kelvin', '开尔文']:
                celsius = value - 273.15
            else:
                self.speak(f"不支持的温度单位: {from_unit}")
                return f"error: unsupported_temperature_unit: {from_unit}"
                
            # 从摄氏度转换到目标单位
            if to_unit in ['c', 'celsius', '摄氏度']:
                result = celsius
                unit_name = "°C"
            elif to_unit in ['f', 'fahrenheit', '华氏度']:
                result = celsius * 9/5 + 32
                unit_name = "°F"
            elif to_unit in ['k', 'kelvin', '开尔文']:
                result = celsius + 273.15
                unit_name = "K"
            else:
                self.speak(f"不支持的温度单位: {to_unit}")
                return f"error: unsupported_temperature_unit: {to_unit}"
                
            self.speak(f"温度转换: {value}° {from_unit.upper()} = {result:.2f} {unit_name}")
            return f"temperature_conversion_result: {result:.2f} {unit_name}"
            
        except ValueError as e:
            error_msg = f"温度转换错误: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _calculate_percentage(self, entities: Dict[str, Any]) -> str:
        """百分比计算"""
        operation = entities.get('operation', 'of')  # of, increase, decrease
        value1 = entities.get('value1')
        value2 = entities.get('value2')
        percentage = entities.get('percentage')
        
        try:
            if operation == 'of' and percentage and value1:
                # X% of Y
                percentage = float(percentage)
                value1 = float(value1)
                result = (percentage / 100) * value1
                self.speak(f"{percentage}% of {value1} = {result}")
                return f"percentage_result: {result}"
                
            elif operation == 'increase' and value1 and percentage:
                # 增加X%
                value1 = float(value1)
                percentage = float(percentage)
                result = value1 * (1 + percentage / 100)
                self.speak(f"{value1} 增加 {percentage}% = {result}")
                return f"percentage_increase_result: {result}"
                
            elif operation == 'decrease' and value1 and percentage:
                # 减少X%
                value1 = float(value1)
                percentage = float(percentage)
                result = value1 * (1 - percentage / 100)
                self.speak(f"{value1} 减少 {percentage}% = {result}")
                return f"percentage_decrease_result: {result}"
                
            elif operation == 'ratio' and value1 and value2:
                # X是Y的百分之几
                value1 = float(value1)
                value2 = float(value2)
                result = (value1 / value2) * 100
                self.speak(f"{value1} 是 {value2} 的 {result:.2f}%")
                return f"percentage_ratio_result: {result:.2f}%"
                
            else:
                self.speak("请提供正确的百分比计算参数")
                return "error: invalid_percentage_parameters"
                
        except (ValueError, ZeroDivisionError) as e:
            error_msg = f"百分比计算错误: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _calculate_area(self, entities: Dict[str, Any]) -> str:
        """面积计算"""
        shape = entities.get('shape')
        
        try:
            if shape == 'rectangle':
                length = float(entities.get('length', 0))
                width = float(entities.get('width', 0))
                result = length * width
                self.speak(f"矩形面积: {length} × {width} = {result}")
                
            elif shape == 'square':
                side = float(entities.get('side', 0))
                result = side * side
                self.speak(f"正方形面积: {side}² = {result}")
                
            elif shape == 'circle':
                radius = float(entities.get('radius', 0))
                result = math.pi * radius * radius
                self.speak(f"圆形面积: π × {radius}² = {result:.2f}")
                
            elif shape == 'triangle':
                base = float(entities.get('base', 0))
                height = float(entities.get('height', 0))
                result = 0.5 * base * height
                self.speak(f"三角形面积: 0.5 × {base} × {height} = {result}")
                
            else:
                self.speak(f"不支持的形状: {shape}")
                return f"error: unsupported_shape: {shape}"
                
            return f"area_calculation_result: {result}"
            
        except (ValueError, TypeError) as e:
            error_msg = f"面积计算错误: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _calculate_volume(self, entities: Dict[str, Any]) -> str:
        """体积计算"""
        shape = entities.get('shape')
        
        try:
            if shape == 'cube':
                side = float(entities.get('side', 0))
                result = side ** 3
                self.speak(f"立方体体积: {side}³ = {result}")
                
            elif shape == 'rectangular_prism':
                length = float(entities.get('length', 0))
                width = float(entities.get('width', 0))
                height = float(entities.get('height', 0))
                result = length * width * height
                self.speak(f"长方体体积: {length} × {width} × {height} = {result}")
                
            elif shape == 'sphere':
                radius = float(entities.get('radius', 0))
                result = (4/3) * math.pi * (radius ** 3)
                self.speak(f"球体体积: (4/3) × π × {radius}³ = {result:.2f}")
                
            elif shape == 'cylinder':
                radius = float(entities.get('radius', 0))
                height = float(entities.get('height', 0))
                result = math.pi * (radius ** 2) * height
                self.speak(f"圆柱体体积: π × {radius}² × {height} = {result:.2f}")
                
            else:
                self.speak(f"不支持的形状: {shape}")
                return f"error: unsupported_shape: {shape}"
                
            return f"volume_calculation_result: {result}"
            
        except (ValueError, TypeError) as e:
            error_msg = f"体积计算错误: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _generate_random(self, entities: Dict[str, Any]) -> str:
        """生成随机数"""
        import random
        
        min_val = entities.get('min', 1)
        max_val = entities.get('max', 100)
        count = entities.get('count', 1)
        
        try:
            min_val = int(min_val)
            max_val = int(max_val)
            count = int(count)
            
            if count == 1:
                result = random.randint(min_val, max_val)
                self.speak(f"随机数 ({min_val}-{max_val}): {result}")
                return f"random_number: {result}"
            else:
                results = [random.randint(min_val, max_val) for _ in range(count)]
                self.speak(f"{count}个随机数 ({min_val}-{max_val}): {', '.join(map(str, results))}")
                return f"random_numbers: {results}"
                
        except ValueError as e:
            error_msg = f"生成随机数错误: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _calculate_statistics(self, entities: Dict[str, Any]) -> str:
        """统计计算"""
        numbers = entities.get('numbers', [])
        operation = entities.get('operation', 'all')  # mean, median, mode, std, all
        
        if not numbers:
            self.speak("请提供数字列表")
            return "error: missing_numbers"
            
        try:
            # 转换为浮点数列表
            if isinstance(numbers, str):
                numbers = [float(x.strip()) for x in numbers.split(',')]
            else:
                numbers = [float(x) for x in numbers]
                
            if not numbers:
                self.speak("数字列表为空")
                return "error: empty_numbers_list"
                
            results = {}
            
            if operation in ['mean', 'all']:
                results['平均值'] = sum(numbers) / len(numbers)
                
            if operation in ['median', 'all']:
                sorted_numbers = sorted(numbers)
                n = len(sorted_numbers)
                if n % 2 == 0:
                    results['中位数'] = (sorted_numbers[n//2-1] + sorted_numbers[n//2]) / 2
                else:
                    results['中位数'] = sorted_numbers[n//2]
                    
            if operation in ['mode', 'all']:
                from collections import Counter
                counter = Counter(numbers)
                max_count = max(counter.values())
                modes = [k for k, v in counter.items() if v == max_count]
                results['众数'] = modes[0] if len(modes) == 1 else modes
                
            if operation in ['std', 'all']:
                mean = sum(numbers) / len(numbers)
                variance = sum((x - mean) ** 2 for x in numbers) / len(numbers)
                results['标准差'] = math.sqrt(variance)
                
            if operation in ['all']:
                results['最小值'] = min(numbers)
                results['最大值'] = max(numbers)
                results['总和'] = sum(numbers)
                results['数量'] = len(numbers)
                
            # 格式化输出
            output = "统计结果:\n"
            for key, value in results.items():
                if isinstance(value, float):
                    output += f"{key}: {value:.2f}\n"
                else:
                    output += f"{key}: {value}\n"
                    
            self.speak(output)
            return f"statistics_calculated: {operation}"
            
        except (ValueError, TypeError) as e:
            error_msg = f"统计计算错误: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _solve_equation(self, entities: Dict[str, Any]) -> str:
        """解方程（简单的一元一次方程）"""
        equation = entities.get('equation')
        
        if not equation:
            self.speak("请提供要解的方程")
            return "error: missing_equation"
            
        try:
            # 简单的一元一次方程求解 ax + b = c
            # 例如: 2x + 3 = 7
            equation = equation.replace(' ', '').replace('=', '==').lower()
            
            # 这里只是一个简单的示例，实际应该使用更复杂的解析器
            if 'x' in equation:
                # 尝试数值求解
                for x in range(-1000, 1001):
                    try:
                        if eval(equation.replace('x', str(x))):
                            self.speak(f"方程解: x = {x}")
                            return f"equation_solved: x = {x}"
                    except:
                        continue
                        
                self.speak("无法求解该方程")
                return "error: equation_unsolvable"
            else:
                self.speak("方程中没有找到变量x")
                return "error: no_variable_found"
                
        except Exception as e:
            error_msg = f"解方程错误: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _convert_currency(self, entities: Dict[str, Any]) -> str:
        """货币转换（需要API）"""
        amount = entities.get('amount')
        from_currency = entities.get('from_currency', 'USD')
        to_currency = entities.get('to_currency', 'CNY')
        
        if not amount:
            self.speak("请提供要转换的金额")
            return "error: missing_amount"
            
        try:
            amount = float(amount)
            
            # 这里应该调用实际的汇率API
            # 为了演示，使用固定汇率
            exchange_rates = {
                ('USD', 'CNY'): 7.2,
                ('CNY', 'USD'): 1/7.2,
                ('EUR', 'CNY'): 7.8,
                ('CNY', 'EUR'): 1/7.8,
                ('JPY', 'CNY'): 0.05,
                ('CNY', 'JPY'): 20
            }
            
            rate_key = (from_currency.upper(), to_currency.upper())
            if rate_key in exchange_rates:
                result = amount * exchange_rates[rate_key]
                self.speak(f"货币转换: {amount} {from_currency} = {result:.2f} {to_currency}")
                return f"currency_conversion_result: {result:.2f} {to_currency}"
            else:
                self.speak(f"不支持 {from_currency} 到 {to_currency} 的转换")
                return f"error: unsupported_currency_pair: {from_currency}-{to_currency}"
                
        except ValueError as e:
            error_msg = f"货币转换错误: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"