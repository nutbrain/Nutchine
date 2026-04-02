# Nutchine

一个快速启动搜索工具，支持自定义搜索引擎，使用全局快捷键快速呼出。

## 功能特性

- 🔍 支持多个预设搜索引擎（Google、百度、Bing、哔哩哔哩、YouTube）
- ➕ 支持自定义添加/删除搜索引擎
- ⌨️ 全局快捷键（Alt+F）快速呼出/隐藏窗口
- 🎨 炫彩渐变边框，颜色随时间平滑变化
- 📱 系统托盘图标，支持右键菜单操作
- 🚀 单实例运行，新实例自动关闭旧实例
- 🎯 无边框窗口设计，始终保持在顶层

## 项目结构

```
Nutchine/
├── main.py              # 主程序入口
├── requirements.txt     # 项目依赖
├── config/              # 配置文件目录
│   └── .engine.json    # 搜索引擎配置
└── src/                 # 源代码目录
    ├── __init__.py
    ├── main_window.py   # 主窗口模块
    ├── engine_manager.py # 搜索引擎管理模块
    └── utils.py         # 工具函数模块
```

## 安装

1. 安装 Python 依赖：

```bash
pip install -r requirements.txt
```

## 使用方法

### 启动程序

```bash
python main.py
```

### 搜索功能

- **使用指定搜索引擎**：`engine_name search query`
  - 示例：`google python tutorial`
  - 示例：`baidu 人工智能`
  - 示例：`bilibili 编程教程`

- **默认搜索**：直接输入文字会使用默认搜索引擎（第一个）
  - 示例：`python tutorial`

### 引擎管理命令

- **添加引擎**：`addengine name url`
  - 示例：`addengine github https://github.com/search?q={query}`

- **删除引擎**：`delengine name`
  - 示例：`delengine github`

- **列出引擎**：`listengines`

### 快捷键

- **Alt+F**：显示/隐藏窗口

## 配置

搜索引擎配置文件位于 `config/.engine.json`，格式如下：

```json
{
    "engine_name": "https://example.com/search?q={query}",
    ...
}
```

URL 中的 `{query}` 会被自动替换为实际的搜索关键词。

## 技术栈

- Python 3.x
- PyQt5 - GUI 框架
- psutil - 进程管理
