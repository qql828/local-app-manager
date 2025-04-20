"""
本地应用管理助手代理初始化文件

这个文件使local_app_manager目录成为一个Python包
并提供对代理的引用导出
"""

# 导入主项目中的agent
try:
    from ...agent import app_agent, runner, session_service
except ImportError:
    # 当直接运行时，尝试绝对导入
    from agent import app_agent, runner, session_service

# 导出代理
agent = app_agent