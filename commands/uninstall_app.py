"""
卸载应用程序命令实现。
"""
import os
import logging
from typing import Tuple, Optional
from dotenv import load_dotenv

from utils.app_finder import AppFinder
from utils.platform_utils import PlatformUtils
from utils.device_utils import DeviceUtils
from utils.mac_utils import MacAppController

# 加载环境变量
load_dotenv()

# 配置日志
logger = logging.getLogger(__name__)

# 是否需要确认卸载
CONFIRM_UNINSTALL = os.getenv('CONFIRM_UNINSTALL', 'True').lower() in ('true', '1', 't')


def uninstall(app_name: str) -> Tuple[bool, str]:
    """
    执行卸载应用程序的命令
    
    Args:
        app_name: 应用程序名称
        
    Returns:
        Tuple[bool, str]: 执行结果（成功/失败）和结果消息
    """
    logger.info(f"执行卸载应用命令: {app_name}")
    
    # 查找应用
    resolved_app_name = AppFinder.find_app(app_name)
    
    if not resolved_app_name:
        error_msg = f"无法找到应用程序: {app_name}"
        logger.error(error_msg)
        return False, error_msg
    
    # 检查是否可以使用设备特定功能
    use_device_utils = DeviceUtils.is_available()
    
    # 尝试使用DeviceUtils卸载应用
    if use_device_utils:
        logger.info(f"使用DeviceUtils卸载应用: {resolved_app_name}")
        result = DeviceUtils.uninstall_application(resolved_app_name)
        if result:
            success_msg = f"成功卸载应用程序: {resolved_app_name}"
            logger.info(success_msg)
            return True, success_msg
    
    # 如果DeviceUtils不可用，检查是否可以使用MacAppController
    if MacAppController.is_mac():
        logger.info(f"使用MacAppController卸载应用: {resolved_app_name}")
        success, message = MacAppController.uninstall_app(resolved_app_name)
        if success:
            logger.info(message)
            return True, message
    
    # 最后回退到PlatformUtils
    logger.info(f"使用PlatformUtils卸载应用: {resolved_app_name}")
    result = PlatformUtils.uninstall_application(resolved_app_name)
    
    if result:
        success_msg = f"成功卸载应用程序: {resolved_app_name}"
        logger.info(success_msg)
        return True, success_msg
    else:
        error_msg = f"卸载应用程序失败: {resolved_app_name}"
        logger.error(error_msg)
        return False, error_msg