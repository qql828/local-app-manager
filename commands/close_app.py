"""
关闭应用程序命令实现。
"""
import logging
import os
from typing import Tuple, Optional
from dotenv import load_dotenv

from utils.app_finder import AppFinder
from utils.platform_utils import PlatformUtils
from utils.device_utils import DeviceUtils
from utils.mac_utils import MacAppController

# 配置日志
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()


def close(app_name: str) -> Tuple[bool, str]:
    """
    执行关闭应用程序的命令
    
    Args:
        app_name: 应用程序名称
        
    Returns:
        Tuple[bool, str]: 执行结果（成功/失败）和结果消息
    """
    logger.info(f"执行关闭应用命令: {app_name}")
    
    # 查找应用
    resolved_app_name = AppFinder.find_app(app_name)
    
    if not resolved_app_name:
        # 即使找不到确切的应用名称，也尝试关闭，因为进程名可能与应用名不完全一致
        logger.warning(f"未找到精确匹配的应用: {app_name}，尝试使用原始名称关闭")
        resolved_app_name = app_name
    
    # 检查是否可以使用设备特定功能
    use_device_utils = DeviceUtils.is_available()
    
    # 尝试使用DeviceUtils关闭应用
    if use_device_utils:
        logger.info(f"使用DeviceUtils关闭应用: {resolved_app_name}")
        result = DeviceUtils.close_application(resolved_app_name)
        if result:
            success_msg = f"成功关闭应用程序: {resolved_app_name}"
            logger.info(success_msg)
            return True, success_msg
    
    # 如果DeviceUtils不可用，检查是否可以使用MacAppController
    if MacAppController.is_mac():
        logger.info(f"使用MacAppController关闭应用: {resolved_app_name}")
        success, message = MacAppController.close_app(resolved_app_name)
        if success:
            logger.info(message)
            return True, message
    
    # 最后回退到PlatformUtils
    logger.info(f"使用PlatformUtils关闭应用: {resolved_app_name}")
    result = PlatformUtils.close_application(resolved_app_name)
    
    if result:
        success_msg = f"成功关闭应用程序: {resolved_app_name}"
        logger.info(success_msg)
        return True, success_msg
    else:
        error_msg = f"关闭应用程序失败: {resolved_app_name}。可能该应用未在运行。"
        logger.error(error_msg)
        return False, error_msg