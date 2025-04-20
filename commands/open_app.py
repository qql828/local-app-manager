"""
打开应用命令实现，用于执行打开应用程序的命令。
"""
import logging
from typing import Tuple

from utils.app_finder import AppFinder
from utils.device_utils import DeviceUtils
from utils.platform_utils import PlatformUtils

# 配置日志
logger = logging.getLogger(__name__)


def open(app_name: str) -> Tuple[bool, str]:
    """
    执行打开应用的命令
    
    Args:
        app_name: 要打开的应用程序名称
        
    Returns:
        Tuple[bool, str]: 操作是否成功和结果消息
    """
    logger.info(f"执行打开应用命令: {app_name}")
    
    # 使用AppFinder查找应用
    app_info = AppFinder.find_app(app_name)
    
    if not app_info:
        logger.error(f"找不到应用: {app_name}")
        return False, f"找不到应用: {app_name}"
    
    # 获取实际应用名称 - 处理app_info可能是字符串的情况
    if isinstance(app_info, dict):
        actual_app_name = app_info.get("name", app_name)
    else:
        # 如果app_info是字符串，直接使用它
        actual_app_name = app_info
        
    logger.info(f"找到应用: {actual_app_name}")
    
    # 优先使用DeviceUtils如果可用
    try:
        # 尝试导入DeviceUtils模块
        success, message = DeviceUtils.open_application(actual_app_name)
        if success:
            logger.info(message)
            return True, f"成功打开应用: {actual_app_name}"
        else:
            logger.warning(f"DeviceUtils无法打开应用: {message}")
            # 回退到PlatformUtils
            if PlatformUtils.open_application(actual_app_name):
                return True, f"成功打开应用: {actual_app_name}"
            else:
                return False, f"无法打开应用: {actual_app_name}"
    except (ImportError, AttributeError) as e:
        logger.warning(f"DeviceUtils模块不可用，回退到PlatformUtils: {str(e)}")
        # 回退到PlatformUtils
        if PlatformUtils.open_application(actual_app_name):
            return True, f"成功打开应用: {actual_app_name}"
        else:
            return False, f"无法打开应用: {actual_app_name}"
    except Exception as e:
        logger.error(f"打开应用时出错: {str(e)}")
        return False, f"打开应用时出错: {str(e)}"