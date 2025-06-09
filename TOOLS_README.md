# Addy 语音助手工具系统

## 概述

Addy 语音助手现在支持强大的工具系统，可以处理更多类型的任务。工具系统采用模块化设计，易于扩展和维护。

## 支持的工具类型

### 1. 文件工具 (FileTool)

**功能：**
- 创建、删除、复制、移动文件和文件夹
- 搜索文件
- 读取和写入文件内容
- 列出目录内容
- 获取文件信息

**语音命令示例：**
- "创建文件 test.txt"
- "删除文件 old_file.txt"
- "复制文件 source.txt 到 backup.txt"
- "搜索文件 *.py"
- "列出目录 Documents 的文件"
- "读取文件 readme.txt"

### 2. 系统工具 (SystemTool)

**功能：**
- 获取系统信息（CPU、内存、磁盘使用率）
- 进程管理（列出、终止进程）
- 服务管理
- 网络和电池信息
- 音量控制
- 系统操作（锁定、关机、重启）

**语音命令示例：**
- "获取系统信息"
- "查看CPU使用率"
- "显示内存占用率"
- "列出所有进程"
- "结束进程 notepad"
- "获取网络信息"
- "设置音量到 50"
- "获取当前音量"

### 3. 网络工具 (WebTool)

**功能：**
- HTTP GET/POST 请求
- 文件下载
- 网站状态检查
- API 调用
- IP 信息查询
- Ping 主机
- 端口检查
- 文本翻译
- URL 缩短

**语音命令示例：**
- "下载文件 https://example.com/file.zip"
- "检查网站 https://www.google.com"
- "翻译 Hello World 到中文"

### 4. 计算器工具 (CalculatorTool)

**功能：**
- 基础数学计算
- 科学计算（三角函数、对数等）
- 单位转换
- 温度转换
- 货币转换
- 百分比计算
- 面积和体积计算
- 随机数生成
- 统计计算

**语音命令示例：**
- "计算 2 + 3 * 4"
- "转换 100 米到公里"
- "转换温度 25 摄氏度到华氏度"
- "计算 15% 的 200"

### 5. 天气工具 (WeatherTool)

**功能：**
- 当前天气查询
- 天气预报
- 天气警报
- 空气质量
- 紫外线指数
- 日出日落时间
- 城市天气比较
- 历史天气查询

**语音命令示例：**
- "查看北京的天气"
- "显示天气预报"
- "获取空气质量"

**注意：** 需要配置 OpenWeatherMap API 密钥

### 6. 邮件工具 (EmailTool)

**功能：**
- 发送邮件（支持附件）
- 读取邮件（最新、未读）
- 搜索邮件
- 获取邮件数量
- 创建邮件草稿

**语音命令示例：**
- "发送邮件给 user@example.com 主题 测试 内容 这是一封测试邮件"
- "查看最新邮件"
- "搜索邮件 重要"

**注意：** 需要配置邮箱账户和密码

### 7. 日历工具 (CalendarTool)

**功能：**
- 创建日程事件
- 查看日程
- 设置提醒
- 日期查询
- 计算日期差
- 查找特定星期几
- 节假日信息
- 重复事件

**语音命令示例：**
- "创建事件 会议 在 2024-01-15 14:00"
- "查看今天的日程"
- "设置提醒 买菜 在 2024-01-15 18:00"
- "今天是星期几"

## 配置说明

所有工具的配置都在 `config/config.ini` 文件中进行。您可以参考 `config/config.ini.example` 文件了解所有可用的配置项及其详细说明。

**启用工具：**
在 `config.ini` 的 `[Tools]` 部分，通过 `enabled_tools` 配置项列出您希望启用的工具，例如：
```ini
[Tools]
enabled_tools = file_tool,system_tool,web_tool,calculator_tool,weather_tool,email_tool,calendar_tool
# ... 其他工具通用配置 ...
```

**工具特定配置：**
每个工具（如 `[WeatherTool]`, `[EmailTool]` 等）都有其专属的配置节，用于设置 API 密钥、默认参数等。请务必查阅 `config/config.ini.example` 并根据您的实际情况修改 `config.ini`。

## 使用方法

### 1. 启动助手

```python
from addy_core.task_executor import TaskExecutor
from addy_core.nlp_module import NLPModule
import configparser

# 加载配置
config = configparser.ConfigParser()
config.read('config.ini')

# 初始化NLP模块
nlp = NLPModule(nlp_engine='rule_based')

# 初始化任务执行器
executor = TaskExecutor(config=config, tts_engine_speak_func=your_speak_function)

# 处理用户输入
user_input = "计算 2 + 3"
intent_data = nlp.parse_intent(user_input)
result = executor.execute(intent_data)
```

### 2. 运行测试

```bash
python test_tools.py
```

这将运行所有工具的测试，验证系统是否正常工作。

## 扩展工具

### 1. 创建新工具

继承 `BaseTool` 类：

```python
from addy_core.tools.base_tool import BaseTool

class MyTool(BaseTool):
    def __init__(self, config=None, speak_func=None):
        super().__init__(config, speak_func)
        self.name = "my_tool"
        self.description = "我的自定义工具"
        self.supported_intents = ['my_intent']
    
    def execute(self, intent, entities, original_text):
        # 实现工具逻辑
        return "success"
```

### 2. 注册新工具

在 `ToolManager` 中注册：

```python
tool_manager.register_tool(MyTool(config, speak_func))
```

### 3. 添加NLP模式

在 `NLPModule` 的 `intent_patterns` 中添加新的意图模式。

## 安全注意事项

1. **文件操作**：限制访问敏感目录
2. **系统操作**：谨慎使用关机、重启等操作
3. **网络请求**：验证URL和下载内容
4. **进程管理**：避免终止系统关键进程
5. **API密钥**：妥善保管各种API密钥

## 故障排除

### 常见问题

1. **工具未加载**：检查配置文件中的 `enabled_tools` 设置
2. **API调用失败**：验证API密钥和网络连接
3. **文件操作失败**：检查文件路径和权限
4. **意图识别错误**：检查NLP模式匹配

### 日志查看

工具系统会生成详细的日志，可以通过以下方式查看：

```python
import logging
logging.basicConfig(level=logging.INFO)
```

## 更新日志

### v1.0.0
- 初始版本
- 支持7种工具类型
- 模块化设计
- 完整的配置系统
- 测试框架

## 贡献

欢迎贡献新的工具类型和功能改进。请确保：

1. 遵循现有的代码风格
2. 添加适当的测试
3. 更新文档
4. 考虑安全性和错误处理

## 许可证

本项目采用 MIT 许可证。