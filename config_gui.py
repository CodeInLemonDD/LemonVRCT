#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VRChat Voice Translation Software - Configuration Interface (Simplified Version)
VRChat语音翻译软件 - 配置界面 (简化版)
Standalone GUI interface for adjusting settings without affecting console functionality
独立的GUI界面用于调整设置，不影响原有的控制台功能
Uses standard tkinter to avoid compatibility issues
使用标准tkinter，避免兼容性问题
"""

import ttkbootstrap as tk
from tkinter import ttk, messagebox, scrolledtext
import os
import sys
import io
from dotenv import load_dotenv
import time

# 设置系统编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 加载环境变量
load_dotenv()

# 双语文本定义
class BilingualText:
    """双语文本管理器"""
    def __init__(self):
        self.current_language = "zh"  # 默认中文
        self.texts = {
            "zh": {
                # 窗口标题
                "window_title": "VRChat语音翻译软件 - 配置界面",
                # 框架标题
                "config_frame": "配置设置",
                "log_frame": "操作日志",
                # 标签文本
                "source_language": "源语言:",
                "target_languages": "目标语言:",
                "microphone_device": "麦克风设备:",
                "whisper_model": "Whisper模型:",
                "api_url": "API链接:",
                "api_key": "API密钥:",
                "api_model": "模型:",
                "osc_address": "OSC地址:",
                "osc_port": "端口:",
                "hotkey": "快捷键:",
                "audio_chunk": "音频块大小:",
                "audio_rate": "采样率:",
                "audio_channels": "声道数:",
                "log_level": "日志级别:",
                # 按钮文本
                "save_config": "保存配置",
                "reload_config": "重新加载",
                "reset_default": "重置默认",
                "clear_logs": "清空日志",
                # 设备选项
                "device_options": ["0: 默认设备", "1: 系统默认", "2: 主麦克风"],
                # 日志消息
                "interface_started": "配置界面已启动",
                "config_loaded": "配置已加载到界面",
                "config_saved": "配置已保存到.env文件，请完全退出该程序重新加载",
                "config_save_failed": "保存配置失败",
                "default_reset": "已重置为默认配置",
                # 消息框
                "success": "成功",
                "error": "错误",
                "confirm": "确认",
                "reset_confirm": "确定要重置为默认配置吗？"
            },
            "en": {
                # 窗口标题
                "window_title": "VRChat Voice Translation Software - Configuration Interface",
                # 框架标题
                "config_frame": "Configuration Settings",
                "log_frame": "Operation Log",
                # 标签文本
                "source_language": "Source Language:",
                "target_languages": "Target Languages:",
                "microphone_device": "Microphone Device:",
                "whisper_model": "Whisper Model:",
                "api_url": "API URL:",
                "api_key": "API Key:",
                "api_model": "Model:",
                "osc_address": "OSC Address:",
                "osc_port": "Port:",
                "hotkey": "Hotkey:",
                "audio_chunk": "Audio Chunk Size:",
                "audio_rate": "Sample Rate:",
                "audio_channels": "Channels:",
                "log_level": "Log Level:",
                # 按钮文本
                "save_config": "Save Configuration",
                "reload_config": "Reload",
                "reset_default": "Reset Default",
                "clear_logs": "Clear Logs",
                # 设备选项
                "device_options": ["0: Default Device", "1: System Default", "2: Primary Microphone"],
                # 日志消息
                "interface_started": "Configuration interface started",
                "config_loaded": "Configuration loaded to interface",
                "config_saved": "Configuration saved to .env file.Please completely exit the program and reload it.",
                "config_save_failed": "Failed to save configuration",
                "default_reset": "Default configuration reset",
                # 消息框
                "success": "Success",
                "error": "Error",
                "confirm": "Confirm",
                "reset_confirm": "Are you sure you want to reset to default configuration?"
            }
        }
    
    def get(self, key):
        """获取当前语言的文本"""
        return self.texts[self.current_language].get(key, key)
    
    def set_language(self, language):
        """设置语言"""
        if language in self.texts:
            self.current_language = language
    
    def get_all_texts(self):
        """获取当前语言的所有文本"""
        return self.texts[self.current_language]

class ConfigManager:
    """配置管理器 - 专门处理.env文件读写"""
    def __init__(self):
        self.env_file = '.env'
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """从.env文件加载配置"""
        try:
            if os.path.exists(self.env_file):
                with open(self.env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            self.config[key.strip()] = value.strip()
            else:
                # 如果.env文件不存在，创建默认配置
                self.create_default_config()
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            self.create_default_config()
    
    def create_default_config(self):
        """创建默认配置"""
        self.config = {
            "SOURCE_LANGUAGE": "zh",
            "TARGET_LANGUAGES": "en",
            "OSC_IP": "127.0.0.1",
            "OSC_PORT": "9000",
            "HOTKEY": "k",
            "AUDIO_DEVICE_INDEX": "0",
            "WHISPER_MODEL": "large-v3-turbo",
            "DEEPSEEK_BASE_URL": "https://api.deepseek.com",
            "DEEPSEEK_API_KEY": "",
            "DEEPSEEK_MODEL": "deepseek-chat",
            "AUDIO_CHUNK": "1024",
            "AUDIO_RATE": "16000",
            "AUDIO_CHANNELS": "1",
            "LOG_LEVEL": "INFO"
        }
        self.save_config()
    
    def save_config(self):
        """保存配置到.env文件"""
        try:
            with open(self.env_file, 'w', encoding='utf-8') as f:
                for key, value in self.config.items():
                    f.write(f"{key}={value}\n")
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False
    
    def get(self, key, default=None):
        """获取配置值"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """设置配置值"""
        self.config[key] = value

class ConfigGUI:
    def __init__(self):
        # 双语文本管理器
        self.text_manager = BilingualText()
        
        # 创建主窗口
        self.root = tk.Window(title='config', themename='minty')
        self.root.title(self.text_manager.get("window_title"))
        self.root.geometry("800x600")
        
        # 配置管理器
        self.config_manager = ConfigManager()
        
        # 创建界面
        self.setup_gui()
        
        # 加载当前配置
        self.load_current_config()
        
        self.log_message(self.text_manager.get("interface_started"))
    
    def setup_gui(self):
        """设置图形界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text=self.text_manager.get("window_title"), font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # 语言切换按钮
        lang_frame = ttk.Frame(main_frame)
        lang_frame.pack(pady=(0, 10))
        ttk.Button(lang_frame, text="English", command=lambda: self.switch_language("en")).pack(side="left", padx=(0, 5))
        ttk.Button(lang_frame, text="中文", command=lambda: self.switch_language("zh")).pack(side="left")
        
        # 配置区域
        self.setup_config_section(main_frame)
        
        # 日志显示区域
        self.setup_log_section(main_frame)
        
    def switch_language(self, language):
        """切换语言"""
        self.text_manager.set_language(language)
        self.root.title(self.text_manager.get("window_title"))
        self.update_ui_texts()
        self.log_message(f"Language switched to {language}")
    
    def update_ui_texts(self):
        """更新界面文本"""
        # 更新配置框架标题
        self.config_frame.configure(text=self.text_manager.get("config_frame"))
        
        # 更新日志框架标题
        self.log_frame.configure(text=self.text_manager.get("log_frame"))
        
        # 更新按钮文本
        self.save_button.configure(text=self.text_manager.get("save_config"))
        self.reload_button.configure(text=self.text_manager.get("reload_config"))
        self.reset_button.configure(text=self.text_manager.get("reset_default"))
        self.clear_logs_button.configure(text=self.text_manager.get("clear_logs"))
        
        # 更新标签文本
        self.source_lang_label.configure(text=self.text_manager.get("source_language"))
        self.target_lang_label.configure(text=self.text_manager.get("target_languages"))
        self.microphone_label.configure(text=self.text_manager.get("microphone_device"))
        self.whisper_label.configure(text=self.text_manager.get("whisper_model"))
        self.api_url_label.configure(text=self.text_manager.get("api_url"))
        self.api_key_label.configure(text=self.text_manager.get("api_key"))
        self.api_model_label.configure(text=self.text_manager.get("api_model"))
        self.osc_address_label.configure(text=self.text_manager.get("osc_address"))
        self.osc_port_label.configure(text=self.text_manager.get("osc_port"))
        self.hotkey_label.configure(text=self.text_manager.get("hotkey"))
        self.audio_chunk_label.configure(text=self.text_manager.get("audio_chunk"))
        self.audio_rate_label.configure(text=self.text_manager.get("audio_rate"))
        self.audio_channels_label.configure(text=self.text_manager.get("audio_channels"))
        self.log_level_label.configure(text=self.text_manager.get("log_level"))
        
        # 更新设备选项
        device_options = self.text_manager.get("device_options")
        self.audio_device_combo.configure(values=device_options)
        
    def setup_config_section(self, parent):
        """设置配置区域"""
        self.config_frame = ttk.LabelFrame(parent, text=self.text_manager.get("config_frame"), padding="10")
        self.config_frame.pack(fill="x", pady=(0, 10))
        
        # 源语言
        self.source_lang_label = ttk.Label(self.config_frame, text=self.text_manager.get("source_language"))
        self.source_lang_label.grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.source_lang_combo = ttk.Combobox(self.config_frame, values=["zh", "en", "ja", "ko", "fr", "de", "es", "ru"], width=10)
        self.source_lang_combo.grid(row=0, column=1, sticky="w")
        
        # 目标语言
        self.target_lang_label = ttk.Label(self.config_frame, text=self.text_manager.get("target_languages"))
        self.target_lang_label.grid(row=1, column=0, sticky="w", padx=(0, 5))
        self.target_lang_vars = {}
        
        for i, lang in enumerate(["en", "ja", "ko", "fr", "de", "es", "ru"]):
            var = tk.BooleanVar()
            self.target_lang_vars[lang] = var
            cb = ttk.Checkbutton(self.config_frame, text=lang, variable=var)
            cb.grid(row=1 + i//4, column=2 + i%4, sticky="w", padx=(5, 5))
        
        # 音频设备选择
        self.microphone_label = ttk.Label(self.config_frame, text=self.text_manager.get("microphone_device"))
        self.microphone_label.grid(row=3, column=0, sticky="w", padx=(0, 5))
        self.audio_device_combo = ttk.Combobox(self.config_frame, values=self.text_manager.get("device_options"), width=20)
        self.audio_device_combo.grid(row=3, column=1, sticky="w")
        
        # 语音识别模型大小
        self.whisper_label = ttk.Label(self.config_frame, text=self.text_manager.get("whisper_model"))
        self.whisper_label.grid(row=4, column=0, sticky="w", padx=(0, 5))
        self.whisper_model_combo = ttk.Combobox(self.config_frame, values=["tiny", "base", "small", "medium", "large-v3", "large-v3-turbo"], width=15)
        self.whisper_model_combo.grid(row=4, column=1, sticky="w")
        
        # API配置
        self.api_url_label = ttk.Label(self.config_frame, text=self.text_manager.get("api_url"))
        self.api_url_label.grid(row=5, column=0, sticky="w", padx=(0, 5))
        self.api_base_url_entry = ttk.Entry(self.config_frame, width=30)
        self.api_base_url_entry.grid(row=5, column=1, columnspan=3, sticky="w")
        
        self.api_key_label = ttk.Label(self.config_frame, text=self.text_manager.get("api_key"))
        self.api_key_label.grid(row=6, column=0, sticky="w", padx=(0, 5))
        self.api_key_entry = ttk.Entry(self.config_frame, width=30, show="*")
        self.api_key_entry.grid(row=6, column=1, columnspan=3, sticky="w")
        self.api_model_label = ttk.Label(self.config_frame, text=self.text_manager.get("api_model"))
        self.api_model_label.grid(row=7, column=0, sticky="w", padx=(0, 5))
        self.api_model_entry = ttk.Entry(self.config_frame, width=30)
        self.api_model_entry.grid(row=7, column=1, columnspan=3, sticky="w")
        
        # OSC配置
        self.osc_address_label = ttk.Label(self.config_frame, text=self.text_manager.get("osc_address"))
        self.osc_address_label.grid(row=8, column=0, sticky="w", padx=(0, 5))
        self.osc_ip_entry = ttk.Entry(self.config_frame, width=15)
        self.osc_ip_entry.grid(row=8, column=1, sticky="w")
        
        self.osc_port_label = ttk.Label(self.config_frame, text=self.text_manager.get("osc_port"))
        self.osc_port_label.grid(row=8, column=2, sticky="w", padx=(10, 5))
        self.osc_port_entry = ttk.Entry(self.config_frame, width=8)
        self.osc_port_entry.grid(row=8, column=3, sticky="w")
        
        # 快捷键配置
        self.hotkey_label = ttk.Label(self.config_frame, text=self.text_manager.get("hotkey"))
        self.hotkey_label.grid(row=9, column=0, sticky="w", padx=(0, 5))
        self.hotkey_entry = ttk.Entry(self.config_frame, width=5)
        self.hotkey_entry.grid(row=9, column=1, sticky="w")
        
        # 音频参数
        self.audio_chunk_label = ttk.Label(self.config_frame, text=self.text_manager.get("audio_chunk"))
        self.audio_chunk_label.grid(row=10, column=0, sticky="w", padx=(0, 5))
        self.audio_chunk_entry = ttk.Entry(self.config_frame, width=10)
        self.audio_chunk_entry.grid(row=10, column=1, sticky="w")
        
        self.audio_rate_label = ttk.Label(self.config_frame, text=self.text_manager.get("audio_rate"))
        self.audio_rate_label.grid(row=10, column=2, sticky="w", padx=(10, 5))
        self.audio_rate_entry = ttk.Entry(self.config_frame, width=10)
        self.audio_rate_entry.grid(row=10, column=3, sticky="w")
        
        self.audio_channels_label = ttk.Label(self.config_frame, text=self.text_manager.get("audio_channels"))
        self.audio_channels_label.grid(row=11, column=0, sticky="w", padx=(0, 5))
        self.audio_channels_entry = ttk.Entry(self.config_frame, width=10)
        self.audio_channels_entry.grid(row=11, column=1, sticky="w")
        
        # 日志级别
        self.log_level_label = ttk.Label(self.config_frame, text=self.text_manager.get("log_level"))
        self.log_level_label.grid(row=11, column=2, sticky="w", padx=(10, 5))
        self.log_level_combo = ttk.Combobox(self.config_frame, values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], width=10)
        self.log_level_combo.grid(row=11, column=3, sticky="w")
        
        # 按钮区域
        button_frame = ttk.Frame(self.config_frame)
        button_frame.grid(row=12, column=0, columnspan=4, pady=(10, 0))
        
        self.save_button = ttk.Button(button_frame, text=self.text_manager.get("save_config"), command=self.save_config)
        self.save_button.pack(side="left", padx=(0, 10))
        
        self.reload_button = ttk.Button(button_frame, text=self.text_manager.get("reload_config"), command=self.load_current_config)
        self.reload_button.pack(side="left", padx=(0, 10))
        
        self.reset_button = ttk.Button(button_frame, text=self.text_manager.get("reset_default"), command=self.reset_default)
        self.reset_button.pack(side="left")
        
    def setup_log_section(self, parent):
        """设置日志显示区域"""
        self.log_frame = ttk.LabelFrame(parent, text=self.text_manager.get("log_frame"), padding="10")
        self.log_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(self.log_frame, height=8, wrap="word")
        self.log_text.pack(fill="both", expand=True)
        
        # 清空日志按钮
        self.clear_logs_button = ttk.Button(self.log_frame, text=self.text_manager.get("clear_logs"), command=self.clear_logs)
        self.clear_logs_button.pack(pady=(5, 0))
        
    def load_current_config(self):
        """加载当前配置到界面"""
        try:
            # 重新加载配置
            self.config_manager.load_config()
            
            # 源语言
            self.source_lang_combo.set(self.config_manager.get("SOURCE_LANGUAGE", "zh"))
            
            # 目标语言
            target_langs = self.config_manager.get("TARGET_LANGUAGES", "en,ja,ko").split(",")
            for lang, var in self.target_lang_vars.items():
                var.set(lang in target_langs)
            
            # 音频设备
            default_device_index = self.config_manager.get("AUDIO_DEVICE_INDEX", "0")
            device_options = self.text_manager.get("device_options")
            if default_device_index and default_device_index.isdigit():
                device_index = int(default_device_index)
                if device_index < len(device_options):
                    self.audio_device_combo.set(device_options[device_index])
                else:
                    self.audio_device_combo.set(f"{default_device_index}: Device {default_device_index}")
            else:
                self.audio_device_combo.set(device_options[0])
            
            # Whisper模型
            self.whisper_model_combo.set(self.config_manager.get("WHISPER_MODEL", "large-v3-turbo"))
            
            # API配置
            self.api_base_url_entry.delete(0, "end")
            self.api_base_url_entry.insert(0, self.config_manager.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"))
            
            self.api_key_entry.delete(0, "end")
            self.api_key_entry.insert(0, self.config_manager.get("DEEPSEEK_API_KEY", ""))
            
            self.api_model_entry.delete(0, "end")
            self.api_model_entry.insert(0, self.config_manager.get("DEEPSEEK_MODEL", "deepseek-chat"))
            
            # OSC配置
            self.osc_ip_entry.delete(0, "end")
            self.osc_ip_entry.insert(0, self.config_manager.get("OSC_IP", "127.0.0.1"))
            
            self.osc_port_entry.delete(0, "end")
            self.osc_port_entry.insert(0, self.config_manager.get("OSC_PORT", "9000"))
            
            # 快捷键
            self.hotkey_entry.delete(0, "end")
            self.hotkey_entry.insert(0, self.config_manager.get("HOTKEY", "k"))
            
            # 音频参数
            self.audio_chunk_entry.delete(0, "end")
            self.audio_chunk_entry.insert(0, self.config_manager.get("AUDIO_CHUNK", "1024"))
            
            self.audio_rate_entry.delete(0, "end")
            self.audio_rate_entry.insert(0, self.config_manager.get("AUDIO_RATE", "16000"))
            
            self.audio_channels_entry.delete(0, "end")
            self.audio_channels_entry.insert(0, self.config_manager.get("AUDIO_CHANNELS", "1"))
            
            # 日志级别
            self.log_level_combo.set(self.config_manager.get("LOG_LEVEL", "INFO"))
            
            self.log_message(self.text_manager.get("config_loaded"))
            
        except Exception as e:
            self.log_message(f"加载配置失败: {e}")
            messagebox.showerror(self.text_manager.get("error"), f"加载配置失败: {e}")
    
    def save_config(self):
        """保存配置到.env文件"""
        try:
            # 提取音频设备索引
            audio_device_index = None
            device_str = self.audio_device_combo.get()
            if device_str and ':' in device_str:
                audio_device_index = device_str.split(':')[0].strip()
            
            # 更新配置管理器
            self.config_manager.set("SOURCE_LANGUAGE", self.source_lang_combo.get())
            self.config_manager.set("TARGET_LANGUAGES", ",".join([lang for lang, var in self.target_lang_vars.items() if var.get()]))
            self.config_manager.set("WHISPER_MODEL", self.whisper_model_combo.get())
            self.config_manager.set("DEEPSEEK_BASE_URL", self.api_base_url_entry.get())
            self.config_manager.set("DEEPSEEK_API_KEY", self.api_key_entry.get())
            self.config_manager.set("DEEPSEEK_MODEL", self.api_model_entry.get())
            self.config_manager.set("OSC_IP", self.osc_ip_entry.get())
            self.config_manager.set("OSC_PORT", self.osc_port_entry.get())
            self.config_manager.set("HOTKEY", self.hotkey_entry.get())
            self.config_manager.set("AUDIO_CHUNK", self.audio_chunk_entry.get())
            self.config_manager.set("AUDIO_RATE", self.audio_rate_entry.get())
            self.config_manager.set("AUDIO_CHANNELS", self.audio_channels_entry.get())
            self.config_manager.set("LOG_LEVEL", self.log_level_combo.get())
            
            # 添加音频设备配置
            if audio_device_index:
                self.config_manager.set("AUDIO_DEVICE_INDEX", audio_device_index)
            
            # 保存配置
            if self.config_manager.save_config():
                self.log_message(self.text_manager.get("config_saved"))
                messagebox.showinfo(self.text_manager.get("success"), self.text_manager.get("config_saved"))
            else:
                self.log_message(self.text_manager.get("config_save_failed"))
                messagebox.showerror(self.text_manager.get("error"), self.text_manager.get("config_save_failed"))
                
        except Exception as e:
            self.log_message(f"保存配置失败: {e}")
            messagebox.showerror(self.text_manager.get("error"), f"保存配置失败: {e}")
    
    def reset_default(self):
        """重置为默认配置"""
        try:
            result = messagebox.askyesno(self.text_manager.get("confirm"), self.text_manager.get("reset_confirm"))
            if result:
                self.config_manager.create_default_config()
                self.load_current_config()
                self.log_message(self.text_manager.get("default_reset"))
        except Exception as e:
            self.log_message(f"重置配置失败: {e}")
            messagebox.showerror(self.text_manager.get("error"), f"重置配置失败: {e}")
    
    def clear_logs(self):
        """清空日志"""
        self.log_text.delete(1.0, "end")
    
    def log_message(self, message):
        """添加日志消息"""
        self.log_text.insert("end", f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.log_text.see("end")
    
    def run(self):
        """运行界面"""
        self.root.mainloop()

def main():
    """主函数"""
    try:
        app = ConfigGUI()
        app.run()
        
    except Exception as e:
        messagebox.showerror("错误", f"启动配置界面失败: {e}")

if __name__ == "__main__":
    main()
