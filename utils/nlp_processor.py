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