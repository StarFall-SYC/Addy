# Addy - Windows Voice Assistant
# main.py

import time
import pyttsx3
import os
import logging # For logging
import sys # For PyQt6

import pyaudio # For audio streaming
import struct  # For converting audio bytes

# PyQt6 for GUI
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QSystemTrayIcon, QMenu, QMessageBox
from PyQt6.QtGui import QIcon, QTextCursor, QAction
from PyQt6.QtCore import QThread, pyqtSignal, Qt

# For system tray icon
from PIL import Image # Required by pystray
import pystray

# For Windows Task Scheduler
import win32com.client
import win32com.client.gencache
import pythoncom # Required for COM threading model if Task Scheduler is manipulated in a thread

# Addy custom modules
from utils.config_loader import load_config, get_config_path, get_example_config_path
from addy_core.wake_word_detector import WakeWordDetector
from addy_core.asr_module import ASRModule
from addy_core.nlp_module import NLPModule
from addy_core.task_executor import TaskExecutor
from addy_core.tools.tool_manager import ToolManager

# Global configuration object
CONFIG = None

# --- Logging Setup ---
def setup_logging(config):
    log_file = config.get('Paths', 'log_file', fallback='addy_assistant.log')
    debug_mode = config.getboolean('Miscellaneous', 'debug_mode', fallback=False)
    
    logging.basicConfig(
        level=logging.DEBUG if debug_mode else logging.INFO,
        format='%(asctime)s - %(levelname)s - %(module)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler() # Also print to console
        ]
    )
    logging.info("Logging initialized.")
    if debug_mode:
        logging.debug("Debug mode enabled.")

# --- TTS Engine ---
TTS_ENGINE = None

def initialize_tts(config):
    global TTS_ENGINE
    tts_engine_name = config.get('TTS', 'tts_engine', fallback='pyttsx3').lower()
    logging.info(f"Initializing TTS engine: {tts_engine_name}")
    
    if tts_engine_name == 'pyttsx3':
        try:
            TTS_ENGINE = pyttsx3.init()
            pyttsx3_voice_id = config.get('TTS', 'pyttsx3_voice_id', fallback=None)
            if pyttsx3_voice_id:
                try:
                    TTS_ENGINE.setProperty('voice', pyttsx3_voice_id)
                    logging.info(f"Set pyttsx3 voice ID to: {pyttsx3_voice_id}")
                except Exception as e:
                    logging.error(f"Failed to set pyttsx3 voice ID '{pyttsx3_voice_id}': {e}. Using default.")
            logging.info("pyttsx3 TTS engine initialized.")
        except Exception as e:
            logging.error(f"Error initializing pyttsx3 TTS engine: {e}")
            TTS_ENGINE = None
    elif tts_engine_name == 'azure':
        logging.warning("Azure TTS not yet implemented in this version. Falling back to console print.")
        TTS_ENGINE = None
    else:
        logging.warning(f"Unsupported TTS engine: {tts_engine_name}. Falling back to console print.")
        TTS_ENGINE = None

def speak(text):
    logging.info(f"Addy: {text}")
    if TTS_ENGINE:
        try:
            TTS_ENGINE.say(text)
            TTS_ENGINE.runAndWait()
        except Exception as e:
            logging.error(f"TTS Error: {e}")
    else:
        print(f"(Fallback TTS) Addy: {text}") 

# --- PyQt6 GUI --- 
class AssistantGUI(QWidget):
    log_message_signal = pyqtSignal(str)
    assistant_response_signal = pyqtSignal(str)
    user_input_signal = pyqtSignal(str)

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.init_ui()
        self.assistant_thread = None

    def init_ui(self):
        self.setWindowTitle('Addy 语音助手')
        icon_path = "icon/icon.png"
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            logging.warning(f"Icon file not found at {icon_path}. Using default icon.")

        layout = QVBoxLayout()

        self.status_label = QLabel("状态：等待唤醒...")
        layout.addWidget(self.status_label)

        self.log_text_edit = QTextEdit()
        self.log_text_edit.setReadOnly(True)
        layout.addWidget(self.log_text_edit)

        self.start_button = QPushButton("启动助手")
        self.start_button.clicked.connect(self.start_assistant_thread)
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton("停止助手")
        self.stop_button.clicked.connect(self.stop_assistant_thread)
        self.stop_button.setEnabled(False)
        layout.addWidget(self.stop_button)

        self.setLayout(layout)
        self.resize(600, 400)

        # Connect signals for logging and responses
        self.log_message_signal.connect(self.append_log)
        self.assistant_response_signal.connect(self.display_assistant_response)
        self.user_input_signal.connect(self.display_user_input)

        # System Tray Icon
        self.tray_icon = None
        self.create_tray_icon()

    def append_log(self, message):
        self.log_text_edit.append(message)
        self.log_text_edit.moveCursor(QTextCursor.MoveOperation.End)

    def display_assistant_response(self, message):
        self.append_log(f"Addy: {message}")
        self.status_label.setText("状态：等待唤醒...")

    def display_user_input(self, message):
        self.append_log(f"用户: {message}")
        self.status_label.setText("状态：正在处理...")

    def start_assistant_thread(self):
        if not self.assistant_thread or not self.assistant_thread.isRunning():
            self.assistant_thread = AssistantThread(self.config, self)
            self.assistant_thread.log_message.connect(self.log_message_signal)
            self.assistant_thread.assistant_response.connect(self.assistant_response_signal)
            self.assistant_thread.user_input.connect(self.user_input_signal)
            self.assistant_thread.status_update.connect(self.status_label.setText)
            self.assistant_thread.start()
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.status_label.setText("状态：正在运行...")
            self.append_log("助手线程已启动。")

    def stop_assistant_thread(self):
        if self.assistant_thread and self.assistant_thread.isRunning():
            self.assistant_thread.stop()
            # self.assistant_thread.wait() # Wait for thread to finish cleanly
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.status_label.setText("状态：已停止")
            self.append_log("助手线程已请求停止。")

    def create_tray_icon(self):
        icon_path = "icon/icon.png"
        if os.path.exists(icon_path):
            icon_image = Image.open(icon_path)
            self.startup_action_text = "禁用开机自启" if self.is_startup_task_enabled() else "启用开机自启"
            menu = (
                pystray.MenuItem('显示窗口', self.show_window, default=True, visible=False),
                pystray.MenuItem('设置', self.show_settings_window),
                pystray.MenuItem(lambda item: self.startup_action_text, self.toggle_startup_task),
                pystray.MenuItem('暂停服务', self.toggle_pause_service),
                pystray.MenuItem('退出服务', self.quit_application)
            )
            self.tray_icon = pystray.Icon("addy_assistant", icon_image, "Addy 语音助手", menu)
            # Run the tray icon in a separate thread to avoid blocking the Qt event loop
            import threading
            tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
            tray_thread.start()
            logging.info("System tray icon created.")
        else:
            logging.warning(f"Icon file not found at {icon_path} for tray icon. Tray icon not created.")

    def show_window(self):
        self.showNormal()
        self.activateWindow()

    def toggle_pause_service(self):
        if self.assistant_thread and self.assistant_thread.isRunning():
            current_text_item = self.tray_icon.menu[2] # Assuming '暂停服务' is the third item (index 2)
            if "暂停服务" in current_text_item.text:
                self.assistant_thread.pause_service()
                current_text_item.text = "继续服务"
                self.status_label.setText("状态：服务已暂停")
                self.append_log("服务已暂停。")
                logging.info("Service paused.")
            else:
                self.assistant_thread.resume_service()
                current_text_item.text = "暂停服务"
                # Restore appropriate running status, might need to get it from thread
                self.status_label.setText("状态：等待唤醒...") 
                self.append_log("服务已恢复。")
                logging.info("Service resumed.")
            if self.tray_icon: # pystray needs explicit menu update for text changes
                self.tray_icon.update_menu()
        else:
            logging.info("Assistant thread not running, cannot pause/resume.")

    def is_startup_task_enabled(self):
        pythoncom.CoInitialize() # Initialize COM
        task_name = "AddyVoiceAssistantStartup"
        try:
            # 使用 EnsureDispatch 替代 Dispatch，确保 COM 类型库被正确加载和缓存
            scheduler = win32com.client.gencache.EnsureDispatch('Schedule.Service')
            scheduler.Connect()
            root_folder = scheduler.GetFolder('\\')
            try:
                task = root_folder.GetTask(task_name)
                return task.Enabled
            except pythoncom.com_error as e:
                if e.hresult == -2147023728: # 0x80070490 - Element not found
                    return False # Task does not exist
                raise # Other COM error
        except Exception as e:
            logging.error(f"Error checking startup task status: {e}")
            return False # Assume not enabled on error
        finally:
            pythoncom.CoUninitialize() # Uninitialize COM

    def toggle_startup_task(self):
        if self.is_startup_task_enabled():
            if delete_startup_task():
                self.startup_action_text = "启用开机自启"
                self.append_log("已禁用开机自启。")
                logging.info("Startup task disabled by user.")
            else:
                self.append_log("禁用开机自启失败。")
        else:
            if create_startup_task():
                self.startup_action_text = "禁用开机自启"
                self.append_log("已启用开机自启。")
                logging.info("Startup task enabled by user.")
            else:
                self.append_log("启用开机自启失败。")
        # pystray menu items with dynamic text need a manual update
        if self.tray_icon:
            self.tray_icon.update_menu()

    def show_settings_window(self):
        # Placeholder for showing the settings dialog
        logging.info("Settings window requested.")
        # Ensure pythoncom is initialized if COM objects are used in a new thread for settings
        # pythoncom.CoInitialize() # If settings dialog runs in a separate thread and uses COM
        # Try with parent=None to see if it resolves the QObject::setParent thread issue
        settings_dialog = SettingsDialog(self.config, None) # Pass None as parent
        settings_dialog.exec()
        # pythoncom.CoUninitialize() # If CoInitialize was called

    def quit_application(self):
        logging.info("Quit application requested from tray icon.")
        if self.tray_icon:
            self.tray_icon.stop()
        self.stop_assistant_thread()
        QApplication.instance().quit()

    def closeEvent(self, event):
        # Override close event to hide to tray instead of quitting
        event.ignore()
        self.hide()
        if self.tray_icon:
            # self.tray_icon.notify('Addy 仍在后台运行', '点击托盘图标可进行操作') # Optional notification
            logging.info("Window closed, application hidden to tray.")
        else:
            # Fallback if tray icon failed to create, then actually quit
            self.quit_application()

# --- Assistant Logic Thread ---
class AssistantThread(QThread):
    log_message = pyqtSignal(str)
    assistant_response = pyqtSignal(str)
    user_input = pyqtSignal(str)
    status_update = pyqtSignal(str)

    def __init__(self, config, gui_ref):
        super().__init__()
        self.config = config
        self.gui = gui_ref # Reference to GUI for emitting signals
        self._is_running = True
        self._is_paused = False # New flag for pausing service
        self.wake_word_detector = None
        self.asr_module = None
        self.nlp_module = None
        self.task_executor = None
        self.pa = None
        self.stream = None

    def speak_and_log(self, text):
        self.log_message.emit(f"Addy (TTS): {text}")
        speak(text) # Uses global TTS_ENGINE
        self.assistant_response.emit(text)

    def run(self):
        global WAKE_WORDS # Access global WAKE_WORDS defined in main scope
        self.log_message.emit("助手核心逻辑线程启动。")
        self.status_update.emit("状态：初始化...")

        # Initialize core modules within the thread
        porcupine_access_key = self.config.get('Porcupine', 'access_key', fallback=None)
        if not porcupine_access_key or porcupine_access_key == 'YOUR_ACCESS_KEY_HERE':
            self.log_message.emit("错误：Porcupine AccessKey 未在配置文件中设置。请访问 https://picovoice.ai/platform/porcupine/ 获取密钥。")
            self.speak_and_log("Porcupine AccessKey 未设置，无法启动唤醒词检测。")
            self.status_update.emit("状态：错误 - Porcupine Key 未配置")
            self._is_running = False
            return

        keyword_paths_str = self.config.get('Porcupine', 'keyword_paths', fallback=None)
        if not keyword_paths_str:
            self.log_message.emit("错误：Porcupine keyword_paths 未在配置文件中设置。")
            self.speak_and_log("Porcupine 唤醒词文件路径未设置。")
            self.status_update.emit("状态：错误 - Porcupine 唤醒词路径未配置")
            self._is_running = False
            return
        
        actual_keyword_paths = [WAKE_WORDS[word]['keyword_path'] for word in WAKE_WORDS if WAKE_WORDS[word]['keyword_path']]
        if not actual_keyword_paths:
            self.log_message.emit(f"错误：在 {WAKE_WORDS} 中找不到有效的 Porcupine 唤醒词文件路径。请检查配置文件和唤醒词文件。")
            self.speak_and_log("未找到有效的 Porcupine 唤醒词文件。")
            self.status_update.emit("状态：错误 - 无有效唤醒词文件")
            self._is_running = False
            return

        sensitivities_str = self.config.get('Porcupine', 'sensitivities', fallback=None)
        sensitivities = [float(s.strip()) for s in sensitivities_str.split(',')] if sensitivities_str else [0.5] * len(actual_keyword_paths)
        if len(sensitivities) != len(actual_keyword_paths):
            self.log_message.emit(f"警告：灵敏度数量 ({len(sensitivities)}) 与关键词路径数量 ({len(actual_keyword_paths)}) 不匹配。将对所有关键词使用默认灵敏度 0.5。")
            sensitivities = [0.5] * len(actual_keyword_paths)

        try:
            self.wake_word_detector = WakeWordDetector(
                access_key=porcupine_access_key,
                keyword_paths=actual_keyword_paths,
                sensitivities=sensitivities,
                library_path=self.config.get('Porcupine', 'library_path', fallback=None),
                model_path=self.config.get('Porcupine', 'model_path', fallback=None)
            )
            self.log_message.emit(f"唤醒词检测器 (Porcupine) 初始化成功，使用关键词: {', '.join([os.path.basename(p) for p in actual_keyword_paths])}")
        except Exception as e:
            self.log_message.emit(f"错误：初始化 Porcupine 唤醒词检测器失败: {e}")
            self.speak_and_log(f"初始化唤醒词检测器失败: {e}")
            self.status_update.emit("状态：错误 - 唤醒词检测器初始化失败")
            self._is_running = False
            return

        self.asr_module = ASRModule(config=self.config)
        
        # Initialize NLP Module with potential LLM service
        import json
        from addy_core.llm_services.llm_factory import LLMServiceFactory
        
        nlp_engine_config = self.config.get('NLP', 'engine', fallback='rule_based').lower()
        if nlp_engine_config == 'llm':
            # 获取配置的LLM服务类型
            llm_service_type = self.config.get('NLP', 'llm_service', fallback='openai').lower()
            
            # 使用LLM服务工厂创建相应的服务实例
            self.llm_service = LLMServiceFactory.create_llm_service(
                service_type=llm_service_type,
                config=self.config,
                log_func=self.log_message.emit
            )
            
            # 检查服务是否可用
            if self.llm_service and self.llm_service.is_available():
                self.log_message.emit(f"NLP引擎配置为 'llm'。将使用 {type(self.llm_service).__name__}。")
            else:
                # 如果配置的服务不可用，使用MockLLMService作为后备
                self.log_message.emit(f"警告：配置的LLM服务 '{llm_service_type}' 不可用。将使用MockLLMService作为后备。")
                
                class MockLLMService:
                    def __init__(self, log_func=None):
                        self.log_func = log_func
                        
                    def set_logger(self, log_func):
                        self.log_func = log_func
                        
                    def _log(self, message):
                        if self.log_func:
                            self.log_func(f"MockLLMService: {message}")
                        else:
                            print(f"MockLLMService: {message}")
                            
                    def get_intent_and_entities(self, text):
                        self._log(f"收到文本: {text}。返回占位符意图。")
                        # 模拟LLM返回包含意图和实体的JSON字符串
                        return json.dumps({'intent': 'llm_placeholder', 'entities': {'query': text}, 'detail': 'This is a mock LLM response.'})
                    
                    def generate_response(self, text, context=None):
                        self._log(f"收到生成请求: {text}")
                        return "这是一个模拟的LLM响应。实际集成后，将返回真实的LLM生成内容。"
                    
                    def is_available(self):
                        return True
                
                self.llm_service = MockLLMService(log_func=self.log_message.emit)
        else:
            self.llm_service = None
            self.log_message.emit(f"NLP引擎配置为 'rule_based'。")

        # 初始化 ToolManager
        self.tool_manager = ToolManager(config=self.config, log_func=self.log_message.emit)

        self.nlp_module = NLPModule(
            config_path=get_config_path(), 
            llm_service=self.llm_service, 
            nlp_engine=nlp_engine_config,
            tool_manager=self.tool_manager  # 传递 ToolManager 实例
        )
        self.task_executor = TaskExecutor(config=self.config, tts_engine_speak_func=self.speak_and_log, tool_manager=self.tool_manager)

        self.log_message.emit("核心模块初始化完成。")
        self.status_update.emit("状态：等待唤醒...")

        if self.wake_word_detector:
            try:
                self.pa = pyaudio.PyAudio()
                self.stream = self.pa.open(
                    rate=self.wake_word_detector.porcupine.sample_rate,
                    channels=1,
                    format=pyaudio.paInt16,
                    input=True,
                    frames_per_buffer=self.wake_word_detector.porcupine.frame_length
                )
                self.log_message.emit("PyAudio 音频流已为唤醒词检测打开。")
            except Exception as e:
                self.log_message.emit(f"错误：打开 PyAudio 音频流失败: {e}")
                self.speak_and_log("无法打开麦克风进行唤醒词检测。")
                self.wake_word_detector = None # Disable if stream fails
                self.cleanup_audio_resources()

        self.speak_and_log("Addy 语音助手已在后台启动。")
        self.log_message.emit(f"助手已启动。等待唤醒词: {WAKE_WORDS}")
        self.status_update.emit("状态：等待唤醒...")

        try:
            while self._is_running:
                if self._is_paused:
                    self.status_update.emit("状态：服务已暂停")
                    time.sleep(0.5) # Sleep while paused to reduce CPU usage
                    continue # Skip main loop logic when paused

                if self.wake_word_detector and self.stream:
                    self.status_update.emit("状态：监听唤醒词...")
                    pcm = self.stream.read(self.wake_word_detector.porcupine.frame_length, exception_on_overflow=False)
                    pcm = struct.unpack_from("h" * self.wake_word_detector.porcupine.frame_length, pcm)
                    
                    keyword_index = self.wake_word_detector.porcupine.process(pcm)
                    if keyword_index >= 0:
                        detected_wake_word = WAKE_WORDS[keyword_index] # Assuming WAKE_WORDS aligns with keyword_paths
                        self.log_message.emit(f"检测到唤醒词: {detected_wake_word}")
                        self.status_update.emit("状态：听到唤醒词！正在聆听指令...")
                        self.speak_and_log("我在，请说。") # Notify user
                        
                        # After wake word, listen for command using continuous listening
                        self.log_message.emit("ASR: Starting continuous listening for command.")
                        
                        continuous_audio_data = self.asr_module.listen_continuous(
                            max_record_seconds=self.config.getint('ASR', 'continuous_max_record_seconds', fallback=30),
                            silence_threshold=self.config.getfloat('ASR', 'continuous_silence_threshold', fallback=1.0),
                            phrase_time_limit=self.config.getint('ASR', 'continuous_phrase_time_limit', fallback=5)
                        )
                        
                        # Stop Porcupine stream after wake word detection and command listen
                        if self.stream:
                            if self.stream.is_active():
                                self.stream.stop_stream()
                            self.stream.close()
                            self.log_message.emit("ASR: Porcupine audio stream stopped and closed for command listening.")
                        self.stream = None 
                        
                        if self.pa:
                            self.pa.terminate()
                            self.log_message.emit("ASR: PyAudio instance terminated for command listening.")
                        self.pa = None

                        user_input_text = None
                        if continuous_audio_data:
                            self.log_message.emit("ASR: Continuous audio captured, now recognizing.")
                            self.status_update.emit("状态：正在识别语音...")
                            user_input_text = self.asr_module.recognize_audio_data(continuous_audio_data)
                        else:
                            self.log_message.emit("ASR: No audio captured during continuous listening.")
                            self.speak_and_log("抱歉，我没有听到您的指令。")
                        if user_input_text:
                            self.user_input.emit(user_input_text)
                            self.status_update.emit("状态：处理指令...")
                            intent_data = self.nlp_module.parse_intent(user_input_text)
                            self.log_message.emit(f"NLP 解析结果: {intent_data}")
                            if intent_data and intent_data.get('intent'):
                                self.task_executor.execute_task(intent_data)
                                if intent_data['intent'] == 'exit':
                                    self.speak_and_log("好的，再见。")
                                    self._is_running = False # Stop the loop
                                    self.gui.close() # Request GUI to close
                                    break 
                            else:
                                self.speak_and_log("抱歉，我不太明白您的意思。")
                        else:
                            self.speak_and_log("抱歉，我没有听清楚。")
                        self.status_update.emit("状态：等待唤醒...") # Reset status after command processing
                else: # Fallback if no wake word detector
                    self.status_update.emit("状态：手动模式，请输入指令...") # Or handle differently
                    self.log_message.emit("唤醒词检测未启用。请通过其他方式触发指令（未实现）。")
                    # This part needs a way to get input if wake word is off, e.g., GUI button or console input
                    # For now, it will just loop doing nothing if wake word is off.
                    time.sleep(1) # Prevent busy-looping
                    if not self._is_running: break # Check stop flag
        except KeyboardInterrupt:
            self.log_message.emit("通过 Ctrl+C 请求停止助手。")
        except Exception as e:
            self.log_message.emit(f"助手线程发生意外错误: {e}")
            logging.exception("Exception in AssistantThread run loop") # Log full traceback
        finally:
            self.log_message.emit("助手核心逻辑线程正在停止...")
            self.cleanup_audio_resources()
            if self.wake_word_detector:
                self.wake_word_detector.delete()
                self.log_message.emit("Porcupine 资源已释放。")
            self.status_update.emit("状态：已停止")
            self.log_message.emit("助手核心逻辑线程已停止。")

    def pause_service(self):
        self.log_message.emit("服务暂停中...")
        self._is_paused = True
        # Potentially stop audio stream if it's active and not needed while paused
        if self.stream and self.stream.is_active():
            self.stream.stop_stream()
            self.log_message.emit("Audio stream stopped due to service pause.")

    def resume_service(self):
        self.log_message.emit("服务恢复中...")
        self._is_paused = False
        # Potentially restart audio stream if it was stopped and is needed
        # This might require re-opening the stream if it was closed
        if self.wake_word_detector and not (self.stream and self.stream.is_active()):
            try:
                if not self.pa:
                    self.pa = pyaudio.PyAudio()
                if self.stream:
                    try: self.stream.close() # Ensure old stream is closed
                    except: pass
                self.stream = self.pa.open(
                    rate=self.wake_word_detector.porcupine.sample_rate,
                    channels=1,
                    format=pyaudio.paInt16,
                    input=True,
                    frames_per_buffer=self.wake_word_detector.porcupine.frame_length
                )
                self.log_message.emit("PyAudio 音频流已为唤醒词检测重新打开。")
            except Exception as e:
                self.log_message.emit(f"错误：恢复服务时重新打开 PyAudio 音频流失败: {e}")
                # Handle error, maybe set to paused again or notify user

    def stop(self):
        self.log_message.emit("接收到停止信号。")
        self._is_running = False
        # No need to join here, let the run loop exit naturally

    def cleanup_audio_resources(self):
        if self.stream:
            try:
                if self.stream.is_active():
                    self.stream.stop_stream()
                self.stream.close()
                self.log_message.emit("PyAudio 音频流已关闭。")
            except Exception as e:
                self.log_message.emit(f"关闭 PyAudio 音频流时出错: {e}")
            self.stream = None
        if self.pa:
            try:
                self.pa.terminate()
                self.log_message.emit("PyAudio 实例已终止。")
            except Exception as e:
                self.log_message.emit(f"终止 PyAudio 实例时出错: {e}")
            self.pa = None

# --- Startup Task Management --- 
import pythoncom # Add this import

def create_startup_task():
    pythoncom.CoInitialize() # Initialize COM
    task_name = "AddyVoiceAssistantStartup"
    executable_path = os.path.abspath(sys.executable) # Path to python.exe
    script_path = os.path.abspath(__file__) # Path to main.py
    working_directory = os.path.dirname(script_path)

    try:
        # 使用 EnsureDispatch 替代 Dispatch，确保 COM 类型库被正确加载和缓存
        scheduler = win32com.client.gencache.EnsureDispatch('Schedule.Service')
        scheduler.Connect()
        root_folder = scheduler.GetFolder('\\')
        task_def = scheduler.NewTask(0)

        # Create trigger (on logon)
        trigger = task_def.Triggers.Create(9) # TASK_TRIGGER_LOGON = 9
        trigger.Id = 'LogonTriggerId'
        # trigger.UserId = os.getlogin() # Optional: run for current user, requires admin to set for all users

        # Create action (start program)
        action = task_def.Actions.Create(0) # TASK_ACTION_EXEC = 0
        action.Path = executable_path
        action.Arguments = f'"{script_path}"'
        action.WorkingDirectory = working_directory

        task_def.RegistrationInfo.Description = 'Starts Addy Voice Assistant on user logon.'
        task_def.RegistrationInfo.Author = 'AddyAssistant'
        task_def.Settings.Enabled = True
        task_def.Settings.StopIfGoingOnBatteries = False
        task_def.Settings.DisallowStartIfOnBatteries = False
        task_def.Settings.ExecutionTimeLimit = "PT0S" # Unlimited
        task_def.Settings.StartWhenAvailable = True # Run task as soon as possible after a scheduled start is missed

        # Register the task (will overwrite if exists with same name)
        # TASK_CREATE_OR_UPDATE = 6
        # TASK_LOGON_NONE = 0 (no password needed for this type of task)
        root_folder.RegisterTaskDefinition(
            task_name,
            task_def,
            6, # TASK_CREATE_OR_UPDATE
            None, # User (None for LocalSystem or if UserId in trigger)
            None, # Password
            3    # TASK_LOGON_INTERACTIVE_TOKEN = 3 (Runs only when user is logged on)
        )
        logging.info(f"Startup task '{task_name}' created/updated successfully.")
        return True
    except Exception as e:
        logging.error(f"Failed to create/update startup task '{task_name}': {e}")
        return False
    finally:
        pythoncom.CoUninitialize() # Uninitialize COM

def delete_startup_task():
    pythoncom.CoInitialize() # Initialize COM
    task_name = "AddyVoiceAssistantStartup"
    try:
        # 使用 EnsureDispatch 替代 Dispatch，确保 COM 类型库被正确加载和缓存
        scheduler = win32com.client.gencache.EnsureDispatch('Schedule.Service')
        scheduler.Connect()
        root_folder = scheduler.GetFolder('\\')
        root_folder.DeleteTask(task_name, 0)
        logging.info(f"Startup task '{task_name}' deleted successfully.")
        return True
    except pythoncom.com_error as e:
        if e.hresult == -2147023728: # 0x80070490 - Element not found
            logging.info(f"Startup task '{task_name}' not found, no need to delete.")
            return True # Consider it success if not found
        logging.error(f"Failed to delete startup task '{task_name}': {e} (HRESULT: {e.hresult})")
        return False
    except Exception as e:
        logging.error(f"Failed to delete startup task '{task_name}': {e}")
        return False
    finally:
        pythoncom.CoUninitialize() # Uninitialize COM

# --- Main Application Execution ---
WAKE_WORDS = [] # Define WAKE_WORDS globally so AssistantThread can access it

def main():
    global CONFIG, WAKE_WORDS
    CONFIG = load_config()
    setup_logging(CONFIG)
    initialize_tts(CONFIG)

    wake_words_str = CONFIG.get('General', 'wake_words', fallback='addy你好')
    WAKE_WORDS = [word.strip().lower() for word in wake_words_str.split(',') if word.strip()]
    if not WAKE_WORDS:
        logging.error("错误：未配置唤醒词。请检查 config.ini。")
        # If GUI is planned, show error in GUI instead of just speaking
        # For now, we'll let the AssistantThread handle this and log to GUI if it's running

    app = QApplication(sys.argv)
    # Prevent multiple instances
    app.setQuitOnLastWindowClosed(False) 

    gui = AssistantGUI(CONFIG)
    # gui.show() # Don't show main window initially

    # Show a startup notification popup
    QMessageBox.information(None, "Addy 启动通知", "Addy 语音助手已在后台启动，您可以通过系统托盘图标进行操作。", QMessageBox.StandardButton.Ok)
    logging.info("Application started and hidden to tray initially.")

    # Start assistant thread automatically if configured, or wait for tray/GUI interaction
    # For now, let's assume it starts automatically if tray icon is present
    if gui.tray_icon:
        gui.start_assistant_thread() # Auto-start the assistant if tray is up
    
    # The assistant logic is now started by the GUI's "Start Assistant" button
    # or automatically if tray icon is present.

    # Create startup task if not exists (or if user enables it later via tray)
    # For initial setup, let's try to create it. User can disable via tray.
    # We might want to make this configurable or a first-time setup option.
    if CONFIG.getboolean('General', 'auto_start_on_boot', fallback=True):
        if not gui.is_startup_task_enabled(): # Check first to avoid unnecessary overwrites if already correctly set
            create_startup_task()
    
    # The main application event loop execution must be the last call in main()
    sys.exit(app.exec())

# --- Settings Dialog --- (Could be in a separate file for better organization)
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout, QMessageBox
from PyQt6.QtCore import Qt
import configparser

# --- Settings Dialog --- (Could be in a separate file for better organization)
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QMessageBox, QLineEdit, QLabel, QComboBox, QScrollArea, QWidget, QFormLayout
from PyQt6.QtCore import Qt
import configparser

class SettingsDialog(QDialog):
    def __init__(self, current_config_obj, parent=None):
        super().__init__(parent)
        self.config_path = get_config_path()
        self.config_parser = configparser.ConfigParser()
        self.current_config_obj = current_config_obj # Keep a reference
        self.setWindowTitle("Addy 设置")
        self.setMinimumSize(600, 500)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.controls = {}  # To store references to input controls
        self.init_ui()
        self.load_config_to_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)

        scroll_content_widget = QWidget()
        scroll_area.setWidget(scroll_content_widget)
        
        form_layout = QFormLayout(scroll_content_widget) # Use QFormLayout for label-field pairs

        # Example: General Settings
        general_group_label = QLabel("通用设置")
        general_group_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        form_layout.addRow(general_group_label)

        self.controls[('General', 'language')] = QLineEdit()
        form_layout.addRow(QLabel("助手语言 (language):"), self.controls[('General', 'language')])

        self.controls[('General', 'wake_words')] = QLineEdit()
        form_layout.addRow(QLabel("唤醒词 (wake_words, 逗号分隔):"), self.controls[('General', 'wake_words')])
        
        self.controls[('General', 'auto_start_on_boot')] = QComboBox()
        self.controls[('General', 'auto_start_on_boot')].addItems(["True", "False"])
        form_layout.addRow(QLabel("开机自启 (auto_start_on_boot):"), self.controls[('General', 'auto_start_on_boot')])

        # Example: NLP Settings
        nlp_group_label = QLabel("NLP 设置")
        nlp_group_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        form_layout.addRow(nlp_group_label)

        self.controls[('NLP', 'engine')] = QComboBox()
        self.controls[('NLP', 'engine')].addItems(["rule_based", "llm"])
        form_layout.addRow(QLabel("NLP 引擎 (engine):"), self.controls[('NLP', 'engine')])

        self.controls[('NLP', 'llm_service')] = QComboBox()
        # These should ideally be dynamically populated or from a more robust source
        self.controls[('NLP', 'llm_service')].addItems(["openai", "claude", "tongyi", "gemini", "mock"])
        form_layout.addRow(QLabel("LLM 服务 (llm_service):"), self.controls[('NLP', 'llm_service')])

        # ASR Settings
        asr_group_label = QLabel("ASR 设置")
        asr_group_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        form_layout.addRow(asr_group_label)

        self.controls[('ASR', 'engine')] = QComboBox()
        self.controls[('ASR', 'engine')].addItems(["vosk", "azure", "google"])
        form_layout.addRow(QLabel("ASR 引擎 (engine):"), self.controls[('ASR', 'engine')])
        # Add more ASR specific settings like model_path for vosk, keys for azure/google if needed

        # TTS Settings
        tts_group_label = QLabel("TTS 设置")
        tts_group_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        form_layout.addRow(tts_group_label)

        self.controls[('TTS', 'tts_engine')] = QComboBox()
        self.controls[('TTS', 'tts_engine')].addItems(["pyttsx3", "azure"])
        form_layout.addRow(QLabel("TTS 引擎 (tts_engine):"), self.controls[('TTS', 'tts_engine')])
        self.controls[('TTS', 'pyttsx3_voice_id')] = QLineEdit()
        form_layout.addRow(QLabel("pyttsx3 Voice ID (pyttsx3_voice_id):"), self.controls[('TTS', 'pyttsx3_voice_id')])
        # Add Azure TTS specific settings if needed

        # Porcupine Wake Word Settings
        porcupine_group_label = QLabel("Porcupine 唤醒词设置")
        porcupine_group_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        form_layout.addRow(porcupine_group_label)

        self.controls[('Porcupine', 'access_key')] = QLineEdit()
        form_layout.addRow(QLabel("AccessKey (access_key):"), self.controls[('Porcupine', 'access_key')])
        self.controls[('Porcupine', 'keyword_paths')] = QLineEdit()
        form_layout.addRow(QLabel("关键词文件路径 (keyword_paths, 逗号分隔):"), self.controls[('Porcupine', 'keyword_paths')])
        self.controls[('Porcupine', 'sensitivities')] = QLineEdit()
        form_layout.addRow(QLabel("灵敏度 (sensitivities, 逗号分隔):"), self.controls[('Porcupine', 'sensitivities')])

        # LLM Services API Keys and Models
        llm_keys_group_label = QLabel("LLM 服务 API 密钥和模型")
        llm_keys_group_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        form_layout.addRow(llm_keys_group_label)

        llm_services = ["OpenAI", "Claude", "Tongyi", "Gemini"]
        for service in llm_services:
            self.controls[(service, 'api_key')] = QLineEdit()
            self.controls[(service, 'api_key')].setEchoMode(QLineEdit.EchoMode.Password)
            form_layout.addRow(QLabel(f"{service} API Key (api_key):"), self.controls[(service, 'api_key')])
            
            self.controls[(service, 'model_name')] = QLineEdit()
            form_layout.addRow(QLabel(f"{service} 模型名称 (model_name):"), self.controls[(service, 'model_name')])
            
            if service in ["OpenAI", "Claude"]: # Services that might have a base URL
                self.controls[(service, 'api_base_url')] = QLineEdit()
                form_layout.addRow(QLabel(f"{service} API Base URL (api_base_url, 可选):"), self.controls[(service, 'api_base_url')])

        # Miscellaneous Settings
        misc_group_label = QLabel("其他设置")
        misc_group_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        form_layout.addRow(misc_group_label)

        self.controls[('Miscellaneous', 'debug_mode')] = QComboBox()
        self.controls[('Miscellaneous', 'debug_mode')].addItems(["False", "True"])
        form_layout.addRow(QLabel("调试模式 (debug_mode):"), self.controls[('Miscellaneous', 'debug_mode')])

        button_layout = QHBoxLayout()
        self.save_button = QPushButton("保存设置")
        self.save_button.clicked.connect(self.save_config_from_ui)
        button_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        main_layout.addLayout(button_layout)

    def load_config_to_ui(self):
        try:
            self.config_parser.read(self.config_path, encoding='utf-8')
            logging.info(f"Config file {self.config_path} loaded for settings UI.")

            for (section, key), control in self.controls.items():
                if self.config_parser.has_option(section, key):
                    value = self.config_parser.get(section, key)
                    if isinstance(control, QLineEdit):
                        control.setText(value)
                    elif isinstance(control, QComboBox):
                        index = control.findText(value, Qt.MatchFlag.MatchFixedString)
                        if index >= 0:
                            control.setCurrentIndex(index)
                        else:
                            # Add item if not found and it's a free-form combobox, or log warning
                            logging.warning(f"Value '{value}' for {section}/{key} not in QComboBox items. Adding it or select default.")
                            # control.addItem(value) # If you want to add it
                            # control.setCurrentText(value) # If editable
                else:
                    logging.warning(f"Option {section}/{key} not found in config file. UI control will be empty or default.")
        
        except FileNotFoundError:
            logging.error(f"Config file {self.config_path} not found for settings UI.")
            QMessageBox.warning(self, "错误", f"配置文件 {self.config_path} 未找到。")
            # self.save_button.setEnabled(False) # Or allow creating a new one
        except Exception as e:
            logging.error(f"Error loading config file {self.config_path} into settings UI: {e}")
            QMessageBox.critical(self, "加载错误", f"加载配置文件时出错: {e}")
            # self.save_button.setEnabled(False)

    def save_config_from_ui(self):
        try:
            # Update config_parser from UI controls
            for (section, key), control in self.controls.items():
                if not self.config_parser.has_section(section):
                    self.config_parser.add_section(section)
                
                value = ""
                if isinstance(control, QLineEdit):
                    value = control.text()
                elif isinstance(control, QComboBox):
                    value = control.currentText()
                
                self.config_parser.set(section, key, value)

            with open(self.config_path, 'w', encoding='utf-8') as f:
                self.config_parser.write(f)
            
            logging.info(f"Config file {self.config_path} saved from settings UI.")
            QMessageBox.information(self, "设置已保存", f"配置文件 {self.config_path} 已更新。\n某些更改可能需要重启应用才能生效。")
            
            global CONFIG
            CONFIG = load_config() # Reload global CONFIG
            # Consider more granular updates or signaling the main app
            # initialize_tts(CONFIG) # Example if TTS settings changed
            # if self.parent() and hasattr(self.parent(), 'assistant_thread') and self.parent().assistant_thread:
            #    self.parent().assistant_thread.reload_config(CONFIG) 

            self.accept() # Close dialog
        except Exception as e:
            logging.error(f"Error saving config file {self.config_path} from settings UI: {e}")
            QMessageBox.critical(self, "保存失败", f"保存配置文件时发生错误: {e}")

if __name__ == "__main__":
    # Ensure the icon directory exists for the default icon path
    if not os.path.exists("icon"):
        try:
            os.makedirs("icon")
            logging.info("Created 'icon' directory.")
        except OSError as e:
            logging.error(f"Could not create 'icon' directory: {e}")
    
    # Check if example config needs to be copied
    config_path = get_config_path()
    if not os.path.exists(config_path):
        example_config_path = get_example_config_path()
        try:
            import shutil
            shutil.copy(example_config_path, config_path)
            logging.info(f"'{example_config_path}' has been copied to '{config_path}'. Please configure it.")
            # Potentially show a message in GUI or console to configure and restart
        except Exception as e:
            logging.error(f"Could not copy example config: {e}")

    main()