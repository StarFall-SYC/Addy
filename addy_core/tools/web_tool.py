"""网络工具

提供HTTP请求、API调用、文件下载、网页内容获取等功能。
"""

import requests
import json
import urllib.parse
from typing import Dict, Any, List
from .base_tool import BaseTool

class WebTool(BaseTool):
    """网络工具类"""
    
    def __init__(self, config=None, logger=None, speak_func=None):
        super().__init__(config, logger)
        self.speak = speak_func or (lambda x: print(f"[WebTool] {x}"))
        self.session = requests.Session()
        # 设置默认请求头
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def get_name(self) -> str:
        return "网络工具"
        
    def get_description(self) -> str:
        return "提供HTTP请求、API调用、文件下载、网页内容获取等功能"
        
    def get_supported_intents(self) -> List[str]:
        return [
            'http_get',
            'http_post',
            'download_file',
            'get_webpage_content',
            'check_website_status',
            'api_call',
            'upload_file',
            'get_ip_info',
            'ping_host',
            'check_port',
            'get_weather_api',
            'translate_text',
            'shorten_url'
        ]
        
    def execute(self, intent: str, entities: Dict[str, Any], original_text: str) -> str:
        """执行网络操作"""
        try:
            if intent == 'http_get':
                return self._http_get(entities)
            elif intent == 'http_post':
                return self._http_post(entities)
            elif intent == 'download_file':
                return self._download_file(entities)
            elif intent == 'get_webpage_content':
                return self._get_webpage_content(entities)
            elif intent == 'check_website_status':
                return self._check_website_status(entities)
            elif intent == 'api_call':
                return self._api_call(entities)
            elif intent == 'upload_file':
                return self._upload_file(entities)
            elif intent == 'get_ip_info':
                return self._get_ip_info(entities)
            elif intent == 'ping_host':
                return self._ping_host(entities)
            elif intent == 'check_port':
                return self._check_port(entities)
            elif intent == 'get_weather_api':
                return self._get_weather_api(entities)
            elif intent == 'translate_text':
                return self._translate_text(entities)
            elif intent == 'shorten_url':
                return self._shorten_url(entities)
            else:
                return f"不支持的网络操作: {intent}"
                
        except Exception as e:
            error_msg = f"网络操作失败: {str(e)}"
            self.speak(error_msg)
            self.logger.error(error_msg)
            return f"error: {str(e)}"
            
    def _http_get(self, entities: Dict[str, Any]) -> str:
        """发送HTTP GET请求"""
        validation_error = self.validate_entities(['url'], entities)
        if validation_error:
            self.speak(validation_error)
            return f"error: {validation_error}"
            
        url = entities['url']
        headers = entities.get('headers', {})
        params = entities.get('params', {})
        timeout = entities.get('timeout', 30)
        
        try:
            response = self.session.get(url, headers=headers, params=params, timeout=timeout)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '')
            if 'application/json' in content_type:
                try:
                    data = response.json()
                    self.speak(f"GET请求成功，返回JSON数据: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}...")
                except json.JSONDecodeError:
                    self.speak(f"GET请求成功，状态码: {response.status_code}，内容长度: {len(response.text)}")
            else:
                self.speak(f"GET请求成功，状态码: {response.status_code}，内容长度: {len(response.text)}")
                
            return f"http_get_success: {response.status_code}"
            
        except requests.exceptions.RequestException as e:
            error_msg = f"GET请求失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _http_post(self, entities: Dict[str, Any]) -> str:
        """发送HTTP POST请求"""
        validation_error = self.validate_entities(['url'], entities)
        if validation_error:
            self.speak(validation_error)
            return f"error: {validation_error}"
            
        url = entities['url']
        data = entities.get('data', {})
        json_data = entities.get('json_data')
        headers = entities.get('headers', {})
        timeout = entities.get('timeout', 30)
        
        try:
            if json_data:
                response = self.session.post(url, json=json_data, headers=headers, timeout=timeout)
            else:
                response = self.session.post(url, data=data, headers=headers, timeout=timeout)
                
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '')
            if 'application/json' in content_type:
                try:
                    data = response.json()
                    self.speak(f"POST请求成功，返回JSON数据: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}...")
                except json.JSONDecodeError:
                    self.speak(f"POST请求成功，状态码: {response.status_code}，内容长度: {len(response.text)}")
            else:
                self.speak(f"POST请求成功，状态码: {response.status_code}，内容长度: {len(response.text)}")
                
            return f"http_post_success: {response.status_code}"
            
        except requests.exceptions.RequestException as e:
            error_msg = f"POST请求失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _download_file(self, entities: Dict[str, Any]) -> str:
        """下载文件"""
        validation_error = self.validate_entities(['url', 'save_path'], entities)
        if validation_error:
            self.speak(validation_error)
            return f"error: {validation_error}"
            
        url = entities['url']
        save_path = entities['save_path']
        timeout = entities.get('timeout', 60)
        
        try:
            response = self.session.get(url, timeout=timeout, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
            if total_size > 0:
                self.speak(f"文件下载完成: {save_path} ({downloaded_size}/{total_size} 字节)")
            else:
                self.speak(f"文件下载完成: {save_path} ({downloaded_size} 字节)")
                
            return f"file_downloaded: {save_path}"
            
        except requests.exceptions.RequestException as e:
            error_msg = f"文件下载失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
        except IOError as e:
            error_msg = f"文件保存失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _get_webpage_content(self, entities: Dict[str, Any]) -> str:
        """获取网页内容"""
        validation_error = self.validate_entities(['url'], entities)
        if validation_error:
            self.speak(validation_error)
            return f"error: {validation_error}"
            
        url = entities['url']
        max_length = entities.get('max_length', 1000)
        extract_text = entities.get('extract_text', True)
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            content = response.text
            
            if extract_text:
                # 简单的HTML标签移除（可以使用BeautifulSoup进行更好的处理）
                import re
                content = re.sub(r'<[^>]+>', '', content)
                content = re.sub(r'\s+', ' ', content).strip()
                
            if len(content) > max_length:
                content = content[:max_length] + "..."
                
            self.speak(f"网页内容获取成功:\n{content}")
            return f"webpage_content_retrieved: {url}"
            
        except requests.exceptions.RequestException as e:
            error_msg = f"获取网页内容失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _check_website_status(self, entities: Dict[str, Any]) -> str:
        """检查网站状态"""
        validation_error = self.validate_entities(['url'], entities)
        if validation_error:
            self.speak(validation_error)
            return f"error: {validation_error}"
            
        url = entities['url']
        timeout = entities.get('timeout', 10)
        
        try:
            response = self.session.head(url, timeout=timeout)
            status_code = response.status_code
            
            if status_code == 200:
                self.speak(f"网站 {url} 正常运行 (状态码: {status_code})")
                return f"website_status_ok: {status_code}"
            else:
                self.speak(f"网站 {url} 状态异常 (状态码: {status_code})")
                return f"website_status_error: {status_code}"
                
        except requests.exceptions.RequestException as e:
            error_msg = f"检查网站状态失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _api_call(self, entities: Dict[str, Any]) -> str:
        """通用API调用"""
        validation_error = self.validate_entities(['url', 'method'], entities)
        if validation_error:
            self.speak(validation_error)
            return f"error: {validation_error}"
            
        url = entities['url']
        method = entities['method'].upper()
        headers = entities.get('headers', {})
        data = entities.get('data', {})
        params = entities.get('params', {})
        timeout = entities.get('timeout', 30)
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=headers, params=params, timeout=timeout)
            elif method == 'POST':
                response = self.session.post(url, headers=headers, data=data, params=params, timeout=timeout)
            elif method == 'PUT':
                response = self.session.put(url, headers=headers, data=data, params=params, timeout=timeout)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=headers, params=params, timeout=timeout)
            else:
                self.speak(f"不支持的HTTP方法: {method}")
                return f"error: unsupported_method: {method}"
                
            response.raise_for_status()
            
            try:
                result = response.json()
                self.speak(f"API调用成功，返回数据: {json.dumps(result, ensure_ascii=False, indent=2)[:500]}...")
            except json.JSONDecodeError:
                self.speak(f"API调用成功，状态码: {response.status_code}")
                
            return f"api_call_success: {response.status_code}"
            
        except requests.exceptions.RequestException as e:
            error_msg = f"API调用失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _get_ip_info(self, entities: Dict[str, Any]) -> str:
        """获取IP信息"""
        ip_address = entities.get('ip_address')
        
        try:
            if ip_address:
                url = f"http://ip-api.com/json/{ip_address}"
            else:
                url = "http://ip-api.com/json/"
                
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 'success':
                info = f"IP信息:\n"
                info += f"IP地址: {data.get('query')}\n"
                info += f"国家: {data.get('country')}\n"
                info += f"地区: {data.get('regionName')}\n"
                info += f"城市: {data.get('city')}\n"
                info += f"ISP: {data.get('isp')}\n"
                info += f"时区: {data.get('timezone')}\n"
                
                self.speak(info)
                return f"ip_info_retrieved: {data.get('query')}"
            else:
                self.speak(f"获取IP信息失败: {data.get('message')}")
                return f"error: {data.get('message')}"
                
        except Exception as e:
            error_msg = f"获取IP信息失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _ping_host(self, entities: Dict[str, Any]) -> str:
        """Ping主机"""
        validation_error = self.validate_entities(['host'], entities)
        if validation_error:
            self.speak(validation_error)
            return f"error: {validation_error}"
            
        host = entities['host']
        count = entities.get('count', 4)
        
        try:
            import subprocess
            import platform
            
            # 根据操作系统选择ping命令
            if platform.system().lower() == 'windows':
                cmd = ['ping', '-n', str(count), host]
            else:
                cmd = ['ping', '-c', str(count), host]
                
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # 解析ping结果
                output_lines = result.stdout.split('\n')
                summary_line = [line for line in output_lines if 'packets' in line.lower() or '丢失' in line]
                
                if summary_line:
                    self.speak(f"Ping {host} 成功:\n{summary_line[0]}")
                else:
                    self.speak(f"Ping {host} 成功")
                    
                return f"ping_success: {host}"
            else:
                self.speak(f"Ping {host} 失败: {result.stderr}")
                return f"ping_failed: {host}"
                
        except Exception as e:
            error_msg = f"Ping操作失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _check_port(self, entities: Dict[str, Any]) -> str:
        """检查端口状态"""
        validation_error = self.validate_entities(['host', 'port'], entities)
        if validation_error:
            self.speak(validation_error)
            return f"error: {validation_error}"
            
        host = entities['host']
        port = int(entities['port'])
        timeout = entities.get('timeout', 5)
        
        try:
            import socket
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                self.speak(f"端口 {host}:{port} 开放")
                return f"port_open: {host}:{port}"
            else:
                self.speak(f"端口 {host}:{port} 关闭或不可达")
                return f"port_closed: {host}:{port}"
                
        except Exception as e:
            error_msg = f"检查端口失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _get_weather_api(self, entities: Dict[str, Any]) -> str:
        """通过API获取天气信息"""
        validation_error = self.validate_entities(['city'], entities)
        if validation_error:
            self.speak(validation_error)
            return f"error: {validation_error}"
            
        city = entities['city']
        api_key = entities.get('api_key') or (self.config.get('Weather', 'api_key', fallback=None) if self.config else None)
        
        if not api_key:
            self.speak("需要配置天气API密钥")
            return "error: missing_api_key"
            
        try:
            # 使用OpenWeatherMap API
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': city,
                'appid': api_key,
                'units': 'metric',
                'lang': 'zh_cn'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('cod') == 200:
                weather_info = f"{city}天气信息:\n"
                weather_info += f"温度: {data['main']['temp']}°C\n"
                weather_info += f"体感温度: {data['main']['feels_like']}°C\n"
                weather_info += f"湿度: {data['main']['humidity']}%\n"
                weather_info += f"天气: {data['weather'][0]['description']}\n"
                weather_info += f"风速: {data['wind']['speed']} m/s\n"
                
                self.speak(weather_info)
                return f"weather_retrieved: {city}"
            else:
                self.speak(f"获取天气信息失败: {data.get('message')}")
                return f"error: {data.get('message')}"
                
        except Exception as e:
            error_msg = f"获取天气信息失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _translate_text(self, entities: Dict[str, Any]) -> str:
        """翻译文本（使用免费API）"""
        validation_error = self.validate_entities(['text'], entities)
        if validation_error:
            self.speak(validation_error)
            return f"error: {validation_error}"
            
        text = entities['text']
        target_lang = entities.get('target_lang', 'en')
        source_lang = entities.get('source_lang', 'auto')
        
        try:
            # 使用Google Translate的免费API（非官方）
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                'client': 'gtx',
                'sl': source_lang,
                'tl': target_lang,
                'dt': 't',
                'q': text
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            translated_text = result[0][0][0]
            
            self.speak(f"翻译结果:\n原文: {text}\n译文: {translated_text}")
            return f"text_translated: {source_lang} -> {target_lang}"
            
        except Exception as e:
            error_msg = f"翻译失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _shorten_url(self, entities: Dict[str, Any]) -> str:
        """缩短URL"""
        validation_error = self.validate_entities(['url'], entities)
        if validation_error:
            self.speak(validation_error)
            return f"error: {validation_error}"
            
        url = entities['url']
        
        try:
            # 使用TinyURL服务
            api_url = "http://tinyurl.com/api-create.php"
            params = {'url': url}
            
            response = self.session.get(api_url, params=params, timeout=10)
            response.raise_for_status()
            
            short_url = response.text.strip()
            
            if short_url.startswith('http'):
                self.speak(f"URL缩短成功:\n原URL: {url}\n短URL: {short_url}")
                return f"url_shortened: {short_url}"
            else:
                self.speak(f"URL缩短失败: {short_url}")
                return f"error: {short_url}"
                
        except Exception as e:
            error_msg = f"URL缩短失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _upload_file(self, entities: Dict[str, Any]) -> str:
        """上传文件"""
        validation_error = self.validate_entities(['url', 'file_path'], entities)
        if validation_error:
            self.speak(validation_error)
            return f"error: {validation_error}"
            
        url = entities['url']
        file_path = entities['file_path']
        field_name = entities.get('field_name', 'file')
        headers = entities.get('headers', {})
        
        try:
            with open(file_path, 'rb') as f:
                files = {field_name: f}
                response = self.session.post(url, files=files, headers=headers, timeout=60)
                
            response.raise_for_status()
            
            self.speak(f"文件上传成功: {file_path}")
            return f"file_uploaded: {file_path}"
            
        except FileNotFoundError:
            error_msg = f"文件不存在: {file_path}"
            self.speak(error_msg)
            return f"error: file_not_found"
        except requests.exceptions.RequestException as e:
            error_msg = f"文件上传失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"