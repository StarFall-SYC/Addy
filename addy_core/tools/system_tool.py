"""系统工具

提供系统信息查询、进程管理、服务控制等功能。
"""

import os
import psutil
import subprocess
import platform
from typing import Dict, Any, List
from .base_tool import BaseTool

class SystemTool(BaseTool):
    """系统工具类"""
    
    def __init__(self, config=None, logger=None, speak_func=None):
        super().__init__(config, logger)
        self.speak = speak_func or (lambda x: print(f"[SystemTool] {x}"))
        
    def get_name(self) -> str:
        return "系统工具"
        
    def get_description(self) -> str:
        return "提供系统信息查询、进程管理、服务控制等功能"
        
    def get_supported_intents(self) -> List[str]:
        return [
            'get_system_info',
            'get_cpu_usage',
            'get_memory_usage',
            'get_disk_usage',
            'list_processes',
            'kill_process',
            'start_service',
            'stop_service',
            'restart_service',
            'get_network_info',
            'shutdown_system',
            'restart_system',
            'lock_screen',
            'get_battery_info',
            'set_volume',
            'get_volume',
            'take_screenshot'
        ]
        
    def execute(self, intent: str, entities: Dict[str, Any], original_text: str) -> str:
        """执行系统操作"""
        try:
            if intent == 'get_system_info':
                return self._get_system_info(entities)
            elif intent == 'get_cpu_usage':
                return self._get_cpu_usage(entities)
            elif intent == 'get_memory_usage':
                return self._get_memory_usage(entities)
            elif intent == 'get_disk_usage':
                return self._get_disk_usage(entities)
            elif intent == 'list_processes':
                return self._list_processes(entities)
            elif intent == 'kill_process':
                return self._kill_process(entities)
            elif intent == 'start_service':
                return self._start_service(entities)
            elif intent == 'stop_service':
                return self._stop_service(entities)
            elif intent == 'restart_service':
                return self._restart_service(entities)
            elif intent == 'get_network_info':
                return self._get_network_info(entities)
            elif intent == 'shutdown_system':
                return self._shutdown_system(entities)
            elif intent == 'restart_system':
                return self._restart_system(entities)
            elif intent == 'lock_screen':
                return self._lock_screen(entities)
            elif intent == 'get_battery_info':
                return self._get_battery_info(entities)
            elif intent == 'set_volume':
                return self._set_volume(entities)
            elif intent == 'get_volume':
                return self._get_volume(entities)
            elif intent == 'take_screenshot':
                return self._take_screenshot(entities)
            else:
                return f"不支持的系统操作: {intent}"
                
        except Exception as e:
            error_msg = f"系统操作失败: {str(e)}"
            self.speak(error_msg)
            self.logger.error(error_msg)
            return f"error: {str(e)}"
            
    def _get_system_info(self, entities: Dict[str, Any]) -> str:
        """获取系统信息"""
        try:
            info = f"系统信息:\n"
            info += f"操作系统: {platform.system()} {platform.release()}\n"
            info += f"处理器: {platform.processor()}\n"
            info += f"架构: {platform.architecture()[0]}\n"
            info += f"计算机名: {platform.node()}\n"
            info += f"Python版本: {platform.python_version()}\n"
            
            # CPU信息
            info += f"CPU核心数: {psutil.cpu_count(logical=False)} 物理核心, {psutil.cpu_count(logical=True)} 逻辑核心\n"
            
            # 内存信息
            memory = psutil.virtual_memory()
            info += f"总内存: {memory.total // (1024**3)} GB\n"
            
            self.speak(info)
            return "system_info_retrieved"
            
        except Exception as e:
            error_msg = f"获取系统信息失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _get_cpu_usage(self, entities: Dict[str, Any]) -> str:
        """获取CPU使用率"""
        try:
            # 获取CPU使用率（1秒间隔）
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_per_core = psutil.cpu_percent(interval=1, percpu=True)
            
            info = f"CPU使用率: {cpu_percent}%\n"
            info += f"各核心使用率: {', '.join([f'{i+1}核:{p}%' for i, p in enumerate(cpu_per_core)])}\n"
            
            # CPU频率
            cpu_freq = psutil.cpu_freq()
            if cpu_freq:
                info += f"CPU频率: {cpu_freq.current:.2f} MHz\n"
                
            self.speak(info)
            return f"cpu_usage_retrieved: {cpu_percent}%"
            
        except Exception as e:
            error_msg = f"获取CPU使用率失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _get_memory_usage(self, entities: Dict[str, Any]) -> str:
        """获取内存使用情况"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            info = f"内存使用情况:\n"
            info += f"总内存: {memory.total // (1024**3)} GB\n"
            info += f"已使用: {memory.used // (1024**3)} GB ({memory.percent}%)\n"
            info += f"可用: {memory.available // (1024**3)} GB\n"
            info += f"交换分区: {swap.total // (1024**3)} GB (已使用 {swap.percent}%)\n"
            
            self.speak(info)
            return f"memory_usage_retrieved: {memory.percent}%"
            
        except Exception as e:
            error_msg = f"获取内存使用情况失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _get_disk_usage(self, entities: Dict[str, Any]) -> str:
        """获取磁盘使用情况"""
        try:
            path = entities.get('path', '/')
            if platform.system() == 'Windows':
                path = entities.get('path', 'C:\\')
                
            disk_usage = psutil.disk_usage(path)
            
            info = f"磁盘使用情况 ({path}):\n"
            info += f"总容量: {disk_usage.total // (1024**3)} GB\n"
            info += f"已使用: {disk_usage.used // (1024**3)} GB\n"
            info += f"可用: {disk_usage.free // (1024**3)} GB\n"
            info += f"使用率: {(disk_usage.used / disk_usage.total * 100):.1f}%\n"
            
            # 列出所有磁盘分区
            partitions = psutil.disk_partitions()
            if len(partitions) > 1:
                info += "\n所有分区:\n"
                for partition in partitions:
                    try:
                        partition_usage = psutil.disk_usage(partition.mountpoint)
                        info += f"{partition.device}: {partition_usage.used // (1024**3)} GB / {partition_usage.total // (1024**3)} GB\n"
                    except PermissionError:
                        info += f"{partition.device}: 无法访问\n"
                        
            self.speak(info)
            return f"disk_usage_retrieved: {path}"
            
        except Exception as e:
            error_msg = f"获取磁盘使用情况失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _list_processes(self, entities: Dict[str, Any]) -> str:
        """列出进程"""
        try:
            limit = entities.get('limit', 10)
            sort_by = entities.get('sort_by', 'cpu')  # cpu, memory, name
            
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
                    
            # 排序
            if sort_by == 'cpu':
                processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
            elif sort_by == 'memory':
                processes.sort(key=lambda x: x['memory_percent'] or 0, reverse=True)
            else:
                processes.sort(key=lambda x: x['name'] or '')
                
            info = f"进程列表 (按{sort_by}排序，前{limit}个):\n"
            for i, proc in enumerate(processes[:limit]):
                info += f"{i+1}. {proc['name']} (PID: {proc['pid']}) - CPU: {proc['cpu_percent']:.1f}%, 内存: {proc['memory_percent']:.1f}%\n"
                
            self.speak(info)
            return f"processes_listed: {len(processes[:limit])}"
            
        except Exception as e:
            error_msg = f"列出进程失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _kill_process(self, entities: Dict[str, Any]) -> str:
        """终止进程"""
        process_name = entities.get('process_name')
        process_id = entities.get('process_id')
        
        if not process_name and not process_id:
            self.speak("请指定要终止的进程名称或进程ID")
            return "error: missing_process_identifier"
            
        try:
            killed_count = 0
            
            if process_id:
                # 通过PID终止进程
                try:
                    proc = psutil.Process(int(process_id))
                    proc.terminate()
                    killed_count = 1
                    self.speak(f"进程 {process_id} 已终止")
                except psutil.NoSuchProcess:
                    self.speak(f"进程 {process_id} 不存在")
                    return f"error: process_not_found: {process_id}"
            else:
                # 通过名称终止进程
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        if process_name.lower() in proc.info['name'].lower():
                            proc.terminate()
                            killed_count += 1
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                        
                if killed_count > 0:
                    self.speak(f"已终止 {killed_count} 个名为 '{process_name}' 的进程")
                else:
                    self.speak(f"未找到名为 '{process_name}' 的进程")
                    return f"error: process_not_found: {process_name}"
                    
            return f"process_killed: {killed_count}"
            
        except Exception as e:
            error_msg = f"终止进程失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _get_network_info(self, entities: Dict[str, Any]) -> str:
        """获取网络信息"""
        try:
            # 网络接口信息
            net_io = psutil.net_io_counters()
            net_if_addrs = psutil.net_if_addrs()
            
            info = f"网络信息:\n"
            info += f"总发送: {net_io.bytes_sent // (1024**2)} MB\n"
            info += f"总接收: {net_io.bytes_recv // (1024**2)} MB\n"
            
            info += "\n网络接口:\n"
            for interface_name, interface_addresses in net_if_addrs.items():
                for address in interface_addresses:
                    if str(address.family) == 'AddressFamily.AF_INET':
                        info += f"{interface_name}: {address.address}\n"
                        break
                        
            self.speak(info)
            return "network_info_retrieved"
            
        except Exception as e:
            error_msg = f"获取网络信息失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _get_battery_info(self, entities: Dict[str, Any]) -> str:
        """获取电池信息"""
        try:
            battery = psutil.sensors_battery()
            if battery is None:
                self.speak("此设备没有电池或无法获取电池信息")
                return "no_battery_found"
                
            info = f"电池信息:\n"
            info += f"电量: {battery.percent}%\n"
            info += f"电源连接: {'是' if battery.power_plugged else '否'}\n"
            
            if battery.secsleft != psutil.POWER_TIME_UNLIMITED:
                hours, remainder = divmod(battery.secsleft, 3600)
                minutes, _ = divmod(remainder, 60)
                info += f"剩余时间: {hours}小时{minutes}分钟\n"
            else:
                info += "剩余时间: 无限制（已连接电源）\n"
                
            self.speak(info)
            return f"battery_info_retrieved: {battery.percent}%"
            
        except Exception as e:
            error_msg = f"获取电池信息失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _lock_screen(self, entities: Dict[str, Any]) -> str:
        """锁定屏幕"""
        try:
            if platform.system() == 'Windows':
                os.system('rundll32.exe user32.dll,LockWorkStation')
            elif platform.system() == 'Darwin':  # macOS
                os.system('/System/Library/CoreServices/Menu\\ Extras/User.menu/Contents/Resources/CGSession -suspend')
            else:  # Linux
                os.system('gnome-screensaver-command -l')
                
            self.speak("屏幕已锁定")
            return "screen_locked"
            
        except Exception as e:
            error_msg = f"锁定屏幕失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _shutdown_system(self, entities: Dict[str, Any]) -> str:
        """关闭系统"""
        delay = entities.get('delay', 0)  # 延迟秒数
        
        try:
            self.speak(f"系统将在 {delay} 秒后关闭")
            
            if platform.system() == 'Windows':
                os.system(f'shutdown /s /t {delay}')
            else:
                os.system(f'shutdown -h +{delay//60}')
                
            return f"shutdown_scheduled: {delay}s"
            
        except Exception as e:
            error_msg = f"关闭系统失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _restart_system(self, entities: Dict[str, Any]) -> str:
        """重启系统"""
        delay = entities.get('delay', 0)  # 延迟秒数
        
        try:
            self.speak(f"系统将在 {delay} 秒后重启")
            
            if platform.system() == 'Windows':
                os.system(f'shutdown /r /t {delay}')
            else:
                os.system(f'shutdown -r +{delay//60}')
                
            return f"restart_scheduled: {delay}s"
            
        except Exception as e:
            error_msg = f"重启系统失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _set_volume(self, entities: Dict[str, Any]) -> str:
        """设置音量"""
        validation_error = self.validate_entities(['volume'], entities)
        if validation_error:
            self.speak(validation_error)
            return f"error: {validation_error}"
            
        volume = entities['volume']
        
        try:
            volume_level = int(volume)
            if volume_level < 0 or volume_level > 100:
                self.speak("音量必须在0到100之间")
                return "error: invalid_volume_range"
                
            if platform.system() == 'Windows':
                # Windows音量控制
                from ctypes import cast, POINTER
                from comtypes import CLSCTX_ALL
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume_control = cast(interface, POINTER(IAudioEndpointVolume))
                volume_control.SetMasterVolumeLevelScalar(volume_level / 100.0, None)
                
            self.speak(f"音量已设置为 {volume_level}%")
            return f"volume_set: {volume_level}%"
            
        except Exception as e:
            error_msg = f"设置音量失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _get_volume(self, entities: Dict[str, Any]) -> str:
        """获取当前音量"""
        try:
            if platform.system() == 'Windows':
                # Windows音量获取
                from ctypes import cast, POINTER
                from comtypes import CLSCTX_ALL
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume_control = cast(interface, POINTER(IAudioEndpointVolume))
                current_volume = int(volume_control.GetMasterVolumeLevelScalar() * 100)
                
                self.speak(f"当前音量: {current_volume}%")
                return f"current_volume: {current_volume}%"
            else:
                self.speak("此平台暂不支持音量查询")
                return "error: platform_not_supported"
                
        except Exception as e:
            error_msg = f"获取音量失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"

    def _take_screenshot(self, entities: Dict[str, Any]) -> str:
        """截屏"""
        try:
            # 尝试使用 desktop_controller 的截屏功能
            if hasattr(self, 'desktop_controller') and self.desktop_controller:
                screenshot_path = self.desktop_controller.capture_screen(filename_prefix="screenshot_")
                if screenshot_path:
                    self.speak(f"截图已保存到: {screenshot_path}")
                    return f"screenshot_taken: {screenshot_path}"
                else:
                    self.speak("截屏失败")
                    return "error: screenshot_failed"
            else:
                # 后备方案：直接调用系统命令 (示例，可能需要根据操作系统调整)
                # 注意：这种方式可能不够健壮，且保存路径固定
                import pyautogui # 确保已安装：pip install pyautogui Pillow
                import time
                from pathlib import Path

                screenshots_dir = Path(self.config.get('paths', 'screenshots_dir', fallback='screenshots'))
                screenshots_dir.mkdir(parents=True, exist_ok=True)
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = screenshots_dir / f"screenshot_{timestamp}.png"
                
                pyautogui.screenshot(str(filename))
                self.speak(f"截图已保存到: {filename}")
                return f"screenshot_taken: {filename}"

        except ImportError:
            self.speak("截屏功能需要 pyautogui 库，请先安装它 (pip install pyautogui Pillow)")
            self.logger.error("pyautogui not found for screenshot")
            return "error: pyautogui_not_found"
        except Exception as e:
            error_msg = f"截屏失败: {str(e)}"
            self.speak(error_msg)
            self.logger.error(f"Screenshot failed: {str(e)}", exc_info=True)
            return f"error: {str(e)}"
            
    def _start_service(self, entities: Dict[str, Any]) -> str:
        """启动服务（需要管理员权限）"""
        validation_error = self.validate_entities(['service_name'], entities)
        if validation_error:
            self.speak(validation_error)
            return f"error: {validation_error}"
            
        service_name = entities['service_name']
        
        try:
            if platform.system() == 'Windows':
                result = subprocess.run(['sc', 'start', service_name], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    self.speak(f"服务 {service_name} 已启动")
                    return f"service_started: {service_name}"
                else:
                    self.speak(f"启动服务失败: {result.stderr}")
                    return f"error: {result.stderr}"
            else:
                result = subprocess.run(['systemctl', 'start', service_name], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    self.speak(f"服务 {service_name} 已启动")
                    return f"service_started: {service_name}"
                else:
                    self.speak(f"启动服务失败: {result.stderr}")
                    return f"error: {result.stderr}"
                    
        except Exception as e:
            error_msg = f"启动服务失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _stop_service(self, entities: Dict[str, Any]) -> str:
        """停止服务（需要管理员权限）"""
        validation_error = self.validate_entities(['service_name'], entities)
        if validation_error:
            self.speak(validation_error)
            return f"error: {validation_error}"
            
        service_name = entities['service_name']
        
        try:
            if platform.system() == 'Windows':
                result = subprocess.run(['sc', 'stop', service_name], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    self.speak(f"服务 {service_name} 已停止")
                    return f"service_stopped: {service_name}"
                else:
                    self.speak(f"停止服务失败: {result.stderr}")
                    return f"error: {result.stderr}"
            else:
                result = subprocess.run(['systemctl', 'stop', service_name], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    self.speak(f"服务 {service_name} 已停止")
                    return f"service_stopped: {service_name}"
                else:
                    self.speak(f"停止服务失败: {result.stderr}")
                    return f"error: {result.stderr}"
                    
        except Exception as e:
            error_msg = f"停止服务失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _restart_service(self, entities: Dict[str, Any]) -> str:
        """重启服务（需要管理员权限）"""
        validation_error = self.validate_entities(['service_name'], entities)
        if validation_error:
            self.speak(validation_error)
            return f"error: {validation_error}"
            
        service_name = entities['service_name']
        
        try:
            if platform.system() == 'Windows':
                # Windows没有直接的restart命令，需要先停止再启动
                subprocess.run(['sc', 'stop', service_name], capture_output=True)
                result = subprocess.run(['sc', 'start', service_name], 
                                      capture_output=True, text=True)
            else:
                result = subprocess.run(['systemctl', 'restart', service_name], 
                                      capture_output=True, text=True)
                                      
            if result.returncode == 0:
                self.speak(f"服务 {service_name} 已重启")
                return f"service_restarted: {service_name}"
            else:
                self.speak(f"重启服务失败: {result.stderr}")
                return f"error: {result.stderr}"
                
        except Exception as e:
            error_msg = f"重启服务失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"