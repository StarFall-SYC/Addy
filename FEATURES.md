# Addy 语音助手功能列表

本文档列出了 Addy 语音助手当前支持的主要功能和语音命令示例。随着项目的迭代，此列表会持续更新。

## 核心功能

*   **唤醒助手**: 
    *   默认唤醒词: "Addy，你好"
    *   支持自定义唤醒词 (通过配置)
*   **语音交互**: 支持自然语言指令输入。
*   **任务反馈**: 通过语音或弹窗反馈任务执行结果。

## 内置工具与功能

### 1. 文件工具 (`FileTool`)

*   **创建文件/文件夹**:
    *   "创建文件 [文件名]"
    *   "创建文件夹 [文件夹名]"
*   **删除文件/文件夹**:
    *   "删除文件 [文件名]"
    *   "删除文件夹 [文件夹名]"
*   **复制文件/文件夹**:
    *   "复制文件 [源文件] 到 [目标文件/文件夹]"
    *   "复制文件夹 [源文件夹] 到 [目标文件夹]"
*   **移动文件/文件夹**:
    *   "移动文件 [源文件] 到 [目标文件/文件夹]"
    *   "移动文件夹 [源文件夹] 到 [目标文件夹]"
*   **搜索文件**:
    *   "搜索文件 [关键词或通配符]"
    *   "在 [目录] 中搜索文件 [关键词]"
*   **读取文件内容**:
    *   "读取文件 [文件名]"
*   **写入文件内容**:
    *   "向文件 [文件名] 写入 [内容]"
*   **列出目录内容**:
    *   "列出目录 [目录名] 的文件"
    *   "显示 [目录名] 里面的东西"
*   **获取文件信息**:
    *   "获取文件 [文件名] 的信息"

### 2. 系统工具 (`SystemTool`)

*   **获取系统信息**:
    *   "获取系统信息"
    *   "查看CPU使用率"
    *   "显示内存占用率"
    *   "磁盘空间还有多少"
*   **进程管理**:
    *   "列出所有进程"
    *   "结束进程 [进程名或PID]"
    *   "关闭 [应用名称]"
*   **音量控制**:
    *   "设置音量到 [百分比]"
    *   "调大音量"
    *   "调小音量"
    *   "静音"
    *   "取消静音"
    *   "获取当前音量"
*   **系统操作**:
    *   "锁定电脑"
    *   "电脑休眠"
    *   "关机"
    *   "重启电脑"
*   **获取网络信息**:
    *   "获取网络信息"
    *   "我的IP地址是什么"
*   **获取电池信息** (笔记本):
    *   "查看电池电量"

### 3. 网络工具 (`WebTool`)

*   **网页搜索** (集成，通常通过NLP直接解析，也可显式调用):
    *   "搜索 [关键词]"
    *   "百度一下 [关键词]"
    *   "谷歌搜索 [关键词]"
*   **文件下载**:
    *   "下载文件 [URL]"
    *   "从 [URL] 下载文件到 [本地路径]"
*   **网站状态检查**:
    *   "检查网站 [URL] 能否访问"
*   **文本翻译**:
    *   "翻译 [文本] 到 [目标语言]"
    *   "[文本] 翻译成英文是什么"
*   **IP信息查询**:
    *   "查询IP地址 [IP地址] 的信息"
*   **Ping 主机**:
    *   "Ping [主机名或IP地址]"
*   **URL缩短**:
    *   "缩短网址 [长URL]"

### 4. 计算器工具 (`CalculatorTool`)

*   **基础数学计算**:
    *   "计算 [数学表达式]" (例如: "计算 2 加 3 乘以 4")
*   **科学计算**:
    *   "计算 sin(30)"
    *   "计算 log10(100)"
*   **单位转换** (长度、重量等):
    *   "转换 [数值] [源单位] 到 [目标单位]" (例如: "转换 100 米到公里")
*   **温度转换**:
    *   "转换 [数值] 摄氏度到华氏度"
*   **百分比计算**:
    *   "计算 [百分比] 的 [数值]" (例如: "计算 15% 的 200")
*   **随机数生成**:
    *   "生成一个随机数"
    *   "生成一个 [最小值] 到 [最大值] 之间的随机数"

### 5. 天气工具 (`WeatherTool`)

*   **当前天气查询**:
    *   "[城市名] 今天天气怎么样"
    *   "查询 [城市名] 的天气"
*   **天气预报**:
    *   "[城市名] 未来几天的天气预报"
    *   "明天 [城市名] 会下雨吗"
*   **天气警报**:
    *   "[城市名] 有天气预报吗"
*   **空气质量**:
    *   "[城市名] 的空气质量如何"
*   **紫外线指数**:
    *   "查询 [城市名] 的紫外线指数"
*   **日出日落时间**:
    *   "[城市名] 今天什么时候日出日落"
*   **城市天气比较**:
    *   "比较 [城市A] 和 [城市B] 的天气"
*   **历史天气查询** (部分功能可能需要付费API):
    *   "查询 [城市名] 昨天天气"

**注意**: 天气工具需要配置有效的 OpenWeatherMap API 密钥。

### 6. 邮件工具 (`EmailTool`)

*   **发送邮件**:
    *   "发送邮件给 [收件人邮箱] 主题 [主题内容] 内容 [邮件正文]"
    *   "给 [联系人名] 发邮件说 [内容]"
*   **读取邮件**:
    *   "查看最新邮件"
    *   "我有未读邮件吗"
    *   "读一下来自 [发件人] 的邮件"
*   **搜索邮件**:
    *   "搜索主题包含 [关键词] 的邮件"
*   **获取邮件数量**:
    *   "我有几封未读邮件"
*   **创建邮件草稿**:
    *   "创建一封邮件草稿 主题 [主题] 内容 [内容]"

**注意**: 邮件工具需要配置邮箱账户信息 (IMAP/SMTP 服务器、用户名、密码/应用专用密码)。

### 7. 日历工具 (`CalendarTool`)

*   **创建日程事件**:
    *   "创建日程 [事件名称] 在 [日期] [时间]"
    *   "明天下午3点提醒我 [事件]"
*   **查看日程**:
    *   "查看今天的日程"
    *   "我明天有什么安排"
    *   "查询 [日期] 的日程"
*   **设置提醒** (通常与创建事件结合):
    *   "设置提醒 [事件] 在 [日期] [时间]"
*   **日期查询**:
    *   "今天是几号"
    *   "明天是星期几"
*   **计算日期差**:
    *   "[日期A] 和 [日期B] 之间差几天"
*   **查找特定星期几**:
    *   "下周三是几号"

**注意**: 日历工具可能依赖本地日历文件或配置与在线日历服务同步。

## 其他通用指令

*   **打开应用**:
    *   "打开 [应用名称]" (例如: "打开记事本", "启动微信")
*   **设置提醒/闹钟** (部分可能通过日历工具实现):
    *   "提醒我 [时间] 做 [事情]"
    *   "设置一个 [时间] 的闹钟"
*   **播放音乐** (可能需要配置音乐源或本地音乐库):
    *   "播放音乐"
    *   "播放 [歌曲名]"
*   **获取当前时间/日期**:
    *   "现在几点了"
    *   "今天是什么日期"

## 进阶功能 (部分正在开发或规划中)

*   多轮对话与上下文理解
*   用户自定义指令扩展
*   更深入的第三方服务集成 (如智能家居控制)

---

本功能列表会随着 Addy 的成长而不断丰富。如果您有任何功能建议，欢迎通过项目仓库提出 Issue 或参与贡献！