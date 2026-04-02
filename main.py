"""
Nutchine - 快速启动搜索工具
主程序入口文件
"""

import sys
from PyQt5.QtWidgets import QApplication

from src.utils import kill_existing_instance
from src.main_window import InputWindow


def main():
    """主函数"""
    # 先关闭已存在的实例
    kill_existing_instance()
    
    app = QApplication(sys.argv)
    window = InputWindow()
    # 启动时默认隐藏
    window.hide()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
