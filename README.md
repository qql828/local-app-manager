# 本地应用管理助手

本项目是一个通过自然语言指令管理本地应用程序的智能助手。它使用了Google Agent Development Kit (ADK)框架和DeepSeek API来处理自然语言指令，并整合了本地应用管理功能。

## 功能特点

- **应用程序管理**：打开、关闭和卸载应用程序
- **设备控制**：调整系统音量和屏幕亮度
- **文件操作**：创建文件夹、删除文件、列出目录等
- **智能交互**：支持自然语言指令，融合DeepSeek和Gemini AI模型

## 安装部署

### 前置条件

1. Python 3.8+ 环境
2. Google API 密钥（用于Gemini API）
3. DeepSeek API 密钥（可选，用于增强命令解析）
4. 操作系统支持：macOS、Windows（部分功能）、Linux（部分功能）

### 安装步骤

1. **克隆仓库**：
```bash
git clone https://github.com/qql828/local-app-manager.git
cd local-app-manager
```

2. **安装依赖**：
```bash
pip install -r requirements.txt
```

3. **配置环境变量**：
   - 复制示例配置文件: `cp .env.example .env`
   - 编辑.env文件，填入必要的API密钥和配置

```
# Google API配置（Web界面必填）
GOOGLE_API_KEY=你的Google API密钥

# DeepSeek API配置（可选，增强命令解析）
DEEPSEEK_API_KEY=你的DeepSeek API密钥
DEEPSEEK_API_BASE=https://api.deepseek.com/v1

# 应用设置
DEBUG=False
CONFIRM_UNINSTALL=True
USE_DEEPSEEK=True  # 是否使用DeepSeek进行命令解析
```

### 部署方式

#### 1. 命令行模式部署

最简单的部署方式，直接运行Python脚本：

```bash
# 交互式命令行模式
python app.py

# 或使用简化版应用
python simple_app.py

# 执行单次命令
python app.py "打开Chrome"
```

#### 2. Web界面模式部署（基于ADK）

需要Google API密钥，提供更友好的Web交互界面：

```bash
# 启动Web服务
python adk_app.py web
```

然后在浏览器中访问: http://localhost:8000

#### 3. 系统服务部署（长期运行）

创建系统服务以便应用在后台长期运行：

**Linux/macOS (systemd)**:
```bash
# 创建服务文件
sudo nano /etc/systemd/system/app-manager.service

# 服务文件内容
[Unit]
Description=Local Application Manager Assistant
After=network.target

[Service]
User=your_username
WorkingDirectory=/path/to/app
ExecStart=/usr/bin/python3 /path/to/app/app.py
Restart=on-failure

[Install]
WantedBy=multi-user.target

# 启动服务
sudo systemctl enable app-manager.service
sudo systemctl start app-manager.service
```

**macOS (launchd)**:
```xml
<!-- 创建文件：~/Library/LaunchAgents/com.app.manager.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.app.manager</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/path/to/app/adk_app.py</string>
        <string>web</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>WorkingDirectory</key>
    <string>/path/to/app</string>
</dict>
</plist>

<!-- 加载服务 -->
launchctl load ~/Library/LaunchAgents/com.app.manager.plist
```

## 使用方法

### 命令行模式

```bash
# 直接进入交互式命令行模式
python app.py

# 基于ADK的命令行模式
python adk_app.py cli

# 执行单次命令
python app.py "打开微信"
```

### Web界面模式

```bash
# 启动Web界面
python adk_app.py web
```

然后在浏览器中访问 http://localhost:8000

## 示例命令

- "打开微信"
- "关闭Chrome浏览器"
- "卸载QQ"
- "音量调到50%"
- "增加音量"
- "降低屏幕亮度"
- "在下载目录创建test文件夹"
- "删除下载目录中的test.txt文件"
- "列出桌面上的文件夹"

## 项目结构与文件功能

### 核心入口文件

| 文件名 | 说明 |
|--------|------|
| `app.py` | 主应用入口，包含命令处理和交互逻辑 |
| `adk_app.py` | 基于Google ADK框架的应用入口，支持Web界面和CLI |
| `simple_app.py` | 简化版应用实现 |
| `agent.py` | 智能代理主定义，处理高级语言理解和命令执行 |

### utils/ 工具类

| 文件名 | 说明 |
|--------|------|
| `nlp_processor.py` | 自然语言处理核心，支持DeepSeek API和本地规则解析 |
| `system_utils.py` | 系统操作工具类，处理路径、目录等系统级操作 |
| `app_finder.py` | 应用查找工具，负责在系统中定位应用 |
| `device_utils.py` | 设备控制统一接口，管理设备的基本操作 |
| `file_utils.py` | 文件操作工具，提供安全的文件管理功能 |
| `mac_utils.py` | macOS平台特定操作实现 |
| `platform_utils.py` | 跨平台操作适配器，统一不同操作系统的接口 |
| `brightness_utils.py` | 屏幕亮度控制工具 |
| `volume_utils.py` | 系统音量控制工具 |

### commands/ 命令实现

| 文件名 | 说明 |
|--------|------|
| `file_operations.py` | 文件操作命令实现（创建、删除、列出等） |
| `open_app.py` | 打开应用命令实现 |
| `close_app.py` | 关闭应用命令实现 |
| `list_installed.py` | 列出已安装应用命令实现 |
| `list_running.py` | 列出正在运行应用命令实现 |
| `uninstall_app.py` | 卸载应用命令实现 |
| `brightness_control.py` | 亮度控制命令实现 |
| `volume_control.py` | 音量控制命令实现 |
| `weather_query.py` | 天气查询功能实现 |

### agents/ ADK代理实现

| 文件名 | 说明 |
|--------|------|
| `agent.py` | ADK代理基础定义 |
| `local_app_manager/agent.py` | 本地应用管理ADK代理实现 |

### 配置和辅助文件

| 文件名 | 说明 |
|--------|------|
| `.env` | 环境变量配置文件（API密钥、调试设置等） |
| `.env.example` | 环境变量示例配置 |
| `requirements.txt` | Python依赖包列表 |
| `setup.py` | 项目安装配置 |
| `cleanup.py` | 清理工具，用于清理临时文件 |

## 工作原理

本系统结合了两种AI模型以提供最佳体验：

1. **DeepSeek API**：用于深度解析自然语言命令，将其转化为结构化的命令和参数
2. **Google Gemini API**：在ADK框架中用于提供更全面的语言理解和响应生成

处理流程：
1. 用户输入自然语言命令
2. 命令被发送到NLP处理器
3. NLP处理器首先尝试使用DeepSeek API解析命令
4. 如果DeepSeek解析成功，使用解析结果；否则回退到本地规则解析
5. 根据解析结果调用相应的命令处理模块
6. 执行命令并返回结果给用户

## 系统要求

- **操作系统**：
  - 完全支持：macOS
  - 部分功能支持：Windows、Linux
- **Python**：3.8+
- **内存**：至少2GB RAM
- **存储**：至少50MB可用空间

## 注意事项

- 卸载操作默认需要二次确认
- 权限操作（如卸载应用）可能需要系统权限
- 文件操作仅限于用户目录内，以保证安全性
- DeepSeek API和Google API密钥可能需要额外费用

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| 无法解析命令 | 检查DeepSeek API配置，或尝试更明确的命令表述 |
| 应用无法打开/关闭 | 确认应用名称正确，可能需要管理员权限 |
| Web界面无法加载 | 确认Google API密钥正确配置 |
| 文件操作失败 | 检查路径权限，确保操作在用户目录内 |

## 联系与支持

如有问题或需要帮助，请提交Issue或联系项目维护者。

## 贡献指南

欢迎贡献代码、提出问题或改进建议！贡献步骤：

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的改动 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

请确保你的代码遵循以下原则：
- 代码格式化符合PEP 8
- 添加必要的测试
- 更新文档以反映新功能

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解更多详情。