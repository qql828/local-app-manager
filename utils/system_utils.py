"""
系统工具模块，提供与操作系统相关的通用函数。
"""
import os
import platform
import logging
from typing import Dict, Any, List, Optional

# 配置日志
logger = logging.getLogger(__name__)

class SystemUtils:
    """系统工具类，提供与操作系统相关的通用函数"""
    
    _standard_dirs_cache = None
    
    # 定义常用特殊目录映射（中文名到英文名的映射）
    SPECIAL_DIRS = {
        "桌面": "Desktop",
        "下载": "Downloads", 
        "文档": "Documents",
        "图片": "Pictures",
        "音乐": "Music",
        "视频": "Videos",
        "电影": "Movies",
        "应用": "Applications",
        "资源库": "Library",
        "主目录": "",  # 空字符串表示用户主目录
        "用户目录": "", 
        "根目录": "/",
        "当前目录": "."
    }
    
    # 特殊目录的别名映射
    DIR_ALIASES = {
        "downloads": "下载",
        "desktop": "桌面",
        "documents": "文档",
        "pictures": "图片",
        "music": "音乐",
        "videos": "视频",
        "movies": "视频",
        "applications": "应用",
        "library": "资源库",
        "home": "主目录",
        "user": "用户目录",
        "root": "根目录",
        "current": "当前目录"
    }
    
    @staticmethod
    def get_standard_directories() -> Dict[str, str]:
        """
        获取系统标准目录，兼容不同操作系统
        
        Returns:
            Dict[str, str]: 目录名称和路径的字典
        """
        # 使用缓存避免重复计算
        if SystemUtils._standard_dirs_cache is not None:
            return SystemUtils._standard_dirs_cache
            
        # 获取系统类型和用户主目录
        system = platform.system()
        home = os.path.expanduser("~")
        
        # 初始化基本目录
        dirs = {
            "主目录": home,
            "home": home,
            "用户目录": home,
            "当前目录": ".",
            "current": "."
        }
        
        # 尝试添加常用目录
        for cn_name, en_name in SystemUtils.SPECIAL_DIRS.items():
            if en_name and en_name != "/":  # 排除特殊情况
                # 构建可能的目录路径
                if en_name == ".":
                    path = "."
                else:
                    path = os.path.join(home, en_name)
                
                # 验证目录是否存在
                if os.path.exists(path) and os.path.isdir(path):
                    dirs[cn_name] = path
                    # 添加英文别名
                    en_key = en_name.lower()
                    if en_key not in dirs:
                        dirs[en_key] = path
        
        # Windows特定目录
        if system == "Windows":
            if "PROGRAMFILES" in os.environ:
                dirs["应用"] = dirs["applications"] = os.environ["PROGRAMFILES"]
                
            # 添加Windows特有的目录
            for env_var in ["APPDATA", "LOCALAPPDATA", "PUBLIC", "PROGRAMDATA"]:
                if env_var in os.environ and os.path.exists(os.environ[env_var]):
                    if env_var == "APPDATA":
                        dirs["应用数据"] = dirs["appdata"] = os.environ[env_var]
                    elif env_var == "LOCALAPPDATA":
                        dirs["本地应用数据"] = dirs["localappdata"] = os.environ[env_var]
                    elif env_var == "PUBLIC":
                        dirs["公共"] = dirs["public"] = os.environ[env_var]
                    elif env_var == "PROGRAMDATA":
                        dirs["程序数据"] = dirs["programdata"] = os.environ[env_var]
                
        # macOS特定目录 
        elif system == "Darwin":
            if os.path.exists("/Applications"):
                dirs["应用"] = dirs["applications"] = "/Applications"
            
            # 添加macOS特有的目录
            library_path = os.path.join(home, "Library")
            if os.path.exists(library_path):
                dirs["资源库"] = dirs["library"] = library_path
        
        # Linux特定目录
        elif system == "Linux":
            # 检查常见Linux目录
            for dir_path in ["/usr/bin", "/usr/local/bin", "/opt"]:
                if os.path.exists(dir_path):
                    if "bin" in dir_path:
                        dirs["可执行文件"] = dirs["bin"] = dir_path
                    elif dir_path == "/opt":
                        dirs["可选程序"] = dirs["opt"] = dir_path
        
        # 存入缓存
        SystemUtils._standard_dirs_cache = dirs
        logger.info(f"已获取系统标准目录: {len(dirs)}个")
        
        return dirs
    
    @staticmethod
    def resolve_path(path: str) -> str:
        """
        解析路径，支持相对路径、~符号等
        
        Args:
            path: 要解析的路径
            
        Returns:
            str: 解析后的绝对路径
        """
        # 处理空路径
        if not path:
            return os.getcwd()
            
        # 展开用户主目录符号
        if path.startswith('~'):
            path = os.path.expanduser(path)
            
        # 处理相对路径
        if not os.path.isabs(path):
            path = os.path.abspath(path)
            
        return path
    
    @staticmethod
    def find_directory_by_name(name: str) -> Optional[str]:
        """
        根据名称查找目录路径
        
        Args:
            name: 目录名称(如"下载"、"桌面"等)
            
        Returns:
            Optional[str]: 找到的目录路径，未找到返回None
        """
        dirs = SystemUtils.get_standard_directories()
        
        # 直接匹配
        if name in dirs:
            return dirs[name]
            
        # 尝试部分匹配
        name_lower = name.lower()
        for key, path in dirs.items():
            if key.lower() == name_lower or name_lower in key.lower():
                return path
                
        return None
    
    @staticmethod
    def get_safe_path(path: str, fallback_to_home: bool = True) -> str:
        """
        获取安全路径，如果路径不存在则回退到替代路径
        
        Args:
            path: 原始路径
            fallback_to_home: 如果为True，不存在的路径回退到用户主目录
            
        Returns:
            str: 安全路径
        """
        # 解析路径
        resolved_path = SystemUtils.resolve_path(path)
        
        # 检查路径是否存在
        if os.path.exists(resolved_path) and os.path.isdir(resolved_path):
            return resolved_path
            
        # 如果是标准目录名称，尝试查找
        if not os.path.sep in path:
            std_path = SystemUtils.find_directory_by_name(path)
            if std_path and os.path.exists(std_path) and os.path.isdir(std_path):
                return std_path
                
        # 回退到用户主目录
        if fallback_to_home:
            logger.warning(f"路径不存在，回退到用户主目录: {path}")
            return os.path.expanduser("~")
            
        return resolved_path