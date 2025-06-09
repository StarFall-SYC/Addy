# Addy 语音助手配置指南

本文档将指导您完成 Addy 语音助手的配置过程，确保您的助手能够顺利运行。

## 目录

1.  [初次运行与依赖安装](#1-初次运行与依赖安装)
2.  [核心配置文件：`config.ini`](#2-核心配置文件configini)
3.  [Porcupine 唤醒词引擎配置](#3-porcupine唤醒词引擎配置)
    *   [获取 Picovoice Access Key](#获取-picovoice-access-key)
    *   [准备唤醒词文件 (.ppn)](#准备唤醒词文件-ppn)
    *   [准备模型文件 (.pv)](#准备模型文件-pv)
    *   [配置 `config.ini` 中的 `[Porcupine]` 部分](#配置-configini-中的-porcupine-部分)
4.  [Azure Speech 服务配置 (可选)](#4-azure-speech-服务配置-可选)
5.  [文本转语音 (TTS) 引擎配置](#5-文本转语音-tts-引擎配置)
6.  [自然语言处理 (NLP) 及大型语言模型 (LLM) 配置 (可选)](#6-自然语言处理-nlp-及大型语言模型-llm-配置-可选)
7.  [其他配置项](#7-其他配置项)
8.  [故障排除](#8-故障排除)

## 1. 初次运行与依赖安装

在开始配置之前，请确保您已经克隆了 Addy 语音助手的代码仓库，并且您的 Python 环境已经就绪。

打开终端或命令行工具，导航到项目根目录，然后运行以下命令安装所有必需的依赖项：

```bash
pip install -r requirements.txt
```

这将安装包括 `pvporcupine`（用于唤醒词检测）、`PyQt6`（用于图形用户界面）等在内的所有库。

## 2. 核心配置文件：`config.ini`

Addy 语音助手的所有配置都集中在 `config` 文件夹中的 `config.ini` 文件里。如果您是首次配置，请复制 `config/config.ini.example` 文件并将其重命名为 `config.ini`。

```bash
# 在项目根目录下执行
cp config/config.ini.example config/config.ini
```

**重要提示**: `config.ini.example` 文件中包含了所有可用的配置项及其详细说明。请根据您的需求修改 `config.ini` 中的相应值。

## 3. 配置项说明

以下是 `config.ini.example` 中主要配置项的简要说明。更详细的注释请直接查阅 `config/config.ini.example` 文件。

### 通用设置 (`[General]`)

*   `language`: 助手使用的语言。
*   `wake_word_engine`: 唤醒词引擎，例如 `porcupine`。
*   `wake_words`: 唤醒词，多个唤醒词用逗号分隔。

### Porcupine 唤醒词引擎 (`[Porcupine]`)

*   `access_key`: Picovoice Access Key。请访问 <https://console.picovoice.ai/> 获取。
*   `model_path`: Porcupine 模型文件路径 (.pv)。对于中文等非英文唤醒词，需要下载对应的模型文件。
*   `keyword_paths`: 唤醒词文件路径 (.ppn)。可以包含多个路径，用逗号分隔。
*   `sensitivities`: 每个关键词的灵敏度 (0.0 到 1.0)。

### Azure Speech 服务 (`[AzureSpeech]`)

*   `speech_key`: Azure 语音服务的 API 密钥。
*   `service_region`: Azure 语音服务的区域。

### 文本转语音 (TTS) 引擎 (`[TTS]`)

*   `tts_engine`: TTS 引擎选择，例如 `pyttsx3` 或 `azure`。
*   `pyttsx3_voice_id`: (仅当 `tts_engine = pyttsx3` 时相关) pyttsx3 使用的语音 ID。

### 自然语言处理 (NLP) 及大型语言模型 (LLM) (`[NLP]`)

*   `engine`: NLP 引擎选择，例如 `rule_based` 或 `llm`。
*   `llm_service`: (仅当 `engine = llm` 时相关) 使用的 LLM 服务，例如 `openai`, `claude`, `tongyi`, `gemini`。

### LLM 服务配置 (例如 `[LLM_OpenAI]`, `[LLM_Claude]`, `[LLM_Tongyi]`, `[LLM_Gemini]`)

*   `api_key`: 对应 LLM 服务的 API 密钥。
*   `model`: 使用的 LLM 模型名称。
*   `base_url`: (可选) 自定义 API 基础 URL。

### 工具配置 (`[Tools]` 及各工具专用节)

*   `enabled_tools`: 启用的工具列表，用逗号分隔。
*   各工具（如 `[FileTool]`, `[SystemTool]`, `[WebTool]`, `[CalculatorTool]`, `[WeatherTool]`, `[EmailTool]`, `[CalendarTool]`）有各自的专用配置项，例如 API 密钥、默认城市、邮箱账户等。请查阅 `config/config.ini.example` 中的详细注释。

### 安全配置 (`[Security]`)

*   `allowed_directories`: 允许文件工具操作的目录。
*   `allowed_extensions`: 允许文件工具操作的文件扩展名。
*   `system_commands_whitelist`: 允许系统工具执行的命令白名单。

### 其他配置 (`[Miscellaneous]`)

*   `command_listen_timeout`: 命令监听超时时间。
*   `command_phrase_limit`: 命令短语限制。
*   `debug_mode`: 是否启用调试模式。

## 4. 故障排除

*   **配置错误**: 如果助手无法正常启动或功能异常，请首先检查 `config.ini` 文件中的配置项是否正确，特别是 API 密钥和文件路径。
*   **依赖缺失**: 确保 `requirements.txt` 中的所有依赖都已正确安装。
*   **日志文件**: 检查 `addy_assistant.log` 文件（在 `[Paths]` 中配置）以获取详细的错误信息。

如果您遇到问题，请参考项目的 GitHub 仓库或社区寻求帮助。
# api_base = https://api.openai.com/v1
```

请确保为您选择的 LLM 服务提供有效的 API 密钥。

## 7. 其他配置项

`config.ini` 中还有其他一些配置项，您可以根据需要进行调整：

*   `[General]`
    *   `language`: ASR 和 TTS 的默认语言 (例如 `zh-CN`, `en-US`)。
*   `[Paths]`
    *   `log_file`: 日志文件的名称。
    *   `screenshots_dir`: 截图文件保存目录。
*   `[ASR]`
    *   `command_listen_timeout`: 唤醒后聆听指令的超时时间。
    *   `command_phrase_time_limit`: 单个指令语音片段的最大时长。
    *   连续聆听相关的参数。
*   `[Miscellaneous]`
    *   `debug_mode`: 是否启用调试日志 (True/False)。

## 8. 故障排除

*   **`pvporcupine library not found` 或 `Error initializing Porcupine`**: 
    *   确保已运行 `pip install -r requirements.txt` 并且 `pvporcupine` 已成功安装。
    *   检查 `[Porcupine]` 部分的 `access_key`, `keyword_paths`, `model_path` 是否正确无误，文件是否存在于指定路径。
    *   确保 `.ppn` 文件与您在 `wake_words` 中设置的唤醒词匹配，并且是为您的操作系统 (Windows) 和语言训练的。
    *   确保 `.pv` 模型文件与您选择的语言匹配。
*   **任务计划程序相关错误 (COM 错误)**: 我们在之前的调试中已经通过在 `main.py` 的相关函数中添加 `pythoncom.CoInitialize()` 和 `pythoncom.CoUninitialize()` 以及使用 `win32com.client.gencache.EnsureDispatch` 来解决。如果仍然出现，请检查这些调用是否仍然存在且位置正确。
*   **`QObject::setParent: Cannot set parent, new parent is in a different thread`**: 我们已通过在 `SettingsDialog` 的 `__init__` 中设置父对象为 `None` 并添加 `self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)` 来尝试解决。如果问题复现，可能需要进一步检查线程交互。
*   **唤醒词不灵敏或误唤醒**: 尝试调整 `[Porcupine]` 部分的 `sensitivities` 值。
*   **语音识别或合成问题**: 
    *   如果使用 Azure，检查 `speech_key` 和 `service_region` 是否正确，以及网络连接是否正常。
    *   如果使用 `pyttsx3`，尝试选择不同的 `pyttsx3_voice_id`。

完成以上配置后，您应该可以成功运行 Addy 语音助手了。如果在配置过程中遇到任何问题，请回顾本文档或查看程序运行时输出的错误信息以获取线索。