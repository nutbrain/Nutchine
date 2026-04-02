"""
主窗口模块
包含输入窗口的主界面逻辑
"""

import ctypes
from ctypes import wintypes
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLineEdit, QVBoxLayout, QDesktopWidget, 
    QSystemTrayIcon, QMenu, QAction, QMessageBox, QInputDialog
)
from PyQt5.QtCore import Qt, QEvent, QTimer
from PyQt5.QtGui import QColor, QPen, QIcon, QPainter, QPixmap
from PyQt5.QtWidgets import QGraphicsDropShadowEffect

from .engine_manager import EngineManager
from .utils import WM_HOTKEY, MOD_ALT, VK_F


class InputWindow(QWidget):
    """输入窗口类"""
    
    def __init__(self):
        super().__init__()
        # 初始化搜索引擎管理器
        self.engine_manager = EngineManager()
        self.initUI()
        # 注册全局热键
        self.register_hotkey()
        # 初始化托盘图标
        self.initTrayIcon()
    
    def initUI(self):
        """初始化用户界面"""
        self.setWindowTitle('输入窗口')
        self.setGeometry(0, 0, 900, 120)
        
        # 设置无边框窗口
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        # 设置窗口背景透明
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 移动到屏幕中心
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
        # 创建布局，设置边距
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        
        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText('请输入内容...')
        # 设置输入框样式
        self.input_box.setStyleSheet('''
            QLineEdit {
                background-color: rgba(30, 30, 40, 240);
                border: 3px solid transparent;
                border-radius: 16px;
                padding: 20px 25px;
                font-size: 28px;
                color: #FFFFFF;
                selection-background-color: #0078D7;
            }
            QLineEdit:focus {
                background-color: rgba(40, 40, 55, 245);
            }
            QLineEdit::placeholder {
                color: rgba(200, 200, 200, 150);
            }
        ''')
        
        # 添加光晕效果
        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(30)
        shadow_effect.setColor(QColor(0, 120, 215, 200))
        shadow_effect.setOffset(0, 0)
        self.input_box.setGraphicsEffect(shadow_effect)
        
        layout.addWidget(self.input_box)
        self.setLayout(layout)
        
        self.input_box.returnPressed.connect(self.on_return_pressed)
        # 注意：不使用 editingFinished，因为弹窗会导致失去焦点
        
        # 启动炫彩边框更新定时器
        self.gradient_angle = 0
        self.gradient_timer = QTimer()
        self.gradient_timer.timeout.connect(self.update_gradient_border)
        self.gradient_timer.start(50)  # 每 50ms 更新一次
    
    def update_gradient_border(self):
        """更新炫彩渐变边框 - 单色时间渐变"""
        self.gradient_angle = (self.gradient_angle + 1) % 360
        
        # 使用单色，但是颜色随时间渐变
        current_color = f"hsl({self.gradient_angle}, 100%, 50%)"
        
        gradient_style = f"""
            QLineEdit {{
                background-color: rgba(30, 30, 40, 240);
                border: 3px solid {current_color};
                border-radius: 16px;
                padding: 20px 25px;
                font-size: 28px;
                color: #FFFFFF;
                selection-background-color: #0078D7;
            }}
            QLineEdit:focus {{
                background-color: rgba(40, 40, 55, 245);
                border: 3px solid {current_color};
            }}
            QLineEdit::placeholder {{
                color: rgba(200, 200, 200, 150);
            }}
        """
        self.input_box.setStyleSheet(gradient_style)
    
    def createMagnifierIcon(self):
        """创建自定义放大镜图标"""
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制镜片（圆形）
        painter.setPen(QColor(50, 50, 50))
        painter.setBrush(QColor(200, 200, 255))
        painter.drawEllipse(2, 2, 20, 20)
        
        # 绘制镜柄（斜线）
        painter.setPen(QPen(QColor(50, 50, 50), 3))
        painter.drawLine(18, 18, 28, 28)
        
        painter.end()
        return QIcon(pixmap)
    
    def register_hotkey(self):
        """注册全局热键"""
        hwnd = int(self.winId())
        # 注册 Alt+F 热键
        result = ctypes.windll.user32.RegisterHotKey(
            hwnd, 1, MOD_ALT, VK_F
        )
        if not result:
            print("Failed to register hotkey")
        else:
            print("Hotkey registered successfully")
    
    def initTrayIcon(self):
        """初始化托盘图标"""
        self.tray_icon = QSystemTrayIcon(self)
        # 使用自定义的放大镜图标
        self.tray_icon.setIcon(self.createMagnifierIcon())
        self.tray_icon.setToolTip('输入窗口')
        
        # 创建托盘菜单
        self.tray_menu = QMenu()
        
        # 显示/隐藏窗口动作
        self.show_action = QAction('显示窗口', self)
        self.show_action.triggered.connect(self.show)
        
        # 退出动作
        self.quit_action = QAction('退出', self)
        self.quit_action.triggered.connect(QApplication.instance().quit)
        
        # 添加动作到菜单
        self.tray_menu.addAction(self.show_action)
        self.tray_menu.addAction(self.quit_action)
        
        # 设置托盘菜单
        self.tray_icon.setContextMenu(self.tray_menu)
        
        # 显示托盘图标
        self.tray_icon.show()
    
    def on_return_pressed(self):
        """处理回车键事件"""
        text = self.input_box.text()
        self.input_box.clear()
        
        # 解析命令
        self.process_command(text)
    
    def process_command(self, text):
        """处理输入命令"""
        text = text.strip()
        if not text:
            return
        
        # 检查是否是搜索引擎格式：name query（第一个空格前是 name，之后是 query）
        parts = text.split(' ', 1)
        if len(parts) == 2:
            engine_name = parts[0].strip().lower()
            query = parts[1].strip()
            
            # 检查第一个部分是否是一个有效的搜索引擎名称
            if engine_name in self.engine_manager.list_engines():
                self.search_with_engine(engine_name, query)
                return
        
        # 检查是否是添加引擎命令
        if text.lower().startswith('addengine '):
            parts = text[10:].strip().split(' ', 1)
            if len(parts) == 2:
                name, url = parts
                self.engine_manager.add_engine(name.lower(), url)
                print(f"Added engine: {name} -> {url}")
            else:
                print("Usage: addengine [name] [url]")
            return
        
        # 检查是否是删除引擎命令
        if text.lower().startswith('delengine '):
            name = text[10:].strip().lower()
            if self.engine_manager.del_engine(name):
                print(f"Deleted engine: {name}")
            else:
                print(f"Engine '{name}' not found")
            return
        
        # 检查是否是列出引擎命令
        if text.lower() == 'listengines':
            self.show_engines_dialog()
            return
        
        # 默认使用第一个搜索引擎（google）
        engines = self.engine_manager.list_engines()
        if engines:
            default_engine = engines[0]
            self.search_with_engine(default_engine, text)
    
    def search_with_engine(self, engine_name, query):
        """使用指定的搜索引擎搜索"""
        import webbrowser
        import urllib.parse
        
        url_template = self.engine_manager.get_engine(engine_name)
        if url_template:
            # 替换 {query} 为实际的搜索词
            encoded_query = urllib.parse.quote(query)
            url = url_template.replace('{query}', encoded_query)
            print(f"Searching with {engine_name}: {url}")
            # 打开浏览器
            webbrowser.open(url)
            # 搜索后隐藏窗口
            self.hide()
        else:
            print(f"Engine '{engine_name}' not found. Available engines: {', '.join(self.engine_manager.list_engines())}")
    
    def show_engines_dialog(self):
        """显示搜索引擎列表弹窗"""
        engines = self.engine_manager.list_engines()
        if not engines:
            QMessageBox.information(self, '搜索引擎列表', '暂无搜索引擎')
            return
        
        # 构建引擎列表文本
        engine_list = []
        for name in engines:
            url = self.engine_manager.get_engine(name)
            engine_list.append(f"{name}: {url}")
        
        message = '\n'.join(engine_list)
        QMessageBox.information(self, '搜索引擎列表', f'可用的搜索引擎：\n\n{message}')
    
    def toggleVisibility(self):
        """切换窗口显示/隐藏状态"""
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.activateWindow()
            # 显示后将焦点设置到输入框
            self.input_box.setFocus()
            self.input_box.activateWindow()
    
    def nativeEvent(self, eventType, message):
        """处理 Windows 原生事件"""
        if eventType == 'windows_generic_MSG':
            # 获取消息指针
            ptr = int(message)
            msg = wintypes.MSG.from_address(ptr)
            if msg.message == WM_HOTKEY and msg.wParam == 1:
                self.toggleVisibility()
                return True, 0
        return super().nativeEvent(eventType, message)
    
    def closeEvent(self, event):
        """处理窗口关闭事件"""
        # 注销热键
        ctypes.windll.user32.UnregisterHotKey(None, 1)
        super().closeEvent(event)
