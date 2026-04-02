import sys
import ctypes
import json
import os
import webbrowser
from ctypes import wintypes
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QVBoxLayout, QDesktopWidget, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtCore import Qt, QCoreApplication, QEvent, QObject, QPropertyAnimation, QEasingCurve
from PyQt5.QtWidgets import QGraphicsDropShadowEffect
from PyQt5.QtGui import QKeySequence, QIcon, QPainter, QPixmap, QColor, QPen

# Windows API 常量
WM_HOTKEY = 0x0312
MOD_ALT = 0x0001
VK_F = 0x46

# 用于单实例的互斥量名称
MUTEX_NAME = 'InputWindow_SingleInstance_Mutex'

# 搜索引擎配置文件路径
ENGINE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.engine.json')

class EngineManager:
    """搜索引擎管理器"""
    def __init__(self):
        self.engines = {}
        self.load_engines()
    
    def load_engines(self):
        """加载搜索引擎配置"""
        try:
            if os.path.exists(ENGINE_FILE):
                with open(ENGINE_FILE, 'r', encoding='utf-8') as f:
                    self.engines = json.load(f)
        except Exception as e:
            print(f"Error loading engines: {e}")
            self.engines = {}
    
    def save_engines(self):
        """保存搜索引擎配置"""
        try:
            with open(ENGINE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.engines, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving engines: {e}")
    
    def add_engine(self, name, url):
        """添加搜索引擎"""
        self.engines[name] = url
        self.save_engines()
    
    def del_engine(self, name):
        """删除搜索引擎"""
        if name in self.engines:
            del self.engines[name]
            self.save_engines()
            return True
        return False
    
    def get_engine(self, name):
        """获取搜索引擎 URL"""
        return self.engines.get(name)
    
    def list_engines(self):
        """列出所有搜索引擎"""
        return list(self.engines.keys())

def kill_existing_instance():
    """查找并关闭已存在的实例"""
    try:
        # 枚举所有进程
        import psutil
        import os
        
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
                        if 'input_window.py' in script_path:
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

class InputWindow(QWidget):
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
        # 设置输入框样式 - 基础样式
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
        
        # 创建渐变动画
        self.gradient_animation = QPropertyAnimation(self.input_box, b"geometry")
        self.gradient_animation.setDuration(2000)
        self.gradient_animation.setEasingCurve(QEasingCurve.InOutSine)
        
        layout.addWidget(self.input_box)
        self.setLayout(layout)
        
        self.input_box.returnPressed.connect(self.on_return_pressed)
        self.input_box.editingFinished.connect(self.hide)
        
        # 启动炫彩边框更新定时器
        self.gradient_angle = 0
        from PyQt5.QtCore import QTimer
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
        # 创建自定义放大镜图标
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
        # 获取窗口句柄
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
        # 创建托盘图标
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
            engines = self.engine_manager.list_engines()
            print(f"Available engines: {', '.join(engines)}")
            return
        
        # 默认使用第一个搜索引擎（google）
        engines = self.engine_manager.list_engines()
        if engines:
            default_engine = engines[0]
            self.search_with_engine(default_engine, text)
    
    def search_with_engine(self, engine_name, query):
        """使用指定的搜索引擎搜索"""
        url_template = self.engine_manager.get_engine(engine_name)
        if url_template:
            # 替换 {query} 为实际的搜索词
            import urllib.parse
            encoded_query = urllib.parse.quote(query)
            url = url_template.replace('{query}', encoded_query)
            print(f"Searching with {engine_name}: {url}")
            # 打开浏览器
            webbrowser.open(url)
            # 搜索后隐藏窗口
            self.hide()
        else:
            print(f"Engine '{engine_name}' not found. Available engines: {', '.join(self.engine_manager.list_engines())}")
    
    def toggleVisibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.activateWindow()
            # 显示后将焦点设置到输入框
            self.input_box.setFocus()
            self.input_box.activateWindow()
    
    def nativeEvent(self, eventType, message):
        # 处理 Windows 消息
        if eventType == 'windows_generic_MSG':
            # 获取消息指针
            ptr = int(message)
            msg = wintypes.MSG.from_address(ptr)
            if msg.message == WM_HOTKEY and msg.wParam == 1:
                self.toggleVisibility()
                return True, 0
        return super().nativeEvent(eventType, message)
    
    def closeEvent(self, event):
        # 注销热键
        ctypes.windll.user32.UnregisterHotKey(None, 1)
        super().closeEvent(event)

if __name__ == '__main__':
    # 先关闭已存在的实例
    kill_existing_instance()
    
    app = QApplication(sys.argv)
    window = InputWindow()
    # 启动时默认隐藏
    window.hide()
    sys.exit(app.exec_())