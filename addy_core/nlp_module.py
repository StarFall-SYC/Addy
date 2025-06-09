# addy_core/nlp_module.py

import re
import json # For parsing LLM responses if they are JSON formatted

class NLPModule:
    def __init__(self, config_path=None, llm_service=None, nlp_engine='rule_based', tool_manager=None):
        """Initializes the NLP module.

        Args:
            config_path (str, optional): Path to configuration if needed for rule-based system.
            llm_service (object, optional): An instance of a Large Language Model service client.
                                          This object should have a method like `get_intent_and_entities(text)`.
            nlp_engine (str): 'rule_based' or 'llm'. Determines which parsing method to use.
        """
        self.config_path = config_path
        self.llm_service = llm_service
        self.nlp_engine = nlp_engine.lower()
        self.tool_manager = tool_manager # 存储工具管理器实例

        if self.nlp_engine == 'rule_based':
            print("NLP Module Initialized (Engine: Rule-Based).")
            print("Note: This uses a basic rule-based system. Consider Rasa, LUIS, or spaCy for advanced NLP.")
        elif self.nlp_engine == 'llm':
            if self.llm_service:
                print(f"NLP Module Initialized (Engine: LLM - {type(self.llm_service).__name__}).")
                if self.tool_manager:
                    if hasattr(self.llm_service, 'set_tool_manager'):
                        self.llm_service.set_tool_manager(self.tool_manager)
                        print("Tool manager passed to LLM service.")
                        if hasattr(self.llm_service, 'get_supported_tool_protocols'):
                            supported_protocols = self.llm_service.get_supported_tool_protocols()
                            print(f"LLM service supports tool protocols: {supported_protocols}")
                        else:
                            print("NLP Module Info: LLM service does not declare supported tool protocols (get_supported_tool_protocols missing).")
                    else:
                        print("NLP Module Warning: LLM service does not support set_tool_manager.")
                else:
                    print("NLP Module Info: No tool manager provided to NLPModule.")
            else:
                print("NLP Module Warning: LLM engine selected, but no LLM service provided. Falling back to rule-based (if available) or 'unknown'.")
                self.nlp_engine = 'rule_based' # Fallback if LLM service is missing
        else:
            print(f"NLP Module Warning: Unknown NLP engine '{nlp_engine}'. Defaulting to 'rule_based'.")
            self.nlp_engine = 'rule_based'

        # Define application name mappings for normalization (used by rule-based)
        self.app_name_mappings = {
            '记事本': 'notepad.exe',
            'notepad': 'notepad.exe',
            '计算器': 'calc.exe',
            'calculator': 'calc.exe',
            '浏览器': 'browser', 
            'chrome': 'chrome', 
            'edge': 'msedge',
            '火狐': 'firefox',
            'word': 'winword.exe', 
            'excel': 'excel.exe', 
        }

        # Define patterns for intent extraction using regular expressions (used by rule-based)
        self.intent_patterns = [
            {'intent': 'exit_assistant', 'pattern': r"^(再见|拜拜|退出|关闭助手|别说了)$"},
            {'intent': 'greeting', 'pattern': r"^(你好|哈喽|嗨|在吗|你好呀)$"},
            {'intent': 'get_time', 'pattern': r"(现在几点|当前时间|几点钟了|报时)"},
            {
                'intent': 'open_application',
                'pattern': r"(打开|启动|运行|开一下|帮我打开)(?:一个)?(?:叫做)?\s*([\w\s]+?)(?:程序|应用|软件)?(?:吧|呀|行吗)?$",
                'entity_extractors': {'application_name': (2, self._normalize_app_name)}
            },
            {
                'intent': 'open_application',
                'pattern': r"(打开|启动|运行|开一下|帮我打开)\s*([\w\s]+?)(?:吧|呀|行吗)?$",
                'entity_extractors': {'application_name': (2, self._normalize_app_name)}
            },
            {
                'intent': 'search_web',
                'pattern': r"(搜索|查找|查一下|搜一下)(?:关于)?\s*(.+?)(?:的信息|内容)?(?:吧|呀|行吗)?$",
                'entity_extractors': {'search_query': 2}
            },
            {
                'intent': 'search_web_generic',
                'pattern': r"^(搜索|查找|查一下|搜一下)$"
            },
            # Window Management Intents
            {
                'intent': 'activate_window',
                'pattern': r"(激活|切换到|打开|显示)(?:名为|标题为|叫做)?\s*[\"']?(.+?)[\"']?(?:的)?(?:窗口)?",
                'entity_extractors': {'window_title': 2}
            },
            {
                'intent': 'minimize_window',
                'pattern': r"(最小化)(?:名为|标题为|叫做)?\s*[\"']?(.+?)[\"']?(?:的)?(?:窗口)?",
                'entity_extractors': {'window_title': 2}
            },
            {
                'intent': 'minimize_window', # Minimize current/active window
                'pattern': r"(最小化当前窗口|最小化活动窗口|最小化这个窗口|最小化窗口)"
            },
            {
                'intent': 'maximize_window',
                'pattern': r"(最大化)(?:名为|标题为|叫做)?\s*[\"']?(.+?)[\"']?(?:的)?(?:窗口)?",
                'entity_extractors': {'window_title': 2}
            },
            {
                'intent': 'maximize_window', # Maximize current/active window
                'pattern': r"(最大化当前窗口|最大化活动窗口|最大化这个窗口|最大化窗口)"
            },
            {
                'intent': 'close_window',
                'pattern': r"(关闭)(?:名为|标题为|叫做)?\s*[\"']?(.+?)[\"']?(?:的)?(?:窗口)?",
                'entity_extractors': {'window_title': 2}
            },
            {
                'intent': 'list_windows',
                'pattern': r"(列出所有窗口|显示所有窗口|有哪些窗口|打开了哪些窗口)"
            },
            # Desktop Control Intents
            {
                'intent': 'capture_screen',
                'pattern': r"(截屏|截图|屏幕截图|截个图)(?:并保存为)?\s*([\w\-\.]+)?(?:到)?\s*([\d,]+)?",
                'entity_extractors': {'filename': 2, 'region': 3} # region e.g., "0,0,800,600"
            },
            {
                'intent': 'capture_screen',
                'pattern': r"(截屏|截图|屏幕截图|截个图)"
            },
            {
                'intent': 'move_mouse',
                'pattern': r"(移动鼠标|鼠标移动|鼠标移到|把鼠标放到)(?:到)?\s*([-\d]+)\s*[,，]\s*([-\d]+)(?:相对位置)?(?:持续时间)?\s*([\d\.]+)?s?",
                'entity_extractors': {'x': 2, 'y': 3, 'duration': 4, 'relative': lambda m: '相对位置' in m.group(0)}
            },
            {
                'intent': 'move_mouse',
                'pattern': r"(鼠标相对移动|相对移动鼠标)(?:到)?\s*([-\d]+)\s*[,，]\s*([-\d]+)(?:持续时间)?\s*([\d\.]+)?s?",
                'entity_extractors': {'x': 2, 'y': 3, 'duration': 4, 'relative': lambda m: True}
            },
            {
                'intent': 'click_mouse',
                'pattern': r"(点击鼠标|鼠标点击|单击)(?:在)?\s*([-\d]+)\s*[,，]\s*([-\d]+)?(?:用)?(左键|右键|中键)?(?:(\d+)次)?",
                'entity_extractors': {'x': 2, 'y': 3, 'button': 4, 'clicks': 5}
            },
            {
                'intent': 'click_mouse',
                'pattern': r"(点击鼠标|鼠标点击|单击)(?:用)?(左键|右键|中键)?(?:(\d+)次)?",
                'entity_extractors': {'button': 2, 'clicks': 3}
            },
            {
                'intent': 'type_text',
                'pattern': r"(输入文本|打字|输入)\s*(.+)",
                'entity_extractors': {'text': 2}
            },
            {
                'intent': 'press_key',
                'pattern': r"(按下|按一下|按)\s*([\w\s\+]+?)\s*(?:键)?",
                'entity_extractors': {'key_name': 2}
            },
            {
                'intent': 'hotkey',
                'pattern': r"(按下组合键|执行组合键|组合键)\s*(.+)", # Expects keys like "ctrl,shift,t" or "ctrl+alt+delete"
                'entity_extractors': {'keys': 2} # Further processing in TaskExecutor might be needed for splitting keys
            },
            # File Operations
            {
                'intent': 'create_file',
                'pattern': r"(创建|新建)(?:一个)?文件\s*(.+?)(?:在|到)\s*(.+)",
                'entity_extractors': {'filename': 2, 'path': 3}
            },
            {
                'intent': 'create_file',
                'pattern': r"(创建|新建)(?:一个)?文件\s*(.+)",
                'entity_extractors': {'filename': 2}
            },
            {
                'intent': 'delete_file',
                'pattern': r"(删除|移除)文件\s*(.+)",
                'entity_extractors': {'path': 2}
            },
            {
                'intent': 'copy_file',
                'pattern': r"(复制|拷贝)文件\s*(.+?)(?:到)\s*(.+)",
                'entity_extractors': {'source': 2, 'destination': 3}
            },
            {
                'intent': 'move_file',
                'pattern': r"(移动|剪切)文件\s*(.+?)(?:到)\s*(.+)",
                'entity_extractors': {'source': 2, 'destination': 3}
            },
            {
                'intent': 'search_files',
                'pattern': r"(搜索|查找)文件\s*(.+?)(?:在)\s*(.+)",
                'entity_extractors': {'pattern': 2, 'directory': 3}
            },
            {
                'intent': 'search_files',
                'pattern': r"(搜索|查找)文件\s*(.+)",
                'entity_extractors': {'pattern': 2}
            },
            {
                'intent': 'list_files',
                'pattern': r"(列出|显示)(?:目录|文件夹)\s*(.+?)(?:的|中的)?(?:文件|内容)",
                'entity_extractors': {'directory': 2}
            },
            {
                'intent': 'read_file',
                'pattern': r"(读取|查看|打开)文件\s*(.+)",
                'entity_extractors': {'path': 2}
            },
            # System Information
            {
                'intent': 'get_system_info',
                'pattern': r"(获取|查看|显示)(?:系统|电脑)信息"
            },
            {
                'intent': 'get_cpu_usage',
                'pattern': r"(获取|查看|显示)(?:CPU|处理器)(?:使用率|占用率)"
            },
            {
                'intent': 'get_memory_usage',
                'pattern': r"(获取|查看|显示)(?:内存|RAM)(?:使用率|占用率)"
            },
            {
                'intent': 'get_disk_usage',
                'pattern': r"(获取|查看|显示)(?:磁盘|硬盘)(?:使用率|占用率|空间)"
            },
            {
                'intent': 'list_processes',
                'pattern': r"(列出|显示)(?:所有)?(?:进程|程序)"
            },
            {
                'intent': 'kill_process',
                'pattern': r"(结束|终止|杀死)进程\s*(.+)",
                'entity_extractors': {'process_name': 2}
            },
            {
                'intent': 'get_network_info',
                'pattern': r"(获取|查看|显示)网络信息"
            },
            {
                'intent': 'get_battery_info',
                'pattern': r"(获取|查看|显示)电池信息"
            },
            {
                'intent': 'set_volume',
                'pattern': r"(设置|调整)音量(?:到|为)\s*(\d+)",
                'entity_extractors': {'level': 2}
            },
            {
                'intent': 'get_volume',
                'pattern': r"(获取|查看|显示)(?:当前)?音量"
            },
            # Calculator
            {
                'intent': 'calculate',
                'pattern': r"(计算|算一下)\s*(.+)",
                'entity_extractors': {'expression': 2}
            },
            {
                'intent': 'convert_unit',
                'pattern': r"(转换|换算)\s*(\d+(?:\.\d+)?)\s*(\w+)(?:到|为)\s*(\w+)",
                'entity_extractors': {'value': 2, 'from_unit': 3, 'to_unit': 4}
            },
            {
                'intent': 'convert_temperature',
                'pattern': r"(转换|换算)温度\s*(\d+(?:\.\d+)?)\s*(摄氏度|华氏度|开尔文)(?:到|为)\s*(摄氏度|华氏度|开尔文)",
                'entity_extractors': {'value': 2, 'from_unit': 3, 'to_unit': 4}
            },
            # Weather
            {
                'intent': 'get_weather',
                'pattern': r"(查看|获取|显示)(?:(.+?)的)?天气",
                'entity_extractors': {'location': 2}
            },
            {
                'intent': 'get_weather_forecast',
                'pattern': r"(查看|获取|显示)(?:(.+?)的)?天气预报",
                'entity_extractors': {'location': 2}
            },
            {
                'intent': 'get_air_quality',
                'pattern': r"(查看|获取|显示)(?:(.+?)的)?空气质量",
                'entity_extractors': {'location': 2}
            },
            # Email
            {
                'intent': 'send_email',
                'pattern': r"(发送|发)邮件(?:给|到)\s*(.+?)(?:主题|标题)\s*(.+?)(?:内容|正文)\s*(.+)",
                'entity_extractors': {'to': 2, 'subject': 3, 'body': 4}
            },
            {
                'intent': 'read_emails',
                'pattern': r"(查看|读取|显示)(?:最新的|未读的)?邮件"
            },
            {
                'intent': 'search_emails',
                'pattern': r"(搜索|查找)邮件\s*(.+)",
                'entity_extractors': {'query': 2}
            },
            # Calendar
            {
                'intent': 'create_event',
                'pattern': r"(创建|新建|添加)(?:日程|事件|活动)\s*(.+?)(?:在|时间)\s*(.+)",
                'entity_extractors': {'title': 2, 'datetime': 3}
            },
            {
                'intent': 'list_events',
                'pattern': r"(查看|显示|列出)(?:今天|明天|本周|本月)?(?:的)?(?:日程|事件|活动)"
            },
            {
                'intent': 'set_reminder',
                'pattern': r"(设置|添加)提醒\s*(.+?)(?:在|时间)\s*(.+)",
                'entity_extractors': {'message': 2, 'datetime': 3}
            },
            {
                'intent': 'get_date_info',
                'pattern': r"(今天|明天|后天)是(?:几号|什么日期|星期几)"
            },
            # Web Operations
            {
                'intent': 'download_file',
                'pattern': r"(下载)文件\s*(.+?)(?:到|保存到)\s*(.+)",
                'entity_extractors': {'url': 2, 'path': 3}
            },
            {
                'intent': 'download_file',
                'pattern': r"(下载)文件\s*(.+)",
                'entity_extractors': {'url': 2}
            },
            {
                'intent': 'check_website',
                'pattern': r"(检查|测试)网站\s*(.+)",
                'entity_extractors': {'url': 2}
            },
            {
                'intent': 'translate_text',
                'pattern': r"(翻译)\s*(.+?)(?:到|为)\s*(\w+)",
                'entity_extractors': {'text': 2, 'target_language': 3}
            }
        ]

    def _normalize_app_name(self, app_name_match):
        """Normalizes extracted application name using predefined mappings."""
        app_name = app_name_match.strip().lower()
        return self.app_name_mappings.get(app_name, app_name)

    def _parse_intent_rules(self, text_input):
        """Parses intent using the rule-based (regex) system."""
        processed_text = text_input.lower().strip()
        intent_data = {'intent': 'unknown', 'entities': {}, 'original_text': text_input, 'engine': 'rule_based'}

        for item in self.intent_patterns:
            match = re.search(item['pattern'], processed_text, re.IGNORECASE)
            if match:
                intent_data['intent'] = item['intent']
                if 'entity_extractors' in item:
                    for entity_name, extractor_config in item['entity_extractors'].items():
                        raw_entity_match = None
                        if isinstance(extractor_config, tuple):
                            group_index, normalizer_func = extractor_config
                            if group_index <= match.re.groups:
                                raw_entity_match = match.group(group_index)
                            
                            if raw_entity_match is not None:
                                intent_data['entities'][entity_name] = normalizer_func(raw_entity_match) if normalizer_func else raw_entity_match.strip()
                            else:
                                intent_data['entities'][entity_name] = None
                        elif isinstance(extractor_config, int): # Direct group index
                            if extractor_config <= match.re.groups:
                                raw_entity_match = match.group(extractor_config)
                            
                            if raw_entity_match is not None:
                                intent_data['entities'][entity_name] = raw_entity_match.strip()
                            else:
                                intent_data['entities'][entity_name] = None
                        elif callable(extractor_config): # Lambda function for more complex extraction
                            try:
                                intent_data['entities'][entity_name] = extractor_config(match)
                            except IndexError:
                                # Handle cases where lambda might access a group that didn't match
                                intent_data['entities'][entity_name] = None
                        else:
                            # Fallback or error for unhandled extractor_config types
                            intent_data['entities'][entity_name] = None
                break 
        return intent_data

    def _parse_intent_llm(self, text_input):
        """Parses intent using the provided LLM service."""
        if not self.llm_service or not hasattr(self.llm_service, 'get_intent_and_entities'):
            print("NLP Error: LLM service not configured or does not have 'get_intent_and_entities' method.")
            return {'intent': 'unknown', 'entities': {}, 'original_text': text_input, 'engine': 'llm_error'}
        
        try:
            # This is a placeholder for how an LLM might be called.
            # The LLM service's get_intent_and_entities method is now expected to return a JSON string
            # that already standardizes the tool_call information if a tool call is detected, 
            # regardless of the underlying protocol (e.g., OpenAI native vs. custom JSON).
            llm_response_str = self.llm_service.get_intent_and_entities(text_input)
            
            try:
                llm_parsed_response = json.loads(llm_response_str)
                if not isinstance(llm_parsed_response, dict):
                    raise ValueError("LLM response is not a dictionary.")

                # Ensure basic structure and presence of tool_call if applicable.
                # The llm_service should have already formatted this correctly.
                intent = llm_parsed_response.get('intent', 'unknown')
                entities = llm_parsed_response.get('entities', {})
                tool_call = llm_parsed_response.get('tool_call') # This should be in our standardized format.

                # If intent is missing but a tool_call is present, we can infer intent from tool_call name.
                if intent == 'unknown' and tool_call and isinstance(tool_call, dict) and tool_call.get('name'):
                    intent = tool_call['name']
                    llm_parsed_response['intent'] = intent
                    # Optionally, populate entities from tool arguments if entities are empty
                    if not entities and tool_call.get('arguments'):
                        llm_parsed_response['entities'] = tool_call['arguments']
                
                # Ensure 'intent' and 'entities' keys exist even if no specific intent/entities were found.
                if 'intent' not in llm_parsed_response:
                    llm_parsed_response['intent'] = 'unknown'
                if 'entities' not in llm_parsed_response:
                    llm_parsed_response['entities'] = {}

                llm_parsed_response['original_text'] = text_input
                llm_parsed_response['engine'] = 'llm'
                
                if tool_call:
                    print(f"NLP Module (LLM): Detected tool call: {tool_call.get('name')}")
                return llm_parsed_response
                
            except (json.JSONDecodeError, ValueError, TypeError) as e:
                print(f"NLP Warning: Could not parse LLM response as JSON or format is incorrect: {e}. Response: {llm_response_str}")
                return {'intent': 'unknown', 'entities': {'raw_llm_response': llm_response_str}, 'original_text': text_input, 'engine': 'llm_parse_error'}

        except Exception as e:
            print(f"NLP Error: Exception during LLM intent parsing: {e}")
            return {'intent': 'unknown', 'entities': {}, 'original_text': text_input, 'engine': 'llm_exception'}

    def parse_intent(self, text_input):
        """
        Parses the input text to determine user intent and extract entities.
        Uses either rule-based or LLM based on the 'nlp_engine' configuration.

        Args:
            text_input (str): The text spoken by the user (output from ASR).

        Returns:
            dict: A dictionary containing the intent, entities, original text, and engine used.
        """
        if not text_input:
            return {'intent': 'unknown', 'entities': {}, 'original_text': '', 'engine': self.nlp_engine}

        if self.nlp_engine == 'llm' and self.llm_service:
            intent_data = self._parse_intent_llm(text_input)
        else:
            if self.nlp_engine == 'llm' and not self.llm_service:
                print("NLP Info: LLM engine selected but no service provided, falling back to rule-based.")
            intent_data = self._parse_intent_rules(text_input)
        
        if intent_data['intent'] == 'unknown':
            print(f"NLP Parse ({intent_data.get('engine', 'unknown_engine')}): No specific intent found for '{text_input}'. Defaulting to 'unknown'.")
        else:
            print(f"NLP Parse ({intent_data.get('engine', 'unknown_engine')}): '{text_input}' -> Intent: {intent_data['intent']}, Entities: {intent_data['entities']}")
        
        return intent_data

# Example Usage (for testing this module directly)
if __name__ == '__main__':
    nlp = NLPModule()

    test_phrases = [
        "打开记事本",
        "帮我打开计算器",
        "启动 word",
        "开一下 Chrome 浏览器",
        "运行一个叫做 Excel 的应用",
        "现在几点钟了",
        "当前时间",
        "搜索今天北京的天气预报",
        "查一下 Python 编程语言",
        "搜索", # Generic search
        "你好呀",
        "再见",
        "播放周杰伦的歌", # Example of an intent not yet implemented
        "今天星期几",     # Example of an intent not yet implemented
        "完全听不懂你在说什么", # Unknown
    ]

    print("\n--- NLP Module Test ---_normalize_app_name")
    for phrase in test_phrases:
        parsed = nlp.parse_intent(phrase)
        print(f"  Input:    '{phrase}'")
        print(f"  Intent:   {parsed.get('intent')}")
        print(f"  Entities: {parsed.get('entities')}")
        print("  ---------------------")