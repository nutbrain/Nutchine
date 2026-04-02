"""
工具函数模块
包含单实例检查、Windows API 常量等工具函数
"""

import ctypes
import os
import psutil

# Windows API 常量
WM_HOTKEY = 0x0312
MOD_ALT = 0x0001
VK_F = 0x46
VK_SPACE = 0x20
MOD_CONTROL = 0x0002
MOD_NOREPEAT = 0x4000


def kill_existing_instance():
    """查找并关闭已存在的实例"""
    try:
        current_pid = ctypes.windll.kernel32.GetCurrentProcessId()
        current_script = os.path.abspath(__file__)
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                # 检查是否是同一个程序
                if proc.info['pid'] != current_pid:
                    p = psutil.Process(proc.info['pid'])
                    cmdline = p.cmdline()
                    
                    # 检查命令行是否包含相同的脚本路径
                    if len(cmdline) > 1:
                        # 检查最后一个参数是否是我们的脚本
                        script_path = cmdline[-1] if cmdline else ''
                        if 'main.py' in script_path or 'input_window.py' in script_path:
                            print(f"Killing existing instance (PID: {proc.info['pid']})")
                            proc.terminate()
                            try:
                                proc.wait(timeout=3)
                            except psutil.TimeoutExpired:
                                proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except ImportError:
        print("psutil not installed, skipping instance check")
    except Exception as e:
        print(f"Error checking instances: {e}")
