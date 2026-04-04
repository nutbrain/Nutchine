"""
搜索引擎管理模块
负责加载、保存、添加、删除搜索引擎配置
"""

import json
import os
import sys

# 默认搜索引擎配置（打包进 exe 的默认值）
DEFAULT_ENGINES = {
    "google": "https://www.google.com/search?q={query}",
    "gai": "https://www.google.com/search?q={query}&sca_esv=b64da7969411eeee&sxsrf=ANbL-n5LTr34hqdM48eBK3hmbVYgKqJ3jg%3A1775266503817&source=hp&ei=x2rQaeixMPTKkPIPpI-hqQI&iflsig=AFdpzrgAAAAAadB410xt2RhjytImUD6YNgF6Dk-lSTbz&aep=22&udm=50&ved=0ahUKEwiosdyKh9OTAxV0JUQIHaRHKCUQteYPCBE&oq=&gs_lp=Egdnd3Mtd2l6IgBIAFAAWABwAHgAkAEAmAEAoAEAqgEAuAEByAEAmAIAoAIAmAMAkgcAoAcAsgcAuAcAwgcAyAcAgAgB&sclient=gws-wiz",
    "baidu": "https://www.baidu.com/s?wd={query}",
    "bing": "https://www.bing.com/search?q={query}",
    "bilibili": "https://search.bilibili.com/all?keyword={query}",
    "youtube": "https://www.youtube.com/results?search_query={query}"
}

def get_config_path():
    """获取配置文件路径（与 exe 在同一目录）"""
    # 始终使用 exe 所在目录或项目根目录
    if getattr(sys, 'frozen', False):
        # 打包后的环境 - 使用 exe 所在目录
        base_path = os.path.dirname(sys.executable)
    else:
        # 开发环境 - 使用项目根目录
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    config_dir = os.path.join(base_path, 'config')
    # 确保 config 目录存在
    os.makedirs(config_dir, exist_ok=True)
    
    return os.path.join(config_dir, '.engine.json')

# 搜索引擎配置文件路径
ENGINE_FILE = get_config_path()


class EngineManager:
    """搜索引擎管理器"""
    
    def __init__(self):
        self.engines = {}
        self.load_engines()
    
    def load_engines(self):
        """加载搜索引擎配置"""
        try:
            if os.path.exists(ENGINE_FILE):
                # 配置文件存在，直接加载
                with open(ENGINE_FILE, 'r', encoding='utf-8') as f:
                    self.engines = json.load(f)
            else:
                # 配置文件不存在，使用内置默认配置
                self.engines = DEFAULT_ENGINES
                self.save_engines()
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
