"""天气工具

提供天气查询、天气预报、天气警报等功能。
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
from .base_tool import BaseTool

class WeatherTool(BaseTool):
    """天气工具类"""
    
    def __init__(self, config=None, logger=None, speak_func=None):
        super().__init__(config, logger)
        self.speak = speak_func or (lambda x: print(f"[WeatherTool] {x}"))
        self.api_key = None
        if config:
            self.api_key = config.get('Weather', 'api_key', fallback=None)
        
    def get_name(self) -> str:
        return "天气工具"
        
    def get_description(self) -> str:
        return "提供天气查询、天气预报、天气警报等功能"
        
    def get_supported_intents(self) -> List[str]:
        return [
            'get_weather',
            'get_weather_forecast',
            'get_weather_alerts',
            'get_air_quality',
            'get_uv_index',
            'get_sunrise_sunset',
            'compare_weather',
            'get_weather_history'
        ]
        
    def execute(self, intent: str, entities: Dict[str, Any], original_text: str) -> str:
        """执行天气操作"""
        try:
            if intent == 'get_weather':
                return self._get_weather(entities)
            elif intent == 'get_weather_forecast':
                return self._get_weather_forecast(entities)
            elif intent == 'get_weather_alerts':
                return self._get_weather_alerts(entities)
            elif intent == 'get_air_quality':
                return self._get_air_quality(entities)
            elif intent == 'get_uv_index':
                return self._get_uv_index(entities)
            elif intent == 'get_sunrise_sunset':
                return self._get_sunrise_sunset(entities)
            elif intent == 'compare_weather':
                return self._compare_weather(entities)
            elif intent == 'get_weather_history':
                return self._get_weather_history(entities)
            else:
                return f"不支持的天气操作: {intent}"
                
        except Exception as e:
            error_msg = f"天气查询失败: {str(e)}"
            self.speak(error_msg)
            self.logger.error(error_msg)
            return f"error: {str(e)}"
            
    def _check_api_key(self) -> bool:
        """检查API密钥是否可用"""
        if not self.api_key:
            self.speak("请在配置文件中设置天气API密钥")
            return False
        return True
        
    def _get_weather(self, entities: Dict[str, Any]) -> str:
        """获取当前天气"""
        if not self._check_api_key():
            return "error: missing_api_key"
            
        city = entities.get('city', '北京')
        units = entities.get('units', 'metric')  # metric, imperial, kelvin
        
        try:
            # 使用OpenWeatherMap API
            url = "http://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': city,
                'appid': self.api_key,
                'units': units,
                'lang': 'zh_cn'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('cod') == 200:
                weather_info = self._format_current_weather(data, city)
                self.speak(weather_info)
                return f"weather_retrieved: {city}"
            else:
                error_msg = f"获取天气信息失败: {data.get('message', '未知错误')}"
                self.speak(error_msg)
                return f"error: {data.get('message')}"
                
        except requests.exceptions.RequestException as e:
            error_msg = f"天气API请求失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _format_current_weather(self, data: Dict, city: str) -> str:
        """格式化当前天气信息"""
        main = data['main']
        weather = data['weather'][0]
        wind = data.get('wind', {})
        
        info = f"{city}当前天气:\n"
        info += f"天气: {weather['description']}\n"
        info += f"温度: {main['temp']}°C\n"
        info += f"体感温度: {main['feels_like']}°C\n"
        info += f"湿度: {main['humidity']}%\n"
        info += f"气压: {main['pressure']} hPa\n"
        
        if 'speed' in wind:
            info += f"风速: {wind['speed']} m/s\n"
        if 'deg' in wind:
            info += f"风向: {wind['deg']}°\n"
            
        if 'visibility' in data:
            info += f"能见度: {data['visibility']/1000} km\n"
            
        return info
        
    def _get_weather_forecast(self, entities: Dict[str, Any]) -> str:
        """获取天气预报"""
        if not self._check_api_key():
            return "error: missing_api_key"
            
        city = entities.get('city', '北京')
        days = entities.get('days', 5)
        units = entities.get('units', 'metric')
        
        try:
            # 使用OpenWeatherMap 5天预报API
            url = "http://api.openweathermap.org/data/2.5/forecast"
            params = {
                'q': city,
                'appid': self.api_key,
                'units': units,
                'lang': 'zh_cn'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('cod') == '200':
                forecast_info = self._format_forecast(data, city, days)
                self.speak(forecast_info)
                return f"weather_forecast_retrieved: {city}"
            else:
                error_msg = f"获取天气预报失败: {data.get('message', '未知错误')}"
                self.speak(error_msg)
                return f"error: {data.get('message')}"
                
        except requests.exceptions.RequestException as e:
            error_msg = f"天气预报API请求失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _format_forecast(self, data: Dict, city: str, days: int) -> str:
        """格式化天气预报信息"""
        forecasts = data['list']
        
        info = f"{city}未来{days}天天气预报:\n"
        
        # 按天分组预报数据
        daily_forecasts = {}
        for forecast in forecasts:
            date = datetime.fromtimestamp(forecast['dt']).date()
            if date not in daily_forecasts:
                daily_forecasts[date] = []
            daily_forecasts[date].append(forecast)
            
        # 取前N天的数据
        sorted_dates = sorted(daily_forecasts.keys())[:days]
        
        for date in sorted_dates:
            day_forecasts = daily_forecasts[date]
            
            # 计算当天的平均温度和主要天气
            temps = [f['main']['temp'] for f in day_forecasts]
            avg_temp = sum(temps) / len(temps)
            min_temp = min(temps)
            max_temp = max(temps)
            
            # 取最常见的天气描述
            weather_descriptions = [f['weather'][0]['description'] for f in day_forecasts]
            main_weather = max(set(weather_descriptions), key=weather_descriptions.count)
            
            info += f"{date.strftime('%m月%d日')}: {main_weather}, {min_temp:.0f}°C - {max_temp:.0f}°C\n"
            
        return info
        
    def _get_weather_alerts(self, entities: Dict[str, Any]) -> str:
        """获取天气警报"""
        if not self._check_api_key():
            return "error: missing_api_key"
            
        city = entities.get('city', '北京')
        
        try:
            # 首先获取城市坐标
            geocoding_url = "http://api.openweathermap.org/geo/1.0/direct"
            geocoding_params = {
                'q': city,
                'appid': self.api_key,
                'limit': 1
            }
            
            geo_response = requests.get(geocoding_url, params=geocoding_params, timeout=10)
            geo_response.raise_for_status()
            geo_data = geo_response.json()
            
            if not geo_data:
                self.speak(f"未找到城市: {city}")
                return f"error: city_not_found: {city}"
                
            lat = geo_data[0]['lat']
            lon = geo_data[0]['lon']
            
            # 获取天气警报
            alerts_url = "http://api.openweathermap.org/data/2.5/onecall"
            alerts_params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'exclude': 'minutely,hourly,daily',
                'lang': 'zh_cn'
            }
            
            alerts_response = requests.get(alerts_url, params=alerts_params, timeout=10)
            alerts_response.raise_for_status()
            alerts_data = alerts_response.json()
            
            if 'alerts' in alerts_data and alerts_data['alerts']:
                alerts_info = f"{city}天气警报:\n"
                for alert in alerts_data['alerts']:
                    start_time = datetime.fromtimestamp(alert['start']).strftime('%m月%d日 %H:%M')
                    end_time = datetime.fromtimestamp(alert['end']).strftime('%m月%d日 %H:%M')
                    alerts_info += f"警报: {alert['event']}\n"
                    alerts_info += f"时间: {start_time} - {end_time}\n"
                    alerts_info += f"描述: {alert['description']}\n\n"
                    
                self.speak(alerts_info)
                return f"weather_alerts_retrieved: {len(alerts_data['alerts'])}"
            else:
                self.speak(f"{city}当前没有天气警报")
                return "no_weather_alerts"
                
        except requests.exceptions.RequestException as e:
            error_msg = f"天气警报API请求失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _get_air_quality(self, entities: Dict[str, Any]) -> str:
        """获取空气质量"""
        if not self._check_api_key():
            return "error: missing_api_key"
            
        city = entities.get('city', '北京')
        
        try:
            # 首先获取城市坐标
            geocoding_url = "http://api.openweathermap.org/geo/1.0/direct"
            geocoding_params = {
                'q': city,
                'appid': self.api_key,
                'limit': 1
            }
            
            geo_response = requests.get(geocoding_url, params=geocoding_params, timeout=10)
            geo_response.raise_for_status()
            geo_data = geo_response.json()
            
            if not geo_data:
                self.speak(f"未找到城市: {city}")
                return f"error: city_not_found: {city}"
                
            lat = geo_data[0]['lat']
            lon = geo_data[0]['lon']
            
            # 获取空气质量数据
            air_url = "http://api.openweathermap.org/data/2.5/air_pollution"
            air_params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key
            }
            
            air_response = requests.get(air_url, params=air_params, timeout=10)
            air_response.raise_for_status()
            air_data = air_response.json()
            
            if 'list' in air_data and air_data['list']:
                air_info = self._format_air_quality(air_data['list'][0], city)
                self.speak(air_info)
                return f"air_quality_retrieved: {city}"
            else:
                self.speak(f"无法获取{city}的空气质量数据")
                return "error: no_air_quality_data"
                
        except requests.exceptions.RequestException as e:
            error_msg = f"空气质量API请求失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _format_air_quality(self, data: Dict, city: str) -> str:
        """格式化空气质量信息"""
        aqi = data['main']['aqi']
        components = data['components']
        
        aqi_levels = {
            1: "优秀",
            2: "良好", 
            3: "中等",
            4: "较差",
            5: "很差"
        }
        
        info = f"{city}空气质量:\n"
        info += f"空气质量指数: {aqi} ({aqi_levels.get(aqi, '未知')})\n"
        info += f"CO: {components.get('co', 'N/A')} μg/m³\n"
        info += f"NO: {components.get('no', 'N/A')} μg/m³\n"
        info += f"NO2: {components.get('no2', 'N/A')} μg/m³\n"
        info += f"O3: {components.get('o3', 'N/A')} μg/m³\n"
        info += f"SO2: {components.get('so2', 'N/A')} μg/m³\n"
        info += f"PM2.5: {components.get('pm2_5', 'N/A')} μg/m³\n"
        info += f"PM10: {components.get('pm10', 'N/A')} μg/m³\n"
        
        return info
        
    def _get_uv_index(self, entities: Dict[str, Any]) -> str:
        """获取紫外线指数"""
        if not self._check_api_key():
            return "error: missing_api_key"
            
        city = entities.get('city', '北京')
        
        try:
            # 首先获取城市坐标
            geocoding_url = "http://api.openweathermap.org/geo/1.0/direct"
            geocoding_params = {
                'q': city,
                'appid': self.api_key,
                'limit': 1
            }
            
            geo_response = requests.get(geocoding_url, params=geocoding_params, timeout=10)
            geo_response.raise_for_status()
            geo_data = geo_response.json()
            
            if not geo_data:
                self.speak(f"未找到城市: {city}")
                return f"error: city_not_found: {city}"
                
            lat = geo_data[0]['lat']
            lon = geo_data[0]['lon']
            
            # 获取UV指数（使用OneCall API）
            uv_url = "http://api.openweathermap.org/data/2.5/onecall"
            uv_params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'exclude': 'minutely,hourly,daily,alerts'
            }
            
            uv_response = requests.get(uv_url, params=uv_params, timeout=10)
            uv_response.raise_for_status()
            uv_data = uv_response.json()
            
            if 'current' in uv_data and 'uvi' in uv_data['current']:
                uv_index = uv_data['current']['uvi']
                uv_info = self._format_uv_index(uv_index, city)
                self.speak(uv_info)
                return f"uv_index_retrieved: {city}"
            else:
                self.speak(f"无法获取{city}的紫外线指数")
                return "error: no_uv_data"
                
        except requests.exceptions.RequestException as e:
            error_msg = f"紫外线指数API请求失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _format_uv_index(self, uv_index: float, city: str) -> str:
        """格式化紫外线指数信息"""
        if uv_index <= 2:
            level = "低"
            advice = "无需防护"
        elif uv_index <= 5:
            level = "中等"
            advice = "建议戴帽子和太阳镜"
        elif uv_index <= 7:
            level = "高"
            advice = "建议使用防晒霜，戴帽子和太阳镜"
        elif uv_index <= 10:
            level = "很高"
            advice = "必须使用防晒霜，避免长时间暴露在阳光下"
        else:
            level = "极高"
            advice = "避免外出，必要时采取全面防护措施"
            
        info = f"{city}紫外线指数:\n"
        info += f"UV指数: {uv_index} ({level})\n"
        info += f"建议: {advice}\n"
        
        return info
        
    def _get_sunrise_sunset(self, entities: Dict[str, Any]) -> str:
        """获取日出日落时间"""
        if not self._check_api_key():
            return "error: missing_api_key"
            
        city = entities.get('city', '北京')
        
        try:
            # 使用当前天气API获取日出日落时间
            url = "http://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': city,
                'appid': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('cod') == 200 and 'sys' in data:
                sunrise = datetime.fromtimestamp(data['sys']['sunrise'])
                sunset = datetime.fromtimestamp(data['sys']['sunset'])
                
                info = f"{city}日出日落时间:\n"
                info += f"日出: {sunrise.strftime('%H:%M')}\n"
                info += f"日落: {sunset.strftime('%H:%M')}\n"
                
                # 计算日照时长
                daylight_duration = sunset - sunrise
                hours = daylight_duration.seconds // 3600
                minutes = (daylight_duration.seconds % 3600) // 60
                info += f"日照时长: {hours}小时{minutes}分钟\n"
                
                self.speak(info)
                return f"sunrise_sunset_retrieved: {city}"
            else:
                error_msg = f"获取日出日落时间失败: {data.get('message', '未知错误')}"
                self.speak(error_msg)
                return f"error: {data.get('message')}"
                
        except requests.exceptions.RequestException as e:
            error_msg = f"日出日落API请求失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _compare_weather(self, entities: Dict[str, Any]) -> str:
        """比较多个城市的天气"""
        if not self._check_api_key():
            return "error: missing_api_key"
            
        cities = entities.get('cities', [])
        if len(cities) < 2:
            self.speak("请提供至少两个城市进行比较")
            return "error: insufficient_cities"
            
        try:
            weather_data = []
            
            for city in cities:
                url = "http://api.openweathermap.org/data/2.5/weather"
                params = {
                    'q': city,
                    'appid': self.api_key,
                    'units': 'metric',
                    'lang': 'zh_cn'
                }
                
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    weather_data.append({
                        'city': city,
                        'temp': data['main']['temp'],
                        'description': data['weather'][0]['description'],
                        'humidity': data['main']['humidity']
                    })
                    
            if weather_data:
                comparison_info = "城市天气比较:\n"
                for weather in weather_data:
                    comparison_info += f"{weather['city']}: {weather['temp']}°C, {weather['description']}, 湿度{weather['humidity']}%\n"
                    
                self.speak(comparison_info)
                return f"weather_comparison_completed: {len(weather_data)} cities"
            else:
                self.speak("无法获取任何城市的天气数据")
                return "error: no_weather_data"
                
        except requests.exceptions.RequestException as e:
            error_msg = f"天气比较API请求失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _get_weather_history(self, entities: Dict[str, Any]) -> str:
        """获取历史天气数据"""
        if not self._check_api_key():
            return "error: missing_api_key"
            
        city = entities.get('city', '北京')
        date = entities.get('date')  # 格式: YYYY-MM-DD
        
        if not date:
            self.speak("请提供要查询的日期")
            return "error: missing_date"
            
        try:
            # 解析日期
            target_date = datetime.strptime(date, '%Y-%m-%d')
            timestamp = int(target_date.timestamp())
            
            # 首先获取城市坐标
            geocoding_url = "http://api.openweathermap.org/geo/1.0/direct"
            geocoding_params = {
                'q': city,
                'appid': self.api_key,
                'limit': 1
            }
            
            geo_response = requests.get(geocoding_url, params=geocoding_params, timeout=10)
            geo_response.raise_for_status()
            geo_data = geo_response.json()
            
            if not geo_data:
                self.speak(f"未找到城市: {city}")
                return f"error: city_not_found: {city}"
                
            lat = geo_data[0]['lat']
            lon = geo_data[0]['lon']
            
            # 获取历史天气数据（需要付费API）
            history_url = "http://api.openweathermap.org/data/2.5/onecall/timemachine"
            history_params = {
                'lat': lat,
                'lon': lon,
                'dt': timestamp,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'zh_cn'
            }
            
            history_response = requests.get(history_url, params=history_params, timeout=10)
            
            if history_response.status_code == 200:
                history_data = history_response.json()
                history_info = self._format_weather_history(history_data, city, date)
                self.speak(history_info)
                return f"weather_history_retrieved: {city} {date}"
            else:
                self.speak("历史天气数据需要付费API，当前无法获取")
                return "error: historical_data_requires_paid_api"
                
        except ValueError:
            self.speak("日期格式错误，请使用YYYY-MM-DD格式")
            return "error: invalid_date_format"
        except requests.exceptions.RequestException as e:
            error_msg = f"历史天气API请求失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _format_weather_history(self, data: Dict, city: str, date: str) -> str:
        """格式化历史天气信息"""
        current = data['current']
        
        info = f"{city} {date} 历史天气:\n"
        info += f"温度: {current['temp']}°C\n"
        info += f"体感温度: {current['feels_like']}°C\n"
        info += f"湿度: {current['humidity']}%\n"
        info += f"气压: {current['pressure']} hPa\n"
        info += f"天气: {current['weather'][0]['description']}\n"
        
        if 'wind_speed' in current:
            info += f"风速: {current['wind_speed']} m/s\n"
            
        return info