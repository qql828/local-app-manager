"""
自然语言处理模块，用于解析用户指令。
"""
import os
import re
import json
import logging
import requests
import time
from typing import Dict, List, Tuple, Optional, Any, Union
from dotenv import load_dotenv
from utils.system_utils import SystemUtils

# 加载环境变量
load_dotenv()

# 配置日志
logger = logging.getLogger(__name__)


class NLPProcessor:
    """自然语言处理器，用于解析用户指令"""
    
    # 命令类型
    CMD_OPEN = 'open'
    CMD_CLOSE = 'close'
    CMD_UNINSTALL = 'uninstall'
    CMD_LIST_RUNNING = 'list_running'
    CMD_LIST_INSTALLED = 'list_installed'
    
    # 设备控制命令
    CMD_GET_VOLUME = 'get_volume'
    CMD_SET_VOLUME = 'set_volume'
    CMD_INCREASE_VOLUME = 'increase_volume'
    CMD_DECREASE_VOLUME = 'decrease_volume'
    CMD_MUTE = 'mute'
    CMD_UNMUTE = 'unmute'
    
    # 亮度控制命令
    CMD_GET_BRIGHTNESS = 'get_brightness'
    CMD_SET_BRIGHTNESS = 'set_brightness'
    CMD_INCREASE_BRIGHTNESS = 'increase_brightness'
    CMD_DECREASE_BRIGHTNESS = 'decrease_brightness'
    
    # 文件操作命令
    CMD_LIST_SUBDIRECTORIES = 'list_subdirectories'
    CMD_CREATE_DIRECTORY = 'create_directory'
    CMD_DELETE_FILE = 'delete_file'
    CMD_DELETE_DIRECTORY = 'delete_directory'
    
    # 命令关键词
    COMMANDS = {
        CMD_OPEN: ['打开', '启动', '运行', '开启', 'open', 'run', 'start', 'launch'],
        CMD_CLOSE: ['关闭', '退出', '停止', '结束', 'close', 'exit', 'stop', 'quit', 'terminate'],
        CMD_UNINSTALL: ['卸载', '删除', '移除', 'uninstall', 'remove', 'delete'],
        CMD_LIST_RUNNING: ['查看正在运行', '显示正在运行', '列出正在运行', '当前运行', '正在运行的应用', '运行中的应用', 'list running', 'show running'],
        CMD_LIST_INSTALLED: ['查看已安装', '显示已安装', '列出已安装', '已安装应用', '安装了哪些', '有哪些应用', 'list installed', 'show installed'],
        
        # 音量控制关键词
        CMD_GET_VOLUME: ['当前音量', '查看音量', '显示音量', '获取音量', '音量是多少', '声音大小', 'get volume', 'show volume', 'current volume'],
        CMD_SET_VOLUME: ['设置音量', '调整音量', '音量调到', '音量设为', '把音量设置为', '声音设为', 'set volume', 'adjust volume', 'volume to'],
        CMD_INCREASE_VOLUME: ['增大音量', '提高音量', '调高音量', '音量增加', '音量调高', '声音调大', '声音增大', '音量大点', '音量开大点', '声音大一点', 'increase volume', 'volume up', 'louder'],
        CMD_DECREASE_VOLUME: ['减小音量', '降低音量', '调低音量', '音量减少', '音量调低', '声音调小', '声音减小', '音量小点', '音量开小点', '声音小一点', 'decrease volume', 'volume down', 'quieter'],
        CMD_MUTE: ['静音', '关闭声音', '关掉声音', '没有声音', '音量关闭', '音量静音', 'mute', 'silence'],
        
        # 亮度控制关键词
        CMD_GET_BRIGHTNESS: ['当前亮度', '查看亮度', '显示亮度', '获取亮度', '亮度是多少', '屏幕亮度', 'get brightness', 'show brightness', 'current brightness'],
        CMD_SET_BRIGHTNESS: ['设置亮度', '调整亮度', '亮度调到', '亮度设为', '把亮度设置为', '屏幕亮度设为', 'set brightness', 'adjust brightness', 'brightness to'],
        CMD_INCREASE_BRIGHTNESS: ['增大亮度', '提高亮度', '调高亮度', '亮度增加', '亮度调高', '屏幕调亮', '屏幕亮一点', '亮度大点', '亮度开大点', '亮一点', 'increase brightness', 'brightness up', 'brighter'],
        CMD_DECREASE_BRIGHTNESS: ['减小亮度', '降低亮度', '调低亮度', '亮度减少', '亮度调低', '屏幕调暗', '屏幕暗一点', '亮度小点', '亮度开小点', '暗一点', 'decrease brightness', 'brightness down', 'dimmer'],
        
        # 文件操作关键词
        CMD_LIST_SUBDIRECTORIES: [
            '列出子文件夹', '查看子文件夹', '显示子文件夹', 
            '列出目录下的文件夹', '查看目录下的文件夹', '显示目录下的文件夹',
            '列出文件夹', '查看文件夹', '显示文件夹',
            '目录中的子文件夹', '子文件夹列表', '文件夹列表', 
            '列出下载文件夹', '列出桌面文件夹', '列出文档文件夹',
            '列出目录中的文件夹', '查看目录中的文件夹', '显示目录中的文件夹',
            '查看目录中的子目录', '列出目录中的子目录', '显示目录中的子目录',
            'list subdirectories', 'list folders', 'show folders', 'list directories',
            'show directories', 'display folders', 'display directories'
        ],
        CMD_CREATE_DIRECTORY: [
            '创建文件夹', '新建文件夹', '建立文件夹', '建文件夹', '创建目录', '新建目录',
            '创建一个文件夹', '新建一个文件夹', '建一个文件夹', '创建一个目录', '新建一个目录',
            '在目录中创建文件夹', '在目录下创建文件夹', '在目录里创建文件夹',
            '在目录中新建文件夹', '在目录下新建文件夹', '在目录里新建文件夹',
            'create folder', 'create directory', 'make directory', 'make folder',
            'new folder', 'new directory'
        ],
        CMD_DELETE_FILE: [
            '删除文件', '移除文件', '清除文件', '去掉文件', '除去文件',
            '删掉文件', '删除一个文件', '移除一个文件', '清除一个文件',
            '在目录中删除文件', '在目录下删除文件', '在目录里删除文件',
            'delete file', 'remove file', 'erase file', 'clear file'
        ],
        CMD_DELETE_DIRECTORY: [
            '删除文件夹', '删除目录', '移除文件夹', '移除目录', '清除文件夹', '清除目录',
            '删掉文件夹', '删掉目录', '删除一个文件夹', '删除一个目录', '移除一个文件夹',
            '在目录中删除文件夹', '在目录下删除文件夹', '在目录里删除文件夹',
            'delete folder', 'delete directory', 'remove folder', 'remove directory',
            'erase folder', 'erase directory'
        ]
    }
    
    # 相关命令混合模式匹配
    MIXED_COMMANDS = {
        # 增加音量到特定值
        (CMD_INCREASE_VOLUME, CMD_SET_VOLUME): [
            r'(增大|提高|调高|增加|调大|大)(.*?)(音量|声音)(.*?)(到|至|成|为)(\d+)',
            r'(把|将)(.*?)(音量|声音)(.*?)(增大|提高|调高|增加|调大|大)(.*?)(到|至|成|为)(\d+)',
            r'(音量|声音)(.*?)(增大|提高|调高|增加|调大|大)(.*?)(到|至|成|为)(\d+)',
        ],
        # 减小音量到特定值
        (CMD_DECREASE_VOLUME, CMD_SET_VOLUME): [
            r'(减小|降低|调低|减少|调小|小)(.*?)(音量|声音)(.*?)(到|至|成|为)(\d+)',
            r'(把|将)(.*?)(音量|声音)(.*?)(减小|降低|调低|减少|调小|小)(.*?)(到|至|成|为)(\d+)',
            r'(音量|声音)(.*?)(减小|降低|调低|减少|调小|小)(.*?)(到|至|成|为)(\d+)',
        ],
        # 增加亮度到特定值
        (CMD_INCREASE_BRIGHTNESS, CMD_SET_BRIGHTNESS): [
            r'(增大|提高|调高|增加|调大|大)(.*?)(亮度|屏幕)(.*?)(到|至|成|为)(\d+)',
            r'(把|将)(.*?)(亮度|屏幕)(.*?)(增大|提高|调高|增加|调大|大)(.*?)(到|至|成|为)(\d+)',
            r'(亮度|屏幕)(.*?)(增大|提高|调高|增加|调大|大)(.*?)(到|至|成|为)(\d+)',
        ],
        # 减小亮度到特定值
        (CMD_DECREASE_BRIGHTNESS, CMD_SET_BRIGHTNESS): [
            r'(减小|降低|调低|减少|调小|小)(.*?)(亮度|屏幕)(.*?)(到|至|成|为)(\d+)',
            r'(把|将)(.*?)(亮度|屏幕)(.*?)(减小|降低|调低|减少|调小|小)(.*?)(到|至|成|为)(\d+)',
            r'(亮度|屏幕)(.*?)(减小|降低|调低|减少|调小|小)(.*?)(到|至|成|为)(\d+)',
        ]
    }
    
    @staticmethod
    def parse_with_deepseek(text: str) -> Tuple[Optional[str], Optional[Any]]:
        """
        使用DeepSeek大模型解析用户指令
        
        Args:
            text: 用户输入的命令文本
            
        Returns:
            Tuple[Optional[str], Optional[Any]]: 命令类型和参数
        """
        api_key = os.getenv('DEEPSEEK_API_KEY')
        api_base = os.getenv('DEEPSEEK_API_BASE', 'https://api.deepseek.com/v1')
        
        if not api_key:
            logger.warning("未配置DeepSeek API密钥，无法使用DeepSeek解析")
            return None, None
        
        try:
            # 构建提示词 - 减少硬编码指令，使用更灵活的描述
            prompt = f"""请分析以下用户自然语言指令，提取操作类型和参数。

操作类型包括：
1. 应用操作类：
   - open: 打开应用（例如"打开微信"、"启动浏览器"等）
   - close: 关闭应用（例如"关闭微信"、"退出浏览器"等）
   - uninstall: 卸载应用（例如"卸载QQ"、"删除游戏"等）
   - list_running: 列出正在运行的应用（例如"查看正在运行的应用"等）
   - list_installed: 列出已安装的应用（例如"显示已安装的软件"等）

2. 设备控制类：
   - 音量控制：get_volume（获取当前音量）、set_volume（设置音量）、increase_volume（增加音量）、decrease_volume（减小音量）、mute（静音）、unmute（解除静音）
   - 亮度控制：get_brightness（获取当前亮度）、set_brightness（设置亮度）、increase_brightness（增加亮度）、decrease_brightness（减小亮度）

3. 文件操作类：
   - create_directory: 创建文件夹（例如"创建文件夹"、"新建目录"、"在下载目录下创建一个测试文件夹"等）
   - list_subdirectories: 列出子文件夹（例如"列出目录下的文件夹"、"查看下载文件夹中的子目录"等）
   - delete_file: 删除文件（例如"删除文件"、"移除下载目录中的测试.txt文件"等）
   - delete_directory: 删除文件夹（例如"删除文件夹"、"移除下载目录中的测试目录"等）

注意事项：
- 应理解混合指令：比如"把音量调高到80%"同时包含increase_volume和set_volume语义，应判断为set_volume
- 特别关注路径提取：对于文件操作，需要识别目录路径（如"下载目录"、"桌面"、"~/Documents"等）
- 路径和名称分离：在创建文件夹时，需区分目录路径和文件夹名称

对于目录路径解析的特殊说明：
1. 中文目录名称的关键点：
   - 当用户提到"xxx目录"时，必须考虑两种可能的路径：
     a) "xxx目录"整体作为一个目录名
     b) "xxx"作为真实目录名，"目录"仅是一个描述词
   - 必须优先考虑第二种情况，因为通常"下载目录"实际指的是"下载"这个目录

2. 常见的目录表达方式：
   - "下载目录" → 优先理解为"下载"
   - "桌面目录" → 优先理解为"桌面"
   - "文档目录" → 优先理解为"文档"

3. 扩展理解：
   - "下载文件夹" → 与"下载目录"相同，优先理解为"下载"
   - "在下载目录下" → 路径应该理解为"下载"
   - "在下载里面" → 路径应该理解为"下载"

用户指令: {text}

返回格式（JSON）：
{{
  "command_type": "操作类型",
  "parameter": "应用名称、数值或其他参数"
}}

对于文件操作，请使用以下结构：
{{
  "command_type": "create_directory或list_subdirectories或delete_file或delete_directory",
  "parameter": {{
    "path": "最可能的目录路径",
    "path_alternatives": ["可能的替代路径1", "可能的替代路径2", "可能的替代路径3"],  // 提供至少3个替代路径选项
    "name": "文件夹名称或文件名"  // 仅create_directory和delete_file、delete_directory需要
  }}
}}

例如，当用户说"在下载目录下创建test文件夹"时，应返回：
{{
  "command_type": "create_directory",
  "parameter": {{
    "path": "下载",
    "path_alternatives": ["下载目录", "Downloads", "~/Downloads"],
    "name": "test"
  }}
}}

例如，当用户说"删除下载目录中的test.txt文件"时，应返回：
{{
  "command_type": "delete_file",
  "parameter": {{
    "path": "下载",
    "path_alternatives": ["下载目录", "Downloads", "~/Downloads"],
    "name": "test.txt"
  }}
}}

例如，当用户说"删除下载文件夹中的test目录"时，应返回：
{{
  "command_type": "delete_directory",
  "parameter": {{
    "path": "下载",
    "path_alternatives": ["下载文件夹", "Downloads", "~/Downloads"],
    "name": "test"
  }}
}}

当解析路径时，若遇到"xxx目录"或"xxx文件夹"这样的表达，请始终将"xxx"作为第一优先选项放在path字段，而将完整表达"xxx目录"放入path_alternatives。

若无法确定操作类型，command_type返回null。"""
            
            # 调用DeepSeek API
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "max_tokens": 250
            }
            
            response = requests.post(f"{api_base}/chat/completions", 
                                    headers=headers, 
                                    json=payload, 
                                    timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # 尝试从响应中提取JSON
                try:
                    # 提取JSON内容（可能被包含在代码块中）
                    json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
                    if json_match:
                        content = json_match.group(1)
                    elif content.strip().startswith('{') and content.strip().endswith('}'):
                        # 直接是JSON格式
                        content = content.strip()
                    
                    parsed = json.loads(content)
                    cmd_type = parsed.get("command_type")
                    parameter = parsed.get("parameter")
                    
                    # 检查并处理文件操作的特殊格式
                    if cmd_type in ["create_directory", "list_subdirectories", "delete_file", "delete_directory"]:
                        if isinstance(parameter, dict):
                            # 参数已经是字典格式，直接使用
                            logger.info(f"DeepSeek成功解析文件操作命令: {cmd_type}, 参数: {parameter}")
                        elif isinstance(parameter, str) and cmd_type == "list_subdirectories":
                            # 如果参数是字符串，转换为统一的字典格式
                            parameter = {"path": parameter, "path_alternatives": []}
                            logger.info(f"DeepSeek解析出路径字符串，已转换为字典: {parameter}")
                    
                    # 验证命令类型是否在已定义的命令列表中
                    if cmd_type and hasattr(NLPProcessor, f"CMD_{cmd_type.upper()}"):
                        logger.info(f"DeepSeek成功解析命令: {cmd_type}, 参数: {parameter}")
                        return cmd_type, parameter
                    elif cmd_type:
                        logger.warning(f"DeepSeek解析出未知命令类型: {cmd_type}")
                
                except (json.JSONDecodeError, KeyError) as e:
                    logger.error(f"解析DeepSeek响应失败: {str(e)}, 响应内容: {content}")
            else:
                logger.error(f"DeepSeek API调用失败: {response.status_code}, {response.text}")
        
        except Exception as e:
            logger.error(f"调用DeepSeek时出错: {str(e)}")
        
        return None, None
    
    @staticmethod
    def parse_command(text: str) -> Tuple[Optional[str], Optional[Any]]:
        """
        解析用户输入的命令文本，识别命令类型和目标应用程序
        
        Args:
            text: 用户输入的命令文本
            
        Returns:
            Tuple[Optional[str], Optional[Any]]: 命令类型和参数，如果无法识别则返回(None, None)
        """
        if not text or not text.strip():
            logger.warning("收到空命令，无法解析")
            return None, None
            
        logger.info(f"开始解析命令: '{text}'")
        
        # 检查是否启用大模型解析
        use_ai = os.getenv('USE_DEEPSEEK', 'True').lower() in ('true', '1', 't', 'yes', 'y')
        
        # 首选大模型解析
        if use_ai:
            logger.info("尝试使用大模型解析命令")
            cmd_type, parameter = NLPProcessor.parse_with_deepseek(text)
            
            if cmd_type:
                logger.info(f"大模型成功解析命令: {cmd_type}, 参数: {parameter}")
                return cmd_type, parameter
            else:
                logger.warning("大模型解析失败，回退到本地解析")
        else:
            logger.info("大模型解析已禁用，直接使用本地解析")
        
        # 回退到本地解析
        return NLPProcessor.parse_command_local(text)