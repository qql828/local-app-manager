#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
本地应用管理助手主入口

这个文件是应用程序的主入口点，提供命令行交互界面。
用户可以通过自然语言输入命令，系统会解析并执行相应的操作。
"""

import os
import sys
import logging
import argparse
from typing import List, Dict, Tuple, Any, Optional

# 导入dotenv处理环境变量
from dotenv import load_dotenv

# 加载环境变量（配置文件），用于控制应用行为
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.DEBUG if os.getenv('DEBUG', 'False').lower() in ('true', '1', 't') else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# 导入命令处理模块
from utils.nlp_processor import NLPProcessor
import commands.open_app as open_app
import commands.close_app as close_app
import commands.uninstall_app as uninstall_app
import commands.list_running as list_running
import commands.list_installed as list_installed
import commands.volume_control as volume_control
import commands.brightness_control as brightness_control
import commands.file_operations as file_operations
import commands.weather_query as weather_query

# 是否需要确认卸载
CONFIRM_UNINSTALL = os.getenv('CONFIRM_UNINSTALL', 'True').lower() in ('true', '1', 't')


def process_command(command_text: str) -> Tuple[bool, str]:
    """
    处理用户输入的命令
    
    Args:
        command_text: 用户输入的命令文本
        
    Returns:
        Tuple[bool, str]: 执行结果（成功/失败）和结果消息
    """
    if not command_text:
        return False, "请输入命令"
    
    logger.info(f"用户输入: {command_text}")
    
    # 特殊处理卸载命令的确认
    if "确认卸载" in command_text or "确认删除" in command_text:
        # 从命令中提取应用名称
        app_name = command_text.replace("确认卸载", "").replace("确认删除", "").strip()
        logger.info(f"用户确认卸载应用: {app_name}")
        return uninstall_app.uninstall(app_name)
    
    # 使用NLP处理器解析命令
    parsed_result = NLPProcessor.parse_command(command_text)
    
    if not parsed_result or not parsed_result.get('command_type'):
        logger.warning(f"无法解析命令: {command_text}")
        return False, f"无法理解命令: {command_text}\n请尝试使用更明确的表述，例如"打开Chrome"或"关闭微信"。"
    
    command_type = parsed_result['command_type']
    parameters = parsed_result.get('parameters', {})
    
    logger.info(f"解析结果: 命令类型={command_type}, 参数={parameters}")
    
    # 根据命令类型执行相应操作
    try:
        # 应用操作命令
        if command_type == NLPProcessor.CMD_OPEN:
            app_name = parameters.get('app_name')
            if not app_name:
                return False, "需要指定应用名称"
            return open_app.open(app_name)
            
        elif command_type == NLPProcessor.CMD_CLOSE:
            app_name = parameters.get('app_name')
            if not app_name:
                return False, "需要指定应用名称"
            return close_app.close(app_name)
            
        elif command_type == NLPProcessor.CMD_UNINSTALL:
            app_name = parameters.get('app_name')
            if not app_name:
                return False, "需要指定应用名称"
                
            # 如果需要确认卸载
            if CONFIRM_UNINSTALL:
                return True, f"您确定要卸载 {app_name} 吗？如果确认，请输入"确认卸载 {app_name}""
            else:
                return uninstall_app.uninstall(app_name)
                
        elif command_type == NLPProcessor.CMD_LIST_RUNNING:
            success, result = list_running.list_running()
            if success:
                return success, format_app_list(result, "正在运行的应用")
            return success, result
            
        elif command_type == NLPProcessor.CMD_LIST_INSTALLED:
            success, result = list_installed.list_installed()
            if success:
                return success, format_app_list(result, "已安装的应用")
            return success, result
            
        # 设备控制命令
        elif command_type == NLPProcessor.CMD_VOLUME:
            action = parameters.get('action')
            value = parameters.get('value')
            return volume_control.control_volume(action, value)
            
        elif command_type == NLPProcessor.CMD_BRIGHTNESS:
            action = parameters.get('action')
            value = parameters.get('value')
            return brightness_control.control_brightness(action, value)
            
        # 文件操作命令
        elif command_type == NLPProcessor.CMD_LIST_FILES:
            directory = parameters.get('directory')
            return file_operations.list_files(directory)
            
        elif command_type == NLPProcessor.CMD_CREATE_FILE:
            file_path = parameters.get('file_path')
            content = parameters.get('content', '')
            return file_operations.create_file(file_path, content)
            
        elif command_type == NLPProcessor.CMD_CREATE_DIRECTORY:
            directory_path = parameters.get('directory_path')
            return file_operations.create_directory(directory_path)
            
        elif command_type == NLPProcessor.CMD_DELETE_FILE:
            file_path = parameters.get('file_path')
            return file_operations.delete_file(file_path)
            
        elif command_type == NLPProcessor.CMD_DELETE_DIRECTORY:
            directory_path = parameters.get('directory_path')
            return file_operations.delete_directory(directory_path)
            
        elif command_type == NLPProcessor.CMD_MOVE_FILE:
            source_path = parameters.get('source_path')
            target_path = parameters.get('target_path')
            return file_operations.move_file(source_path, target_path)
            
        elif command_type == NLPProcessor.CMD_COPY_FILE:
            source_path = parameters.get('source_path')
            target_path = parameters.get('target_path')
            return file_operations.copy_file(source_path, target_path)
            
        elif command_type == NLPProcessor.CMD_RENAME_FILE:
            source_path = parameters.get('source_path')
            target_path = parameters.get('target_path')
            return file_operations.rename_file(source_path, target_path)
            
        elif command_type == NLPProcessor.CMD_READ_FILE:
            file_path = parameters.get('file_path')
            return file_operations.read_file(file_path)
            
        elif command_type == NLPProcessor.CMD_WRITE_FILE:
            file_path = parameters.get('file_path')
            content = parameters.get('content', '')
            return file_operations.write_file(file_path, content)
            
        elif command_type == NLPProcessor.CMD_LIST_SUBDIRECTORIES:
            directory_path = parameters.get('directory_path')
            success, result = file_operations.list_subdirectories(directory_path)
            if success and isinstance(result, list):
                return success, format_directory_list(result, f"{directory_path}中的子目录")
            return success, result
            
        # 其他命令
        elif command_type == NLPProcessor.CMD_WEATHER:
            location = parameters.get('location', '当前位置')
            return weather_query.query_weather(location)
            
        else:
            logger.warning(f"未支持的命令类型: {command_type}")
            return False, f"暂不支持该命令: {command_text}"
            
    except Exception as e:
        logger.exception(f"执行命令时出错: {str(e)}")
        return False, f"执行命令时出错: {str(e)}"


def format_result(success: bool, message: str) -> str:
    """
    格式化结果输出
    
    Args:
        success: 是否成功
        message: 结果消息
        
    Returns:
        str: 格式化后的消息
    """
    prefix = "✅ " if success else "❌ "
    return f"{prefix}{message}"


def format_app_list(app_list: List[Dict[str, Any]], title: str) -> str:
    """
    格式化应用列表输出
    
    Args:
        app_list: 应用列表
        title: 标题
        
    Returns:
        str: 格式化后的应用列表
    """
    if not app_list:
        return f"{title}:\n  无应用"
        
    formatted_list = [f"{title}:"]
    
    # 检查列表项的格式
    if isinstance(app_list[0], dict):
        # 如果是字典列表，提取名称和其他信息
        for app in app_list:
            app_name = app.get('name', 'Unknown')
            app_pid = app.get('pid', '')
            
            if app_pid:
                formatted_list.append(f"  {app_name} (PID: {app_pid})")
            else:
                formatted_list.append(f"  {app_name}")
    else:
        # 如果是字符串列表，直接添加
        for app in app_list:
            formatted_list.append(f"  {app}")
            
    return "\n".join(formatted_list)


def format_directory_list(directories: List[Dict[str, Any]], title: str) -> str:
    """
    格式化目录列表输出
    
    Args:
        directories: 目录列表
        title: 标题
        
    Returns:
        str: 格式化后的目录列表
    """
    if not directories:
        return f"{title}:\n  无子目录"
        
    formatted_list = [f"{title}:"]
    
    # 检查列表项的格式
    if isinstance(directories[0], dict):
        for directory in directories:
            dir_name = directory.get('name', 'Unknown')
            dir_path = directory.get('path', '')
            
            if dir_path and dir_path != dir_name:
                formatted_list.append(f"  {dir_name} ({dir_path})")
            else:
                formatted_list.append(f"  {dir_name}")
    else:
        for directory in directories:
            formatted_list.append(f"  {directory}")
            
    return "\n".join(formatted_list)


def main():
    """
    应用程序主入口函数
    """
    parser = argparse.ArgumentParser(description='本地应用管理助手')
    parser.add_argument('command', nargs='?', help='要执行的命令')
    args = parser.parse_args()
    
    try:
        # 如果提供了命令行参数，执行命令并退出
        if args.command:
            result = process_command(args.command)
            print(format_result(*result))
            return
            
        # 否则进入交互模式
        print("欢迎使用本地应用管理助手！")
        print("您可以输入自然语言命令，例如：")
        print("  - 打开Chrome")
        print("  - 关闭微信")
        print("  - 音量调到50%")
        print("  - 在下载目录创建test文件夹")
        print("输入'exit'或'quit'退出程序")
        print("-" * 50)
        
        while True:
            try:
                command = input("\n请输入命令: ").strip()
                
                if command.lower() in ('exit', 'quit', '退出', '关闭'):
                    break
                
                # 处理空命令
                if not command:
                    continue
                
                # 处理命令并显示结果
                result = process_command(command)
                print(result)
            
            except KeyboardInterrupt:
                print("\n程序已被用户中断")
                break
            
            except Exception as e:
                logger.exception(f"发生错误: {str(e)}")
                print(f"发生错误: {str(e)}")
            
        print("程序已退出")


if __name__ == "__main__":
    main()