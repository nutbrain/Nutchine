"""
搜索引擎管理模块
负责加载、保存、添加、删除搜索引擎配置
"""

import json
import os

# 搜索引擎配置文件路径
ENGINE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', '.engine.json')


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
