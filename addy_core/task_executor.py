# addy_core/task_executor.py

import subprocess
import webbrowser
import datetime
import os
import logging

# Addy custom modules
from .desktop_controller import DesktopController # Assuming it's in the same package
from .tools.tool_manager import ToolManager

class TaskExecutor:
    def __init__(self, config=None, tts_engine_speak_func=None, tool_manager=None): # Added tool_manager
        """
        Initializes the TaskExecutor.
        config: The application configuration object.
        tts_engine_speak_func: A function (e.g., from main.py's speak) to provide voice feedback.
        """
        self.config = config
        self.speak = tts_engine_speak_func if tts_engine_speak_func else self._default_speak
        self.logger = logging.getLogger(__name__)
        self.desktop_controller = DesktopController(config=self.config)
        
        # Use provided tool_manager or initialize a new one if not provided (though it should be)
        self.tool_manager = tool_manager if tool_manager else ToolManager(config=config, speak_func=tts_engine_speak_func if tts_engine_speak_func else self._default_speak)
        
        self.logger.info("TaskExecutor initialized.")
    
    def _default_speak(self, text):
        """Default speak function if TTS is not available"""
        print(f"[Addy]: {text}")

    def execute(self, intent_data):
        """
        Executes a task based on the intent data from the NLP module.

        Args:
            intent_data (dict): The output from NLPModule.parse_intent().
                                Example: {'intent': 'open_application', 
                                          'entities': {'application_name': 'notepad.exe'}}
        
        Returns:
            str: A status or result message, or None. Special return "exit" for quitting.
        """
        if not intent_data or 'intent' not in intent_data:
            self.speak("抱歉，我无法理解这个指令。")
            return "error: no intent"

        intent = intent_data.get('intent')
        entities = intent_data.get('entities', {})
        original_text = intent_data.get('original_text', '')
        tool_call_info = intent_data.get('tool_call') # Get tool_call from intent_data

        print(f"TaskExecutor: Executing intent '{intent}' with entities: {entities}, tool_call: {tool_call_info}")

        try:
            # Prioritize tool_call if present and tool_manager is available
            if tool_call_info and self.tool_manager:
                tool_name = tool_call_info.get('name')
                tool_args = tool_call_info.get('arguments') # Arguments from LLM

                if tool_name:
                    # The ToolManager's execute_tool expects an intent-like structure.
                    # We map the LLM tool_name to 'intent' and LLM arguments to 'entities'.
                    # This assumes the ToolManager can handle this mapping or is adapted for it.
                    tool_intent_data = {
                        'intent': tool_name, 
                        'entities': tool_args if isinstance(tool_args, dict) else {},
                        'original_text': original_text
                    }
                    try:
                        # Assuming execute_tool is the correct method for LLM-driven tool calls
                        # If not, and it should be execute_intent, ensure it gets all necessary params
                        current_tool_args = tool_args if isinstance(tool_args, dict) else {}
                        current_original_text_for_tool = str(original_text) if original_text is not None else ''
                        self.logger.debug(f"TaskExecutor calling tool_manager.execute_intent (for LLM tool) with intent: {tool_name} (type: {type(tool_name)}), entities: {current_tool_args} (type: {type(current_tool_args)}), original_text: {current_original_text_for_tool} (type: {type(current_original_text_for_tool)})")
                        result = self.tool_manager.execute_intent(intent=str(tool_name), entities=current_tool_args, original_text=current_original_text_for_tool)
                        if result and not result.startswith('error:'):
                            # self.speak(str(result)) # Tools might provide their own feedback via speak_func
                            pass # Let the tool handle its own speech output if necessary
                        elif result and result.startswith('error:'):
                            self.speak(f"执行工具 {tool_name} 时遇到问题: {result.split(':', 1)[1].strip()}")
                        return f"tool_executed: {tool_name}"
                    except Exception as e:
                        error_msg = f"执行工具 {tool_name} 时发生意外错误: {e}"
                        self.speak(error_msg)
                        self.logger.error(f"TaskExecutor Error: {error_msg} with args {tool_args}", exc_info=True)
                        return f"error: tool_execution_failed: {tool_name}"
                else:
                    self.speak("LLM建议使用工具，但工具名称不完整。")
                    return "error: incomplete_tool_info"
            
            # Fallback to direct intent handling or rule-based tool execution if no LLM tool_call
            # Check if the intent is something the ToolManager should handle
            elif self.tool_manager and self.tool_manager.get_tool_for_intent(intent):
                try:
                    # Ensure entities and original_text are not None and have correct types
                    intent_to_pass = str(intent) if intent is not None else ""
                    current_entities = entities if isinstance(entities, dict) else {}
                    current_original_text = str(original_text) if original_text is not None else ''
                    self.logger.debug(f"TaskExecutor calling tool_manager.execute_intent with intent: {intent_to_pass} (type: {type(intent_to_pass)}), entities: {current_entities} (type: {type(current_entities)}), original_text: {current_original_text} (type: {type(current_original_text)})")
                    result = self.tool_manager.execute_intent(intent_to_pass, current_entities, current_original_text)
                    # Tools are expected to call self.speak() themselves if they need to provide feedback.
                    # TaskExecutor might only speak if there's a generic success/failure or clarification needed.
                    if result and result.startswith('error:'):
                        self.speak(f"处理指令 '{current_original_text}' 时遇到问题。") # Generic error message
                        self.logger.error(f"TaskExecutor: Tool execution for intent '{intent}' failed: {result}")
                    # elif result: # Potentially speak a generic success message if tool doesn't
                        # self.speak("操作已完成。")
                    return result # Return the raw result from the tool
                except Exception as e:
                    current_original_text_for_error = original_text if original_text is not None else ''
                    error_msg = f"执行指令 '{current_original_text_for_error}' (意图: {intent}) 时发生意外错误: {e}"
                    self.speak("抱歉，执行该指令时出现了一些问题。")
                    self.logger.error(error_msg, exc_info=True)
                    return f"error: rule_based_tool_execution_failed: {intent}"
            
            # Legacy/Direct intent handling (if not covered by ToolManager)
            elif intent == 'open_application':
                app_name = entities.get('application_name')
                if app_name == 'browser': # Generic browser intent
                    specific_browser = entities.get('specific_browser')
                    if specific_browser == 'chrome':
                        self.speak("正在打开谷歌浏览器。")
                        # Note: This requires Chrome to be in PATH or provide full path
                        try: subprocess.Popen(['chrome.exe'])
                        except FileNotFoundError: subprocess.Popen(['start', 'chrome'], shell=True) # Fallback for Windows
                    elif specific_browser == 'edge':
                        self.speak("正在打开 Edge 浏览器。")
                        try: subprocess.Popen(['msedge.exe'])
                        except FileNotFoundError: subprocess.Popen(['start', 'msedge'], shell=True)
                    else:
                        self.speak("正在打开默认浏览器。")
                        webbrowser.open("http://google.com") # Opens default browser
                elif app_name:
                    app_name_display = app_name.replace('.exe', '') if app_name.lower().endswith('.exe') else app_name
                    self.speak(f"正在打开 {app_name_display}")
                    # Security consideration: Sanitize app_name or use a whitelist.
                    # The current approach relies on app_name being a direct executable name or
                    # something the 'start' command can handle.
                    try:
                        # First attempt: direct execution (works if in PATH or full path)
                        # Popen with a list of args doesn't use the shell by default, which is safer.
                        subprocess.Popen([app_name])
                    except FileNotFoundError:
                        # This specific FileNotFoundError will have e.filename = app_name
                        if os.name == 'nt': # Windows fallback
                            self.speak(f"直接打开 {app_name_display} 失败，尝试使用 'start' 命令...")
                            try:
                                # Using 'start' command on Windows can open applications not strictly in PATH
                                # and also handles associated file types.
                                # The empty string '' is for the title argument of the 'start' command.
                                # shell=True is required for 'start' but ensure app_name is not arbitrary user input
                                # that could lead to command injection if not handled carefully.
                                # Here, app_name comes from NLP which should ideally map to known/safe values.
                                subprocess.Popen(['start', '', app_name], shell=True)
                            except Exception as e_start: # Catch any error from 'start'
                                # If 'start' also fails, the original problem was not finding app_name.
                                self.speak(f"使用 'start' 命令打开 {app_name_display} 也失败了。请检查程序名称或路径是否正确。")
                                raise # Re-raise the original FileNotFoundError from the first Popen attempt
                        else: # Non-Windows
                            self.speak(f"找不到应用程序 {app_name_display}。请确保它在您的系统路径中或提供完整路径。")
                            raise # Re-raise the FileNotFoundError
                    except Exception as e_other: # Catch other potential errors from the first Popen (e.g., permissions)
                        self.speak(f"打开 {app_name_display} 时发生错误: {e_other}")
                        # This is not a FileNotFoundError, so it will be caught by the generic Exception handler.
                        raise
                else:
                    self.speak("您想打开哪个应用程序？")
                    return "clarification_needed"

            elif intent == 'open_application_generic':
                self.speak("您想打开哪个应用程序？请说出具体名称。")
                return "clarification_needed"

            elif intent == 'get_time':
                now = datetime.datetime.now().strftime("%H点%M分")
                self.speak(f"现在是{now}")
                return f"Current time is {now}"

            elif intent == 'search_web':
                query = entities.get('search_query')
                if query:
                    self.speak(f"正在为您搜索 {query}")
                    # TODO: Make search engine configurable (e.g., via config.ini)
                    # Example: search_url_template = self.config.get('search_engine_url', 'https://www.bing.com/search?q={query}')
                    # webbrowser.open(search_url_template.format(query=query))
                    webbrowser.open(f"https://www.bing.com/search?q={query}") # Bing is default for now
                    return f"Searched for: {query}"
                else:
                    self.speak("您想搜索什么内容？")
                    return "clarification_needed"
            
            elif intent == 'search_web_generic':
                self.speak("您想搜索什么内容？请说出关键词。")
                return "clarification_needed"

            elif intent == 'greeting':
                self.speak("你好！有什么可以帮您的吗？")
                return "greeted"

            elif intent == 'exit_assistant':
                self.speak("再见！")
                return "exit" # Special command to signal exit
            
            # --- Add more intent handlers here ---
            # elif intent == 'get_weather':
            #     location = entities.get('location', '当前位置')
            #     self.speak(f"正在查询{location}的天气...")
            #     # Call weather API here

            # --- Window Management Intents ---
            elif intent == 'activate_window':
                window_title = entities.get('window_title')
                if not window_title:
                    self.speak("请告诉我需要激活哪个窗口的标题。")
                    return "clarification_needed: window_title_missing"
                if self.desktop_controller.activate_window(window_title_substring=window_title):
                    self.speak(f"窗口 '{window_title}' 已激活。")
                    return f"window_activated: {window_title}"
                else:
                    self.speak(f"激活窗口 '{window_title}' 失败。可能找不到该窗口。")
                    return f"error: activate_window_failed: {window_title}"

            elif intent == 'minimize_window':
                window_title = entities.get('window_title')
                # If no specific window title, try to minimize the active window
                active_window = None
                if not window_title:
                    active_window = self.desktop_controller.get_active_window()
                    if active_window:
                        window_title = active_window.title # Use title of active window for feedback
                    else:
                        self.speak("没有活动的窗口可以最小化，或者请指定窗口标题。")
                        return "clarification_needed: no_active_window_to_minimize"
                
                if self.desktop_controller.minimize_window(window_title_substring=window_title, window_obj=active_window):
                    self.speak(f"窗口 '{window_title}' 已最小化。")
                    return f"window_minimized: {window_title}"
                else:
                    self.speak(f"最小化窗口 '{window_title}' 失败。")
                    return f"error: minimize_window_failed: {window_title}"

            elif intent == 'maximize_window':
                window_title = entities.get('window_title')
                active_window = None
                if not window_title:
                    active_window = self.desktop_controller.get_active_window()
                    if active_window:
                        window_title = active_window.title
                    else:
                        self.speak("没有活动的窗口可以最大化，或者请指定窗口标题。")
                        return "clarification_needed: no_active_window_to_maximize"

                if self.desktop_controller.maximize_window(window_title_substring=window_title, window_obj=active_window):
                    self.speak(f"窗口 '{window_title}' 已最大化。")
                    return f"window_maximized: {window_title}"
                else:
                    self.speak(f"最大化窗口 '{window_title}' 失败。")
                    return f"error: maximize_window_failed: {window_title}"

            elif intent == 'close_window':
                window_title = entities.get('window_title')
                if not window_title:
                    self.speak("请告诉我需要关闭哪个窗口的标题。")
                    return "clarification_needed: window_title_missing_for_close"
                if self.desktop_controller.close_window(window_title_substring=window_title):
                    self.speak(f"窗口 '{window_title}' 已尝试关闭。") # Closing can be asynchronous or blocked by app
                    return f"window_closed_attempted: {window_title}"
                else:
                    self.speak(f"关闭窗口 '{window_title}' 失败。可能找不到该窗口。")
                    return f"error: close_window_failed: {window_title}"
            
            elif intent == 'list_windows':
                windows = self.desktop_controller.list_all_windows()
                if windows:
                    self.speak(f"当前打开的窗口有：{', '.join(windows)}")
                    return f"windows_listed: {len(windows)}"
                else:
                    self.speak("目前没有检测到打开的窗口，或者无法列出它们。")
                    return "info: no_windows_listed_or_error"

            # --- Desktop Control Intents ---
            elif intent == 'capture_screen':
                filename = entities.get('filename', 'screenshot.png')
                region_str = entities.get('region') # e.g., "0,0,800,600"
                region = None
                if region_str:
                    try:
                        region = tuple(map(int, region_str.split(',')))
                        if len(region) != 4:
                            raise ValueError("Region must have 4 values: left,top,width,height")
                    except ValueError as e:
                        self.speak(f"无效的区域格式: {region_str}。应该是 left,top,width,height。将截取全屏。")
                        self.logger.warning(f"Invalid region format for screen capture: {e}")
                        region = None
                
                filepath = self.desktop_controller.capture_screen(filename=filename, region=region)
                if filepath:
                    self.speak(f"屏幕已截图并保存到 {filepath}")
                    return f"screenshot_saved: {filepath}"
                else:
                    self.speak("屏幕截图失败。")
                    return "error: screenshot_failed"

            elif intent == 'move_mouse':
                x = entities.get('x')
                y = entities.get('y')
                duration = entities.get('duration', 0.25)
                relative = entities.get('relative', False)
                if x is None or y is None:
                    self.speak("请告诉我鼠标要移动到哪里，例如 '移动鼠标到 100, 200'。")
                    return "clarification_needed: mouse_coordinates_missing"
                try:
                    x = int(x)
                    y = int(y)
                    duration = float(duration)
                except ValueError:
                    self.speak("鼠标坐标或持续时间格式不正确。")
                    return "error: invalid_mouse_parameters"
                
                if self.desktop_controller.move_mouse(x, y, duration=duration, relative=relative):
                    self.speak(f"鼠标已移动到 ({x}, {y}){'相对位置' if relative else ''}。")
                    return "mouse_moved"
                else:
                    self.speak("移动鼠标失败。")
                    return "error: mouse_move_failed"

            elif intent == 'click_mouse':
                x = entities.get('x')
                y = entities.get('y')
                button = entities.get('button', 'left')
                clicks = entities.get('clicks', 1)
                # Convert x, y, clicks to int if they exist and are strings
                try:
                    x = int(x) if x is not None else None
                    y = int(y) if y is not None else None
                    clicks = int(clicks)
                except ValueError:
                    self.speak("鼠标点击参数格式不正确。")
                    return "error: invalid_click_parameters"

                if self.desktop_controller.click_mouse(x=x, y=y, button=button, clicks=clicks):
                    self.speak(f"在{('坐标 (' + str(x) + ', ' + str(y) + ')') if x is not None and y is not None else '当前位置'}执行了{clicks}次{button}键点击。")
                    return "mouse_clicked"
                else:
                    self.speak("鼠标点击失败。")
                    return "error: mouse_click_failed"

            elif intent == 'type_text':
                text_to_type = entities.get('text')
                if not text_to_type:
                    self.speak("您想输入什么文本？")
                    return "clarification_needed: text_to_type_missing"
                if self.desktop_controller.type_text(text_to_type):
                    self.speak(f"已输入文本: {text_to_type}")
                    return "text_typed"
                else:
                    self.speak("输入文本失败。")
                    return "error: type_text_failed"
            
            elif intent == 'press_key':
                key = entities.get('key_name')
                if not key:
                    self.speak("您想按哪个键？")
                    return "clarification_needed: key_name_missing"
                if self.desktop_controller.press_key(key):
                    self.speak(f"已按下按键: {key}")
                    return "key_pressed"
                else:
                    self.speak(f"按下按键 {key} 失败。")
                    return f"error: press_key_failed_{key}"

            elif intent == 'hotkey':
                keys = entities.get('keys') # Expecting a list or comma-separated string
                if not keys:
                    self.speak("您想执行哪个组合键？")
                    return "clarification_needed: hotkey_keys_missing"
                
                key_list = []
                if isinstance(keys, str):
                    key_list = [k.strip() for k in keys.split(',')]
                elif isinstance(keys, list):
                    key_list = keys
                else:
                    self.speak("组合键格式不正确。")
                    return "error: invalid_hotkey_format"

                if not key_list:
                    self.speak("未指定有效的组合键。")
                    return "error: empty_hotkey_list"

                if self.desktop_controller.hotkey(*key_list):
                    self.speak(f"已执行组合键: {', '.join(key_list)}")
                    return "hotkey_performed"
                else:
                    self.speak(f"执行组合键 {', '.join(key_list)} 失败。")
                    return f"error: hotkey_failed"

            else:
                # Try to handle with tool manager
                intent_to_pass = str(intent) if intent is not None else ""
                current_entities = entities if isinstance(entities, dict) else {}
                current_original_text = str(original_text) if original_text is not None else ''
                self.logger.debug(f"TaskExecutor calling tool_manager.execute_intent (fallback) with intent: {intent_to_pass} (type: {type(intent_to_pass)}), entities: {current_entities} (type: {type(current_entities)}), original_text: {current_original_text} (type: {type(current_original_text)})")
                tool_result = self.tool_manager.execute_intent(intent_to_pass, current_entities, current_original_text)
                if tool_result and not tool_result.startswith('unhandled_intent'):
                    return tool_result
                
                self.speak(f"抱歉，我还不知道如何处理指令 '{original_text}' (意图: {intent})。")
                return f"unhandled_intent: {intent}"
        
        except FileNotFoundError as e:
            # If e.filename is available, use it. Otherwise, a generic message.
            error_detail = f" ({e.filename})" if e.filename else ""
            self.speak(f"执行失败：找不到对应的程序或文件{error_detail}。")
            return f"error: FileNotFoundError - {e.filename if e.filename else str(e)}"
        except Exception as e:
            self.speak(f"执行指令时发生错误: {str(e)}")
            print(f"TaskExecutor Error: {e}")
            return f"error: {str(e)}"
        
        return "success"

# Example Usage (for testing this module directly)
if __name__ == '__main__':
    # Define a simple print function to act as speak for testing
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
    def test_speak(text):
        print(f"[TestSpeak] Addy: {text}")
    
    # Create a dummy config for testing paths
    class DummyConfig:
        def get(self, section, option, fallback=None):
            if section == 'Paths' and option == 'screenshots_dir':
                return 'test_task_executor_screenshots' # Use a specific dir for these tests
            return fallback

    executor = TaskExecutor(config=DummyConfig(), tts_engine_speak_func=test_speak)

    test_intents = [
        {'intent': 'open_application', 'entities': {'application_name': 'notepad.exe'}, 'original_text': '打开记事本'},
        {'intent': 'open_application', 'entities': {'application_name': 'calc.exe'}, 'original_text': '打开计算器'},
        {'intent': 'open_application', 'entities': {'application_name': 'browser', 'specific_browser': 'chrome'}, 'original_text': '打开chrome'},
        {'intent': 'get_time', 'entities': {}, 'original_text': '现在几点'},
        {'intent': 'search_web', 'entities': {'search_query': 'python programming'}, 'original_text': '搜索python programming'},
        {'intent': 'greeting', 'entities': {}, 'original_text': '你好'},
        {'intent': 'exit_assistant', 'entities': {}, 'original_text': '再见'},
        {'intent': 'unknown_intent', 'entities': {}, 'original_text': '随便说点什么'},
        {'intent': 'open_application', 'entities': {'application_name': 'nonexistent_app.exe'}, 'original_text': '打开一个不存在的应用'},
        {'intent': 'search_web_generic', 'entities': {}, 'original_text': '搜索'},
        # Desktop controller tests
        {'intent': 'capture_screen', 'entities': {'filename': 'test_fullscreen.png'}, 'original_text': '截个图'},
        {'intent': 'capture_screen', 'entities': {'filename': 'test_region.png', 'region': '0,0,400,400'}, 'original_text': '截取左上角400x400区域'},
        # {'intent': 'move_mouse', 'entities': {'x': '100', 'y': '150'}, 'original_text': '鼠标移动到100,150'}, # Careful with these
        # {'intent': 'click_mouse', 'entities': {'x': '200', 'y': '250', 'button': 'left', 'clicks': '1'}, 'original_text': '点击200,250'}, # Careful
        # {'intent': 'type_text', 'entities': {'text': 'Hello from Addy!'}, 'original_text': '输入 Hello from Addy!'}, # Careful
        # {'intent': 'press_key', 'entities': {'key_name': 'enter'}, 'original_text': '按回车键'}, # Careful
        # {'intent': 'hotkey', 'entities': {'keys': 'ctrl,a'}, 'original_text': '全选'}, # Careful
        # Window management tests
        {'intent': 'list_windows', 'entities': {}, 'original_text': '列出所有窗口'},
        # The following tests depend on specific windows being open. 
        # For example, to test 'activate_window' for 'Notepad', Notepad must be running.
        # {'intent': 'activate_window', 'entities': {'window_title': 'Notepad'}, 'original_text': '激活记事本窗口'},
        # {'intent': 'minimize_window', 'entities': {'window_title': 'Notepad'}, 'original_text': '最小化记事本窗口'},
        # {'intent': 'maximize_window', 'entities': {'window_title': 'Notepad'}, 'original_text': '最大化记事本窗口'},
        # {'intent': 'close_window', 'entities': {'window_title': 'Notepad'}, 'original_text': '关闭记事本窗口'},
    ]

    for intent_data in test_intents:
        print(f"\n--- Testing Intent: {intent_data['intent']} ---")
        result = executor.execute(intent_data)
        print(f"Execution Result: {result}")
        if result == "exit":
            print("Exit command received, stopping tests.")
            break