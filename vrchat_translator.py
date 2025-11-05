#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VRChat Voice Translation Software
VRChat语音翻译软件
Real-time voice recording, translation through DeepSeek to multiple languages, sending to VRChat dialog
实时录制语音，通过DeepSeek翻译成多国语言，发送到VRChat对话框
"""

import pyaudio
import threading
import time
import os
import sys
import io
import numpy as np
import json
import asyncio
from pynput import keyboard
from pynput.keyboard import Key, Listener
import logging
from dotenv import load_dotenv
import whisper
import torch
from pythonosc import udp_client
from openai import OpenAI
import queue
import re

# 设置系统编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 加载环境变量
load_dotenv()

class VRChatTranslator:
    def __init__(self):
        # 音频参数
        self.CHUNK = int(os.getenv("AUDIO_CHUNK", "1024"))
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = int(os.getenv("AUDIO_CHANNELS", "1"))
        self.RATE = int(os.getenv("AUDIO_RATE", "16000"))
        
        # 录音状态
        self.is_recording = False
        self.audio_data = None
        self.audio = None
        self.stream = None
        
        # Whisper模型
        self.model = None
        self.model_size = os.getenv("WHISPER_MODEL", "large-v3-turbo")
        
        # 翻译设置
        self.source_language = os.getenv("SOURCE_LANGUAGE", "zh")
        self.target_languages = os.getenv("TARGET_LANGUAGES", "en,ja,ko").split(",")
        
        # OpenAI客户端 (用于DeepSeek)
        self.openai_client = None
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.model_name = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        self.base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        
        # OSC客户端
        self.osc_client = None
        self.osc_ip = os.getenv("OSC_IP", "127.0.0.1")
        self.osc_port = int(os.getenv("OSC_PORT", "9000"))
        
        # 快捷键状态
        self.hotkey_pressed = False
        self.hotkey_char = os.getenv("HOTKEY", "k").lower()
        
        # 翻译队列
        self.translation_queue = queue.Queue()
        self.is_translating = False
        
        # 初始化日志
        self.setup_logging()
        
        # 初始化各个模块
        self.setup_audio()
        self.load_model()
        self.setup_openai_client()
        self.setup_osc_client()
        
        # 启动翻译队列处理线程
        self.start_translation_worker()
        
    def setup_logging(self):
        """设置日志"""
        log_level = os.getenv("LOG_LEVEL", "INFO")
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('vrchat_translator.log', encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_audio(self):
        """初始化音频设备"""
        try:
            self.audio = pyaudio.PyAudio()
            
            # 获取可用的音频设备信息
            self.available_devices = self.get_audio_devices()
            self.logger.info(f"找到 {len(self.available_devices)} 个音频设备")
            
            # 选择默认输入设备
            self.input_device_index = self.select_input_device()
            
            self.logger.info("音频设备初始化成功")
        except Exception as e:
            self.logger.error(f"音频设备初始化失败: {e}")
            raise
    
    def get_audio_devices(self):
        """获取可用的音频设备列表"""
        devices = []
        try:
            for i in range(self.audio.get_device_count()):
                device_info = self.audio.get_device_info_by_index(i)
                if device_info.get('maxInputChannels', 0) > 0:  # 只选择输入设备
                    devices.append({
                        'index': i,
                        'name': device_info.get('name', 'Unknown'),
                        'maxInputChannels': device_info.get('maxInputChannels', 0),
                        'defaultSampleRate': device_info.get('defaultSampleRate', 0)
                    })
        except Exception as e:
            self.logger.error(f"获取音频设备列表失败: {e}")
        
        return devices
    
    def select_input_device(self):
        """选择输入设备"""
        try:
            # 优先使用环境变量指定的设备
            device_index = os.getenv("AUDIO_DEVICE_INDEX")
            if device_index:
                device_index = int(device_index)
                if 0 <= device_index < self.audio.get_device_count():
                    device_info = self.audio.get_device_info_by_index(device_index)
                    if device_info.get('maxInputChannels', 0) > 0:
                        self.logger.info(f"使用指定设备: {device_info.get('name')} (索引: {device_index})")
                        return device_index
            
            # 如果没有指定设备，使用默认输入设备
            default_device = self.audio.get_default_input_device_info()
            self.logger.info(f"使用默认设备: {default_device.get('name')} (索引: {default_device.get('index')})")
            return default_device.get('index')
            
        except Exception as e:
            self.logger.error(f"选择输入设备失败: {e}")
            # 如果选择失败，使用第一个可用的输入设备
            if self.available_devices:
                self.logger.info(f"使用第一个可用设备: {self.available_devices[0]['name']}")
                return self.available_devices[0]['index']
            else:
                self.logger.error("没有可用的输入设备")
                raise
    
    def load_model(self):
        """加载Whisper模型"""
        try:
            self.logger.info(f"正在加载Whisper模型: {self.model_size}")
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.logger.info(f"使用设备: {device}")
            
            self.model = whisper.load_model(self.model_size, device=device)
            self.logger.info("Whisper模型加载成功")
        except Exception as e:
            self.logger.error(f"模型加载失败: {e}")
            raise
    
    def setup_openai_client(self):
        """设置OpenAI客户端（用于DeepSeek）"""
        try:
            if not self.api_key:
                raise ValueError("未设置DEEPSEEK_API_KEY环境变量")
            
            self.openai_client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            self.logger.info("OpenAI客户端初始化成功")
        except Exception as e:
            self.logger.error(f"OpenAI客户端初始化失败: {e}")
            raise
    
    def setup_osc_client(self):
        """设置OSC客户端"""
        try:
            self.osc_client = udp_client.SimpleUDPClient(self.osc_ip, self.osc_port)
            self.logger.info(f"OSC客户端初始化成功 - 目标: {self.osc_ip}:{self.osc_port}")
        except Exception as e:
            self.logger.error(f"OSC客户端初始化失败: {e}")
            raise
    
    def start_recording(self):
        """开始录音"""
        if self.is_recording:
            return
            
        try:
            self.is_recording = True
            self.audio_data = []
            
            # 打开音频流，使用选择的设备索引
            self.stream = self.audio.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                input_device_index=self.input_device_index,
                frames_per_buffer=self.CHUNK
            )
            
            device_info = self.audio.get_device_info_by_index(self.input_device_index)
            self.logger.info(f"开始录音... 使用设备: {device_info.get('name')}")
            
            # 在单独的线程中录音
            self.recording_thread = threading.Thread(target=self.record_audio)
            self.recording_thread.daemon = True
            self.recording_thread.start()
            
        except Exception as e:
            self.logger.error(f"开始录音失败: {e}")
            self.is_recording = False
    
    def record_audio(self):
        """录音线程"""
        try:
            while self.is_recording:
                data = self.stream.read(self.CHUNK, exception_on_overflow=False)
                self.audio_data.append(data)
        except Exception as e:
            self.logger.error(f"录音过程中出错: {e}")
    
    def stop_recording(self):
        """停止录音并开始处理"""
        if not self.is_recording:
            return
            
        self.is_recording = False
        
        try:
            # 停止音频流
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
            
            self.logger.info("录音停止，开始处理...")
            
            # 直接使用内存中的音频数据进行转录
            if self.audio_data:
                # 将音频数据加入翻译队列
                self.translation_queue.put(self.audio_data.copy())
                self.audio_data.clear()
            else:
                self.logger.error("没有录音数据")
                
        except Exception as e:
            self.logger.error(f"停止录音过程中出错: {e}")
    
    def transcribe_audio(self, audio_data):
        """转录音频数据并进行语义修正"""
        try:
            self.logger.info("正在转录音频...")
            
            # 将音频数据转换为numpy数组
            audio_bytes = b''.join(audio_data)
            audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
            
            # 检查音频长度
            if len(audio_np) < self.RATE * 0.5:  # 至少0.5秒
                self.logger.warning("录音时间太短，无法转录")
                return None
                
            self.logger.info(f"音频数据长度: {len(audio_np)} 样本")
            
            # 使用Whisper进行转录
            result = self.model.transcribe(
                audio_np,
                language=self.source_language,
                fp16=False  # 使用float32确保稳定性
            )
            
            original_text = result.get('text', '').strip()
            self.logger.info(f"原始转录结果: {original_text}")
            
            # 如果转录结果不为空，进行语义修正
            if original_text:
                corrected_text = self.semantic_correction(original_text)
                self.logger.info(f"语义修正后: {corrected_text}")
                return corrected_text
            else:
                return None
            
        except Exception as e:
            self.logger.error(f"转录失败: {e}")
            return None
    
    def semantic_correction(self, text):
        """使用AI进行语义修正，纠正语音识别错误"""
        try:
            if not text or len(text.strip()) < 2:  # 太短的文本不需要修正
                return text
                
            self.logger.info("正在进行语义修正...")
            
            # 构建语义修正提示
            prompt = f"""请对以下语音识别结果进行语义修正，纠正可能的识别错误，使其更符合自然语言表达。
当前语境为vrchat游戏内聊天如果该文本语义没有问题，则直接返回原文本，不做任何修改。
要求：
1. 保持原意不变
2. 修正语法错误和错别字
3. 使文本更通顺自然
4. 只返回修正后的文本，不要添加任何解释

需要修正的文本：{text}"""

            response = self.openai_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "你是一个专业的文本修正助手，专门用于纠正语音识别错误。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.1  # 使用较低的温度确保稳定性
            )
            
            corrected_text = response.choices[0].message.content.strip()
            
            # 如果修正后的文本与原始文本相同，或者修正失败，返回原始文本
            if not corrected_text or corrected_text == text:
                self.logger.info("语义修正无变化，使用原始文本")
                return text
                
            self.logger.info(f"语义修正完成: {text} -> {corrected_text}")
            return corrected_text
            
        except Exception as e:
            self.logger.error(f"语义修正失败: {e}")
            self.logger.info("语义修正失败，使用原始文本")
            return text  # 如果修正失败，返回原始文本
    
    def translate_text(self, text, target_language):
        """翻译文本到指定语言"""
        try:
            if not text:
                return ""
                
            self.logger.info(f"正在翻译到 {target_language}...")
            
            # 构建翻译提示
            prompt = f"请将以下{self.source_language}文本翻译成{target_language}，只返回翻译结果，不要添加任何解释：\n\n{text}"
            
            response = self.openai_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "你是一个专业的翻译助手。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            translated_text = response.choices[0].message.content.strip()
            self.logger.info(f"{target_language}翻译结果: {translated_text}")
            return translated_text
            
        except Exception as e:
            self.logger.error(f"翻译到 {target_language} 失败: {e}")
            return ""
    
    def process_translation_queue(self):
        """处理翻译队列"""
        while True:
            try:
                audio_data = self.translation_queue.get(timeout=1)
                if audio_data is None:  # 退出信号
                    break
                    
                self.is_translating = True
                
                # 转录音频
                original_text = self.transcribe_audio(audio_data)
                
                if original_text:
                    # 翻译到所有目标语言
                    translations = {}
                    for lang in self.target_languages:
                        translated_text = self.translate_text(original_text, lang)
                        if translated_text:
                            translations[lang] = translated_text
                    
                    # 构建输出格式
                    output_text = self.format_output(translations, original_text)
                    
                    # 发送到VRChat
                    self.send_to_vrchat(output_text)
                
                self.is_translating = False
                self.translation_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"处理翻译队列时出错: {e}")
                self.is_translating = False
    
    def format_output(self, translations, original_text):
        """格式化输出文本"""
        lines = []
        
        # 添加所有翻译结果
        for lang, text in translations.items():
            if text:  # 只添加非空文本
                lines.append(text)
        
        # 添加原始文本
        if original_text:
            lines.append(original_text)
        
        # 构建最终输出
        output = "\n".join(lines)
        self.logger.info(f"格式化输出: {output}")
        return output
    
    def send_to_vrchat(self, text):
        """发送文本到VRChat"""
        try:
            if not text:
                self.logger.warning("没有文本可发送")
                return
                
            # 发送到VRChat的聊天框
            # 格式: /chatbox/input [text, True, False]
            self.osc_client.send_message("/chatbox/input", [text, True, False])
            self.logger.info(f"已发送到VRChat: {text}")
            
        except Exception as e:
            self.logger.error(f"发送到VRChat失败: {e}")
    
    def start_translation_worker(self):
        """启动翻译工作线程"""
        self.translation_worker = threading.Thread(target=self.process_translation_queue)
        self.translation_worker.daemon = True
        self.translation_worker.start()
        self.logger.info("翻译工作线程已启动")
    
    def on_press(self, key):
        """按键按下事件"""
        try:
            # 检查快捷键
            if hasattr(key, 'char') and key.char and key.char.lower() == self.hotkey_char:
                self.hotkey_pressed = True
                if not self.is_recording and not self.is_translating:
                    self.logger.info(f"检测到 {self.hotkey_char.upper()} 键，开始录音")
                    self.start_recording()
                
        except AttributeError:
            pass
    
    def on_release(self, key):
        """按键释放事件"""
        try:
            # 检查快捷键释放
            if hasattr(key, 'char') and key.char and key.char.lower() == self.hotkey_char:
                self.hotkey_pressed = False
                if self.is_recording:
                    self.logger.info(f"{self.hotkey_char.upper()} 键释放，停止录音")
                    self.stop_recording()
                
        except AttributeError:
            pass
    
    def run(self):
        """运行程序"""
        self.logger.info("VRChat语音翻译软件启动")
        self.logger.info("配置信息:")
        self.logger.info(f"  源语言: {self.source_language}")
        self.logger.info(f"  目标语言: {', '.join(self.target_languages)}")
        self.logger.info(f"  Whisper模型: {self.model_size}")
        self.logger.info(f"  OSC目标: {self.osc_ip}:{self.osc_port}")
        self.logger.info(f"  快捷键: {self.hotkey_char.upper()}")
        self.logger.info("使用方法:")
        self.logger.info(f"  - 按下 {self.hotkey_char.upper()} 键开始录音")
        self.logger.info(f"  - 松开 {self.hotkey_char.upper()} 键停止录音并翻译")
        self.logger.info("  - 翻译结果会自动发送到VRChat对话框")
        self.logger.info("应用正在后台运行...")
        
        # 启动键盘监听
        with Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()
    
    def cleanup(self):
        """清理资源"""
        if self.audio:
            self.audio.terminate()
        # 发送退出信号到翻译队列
        self.translation_queue.put(None)

def main():
    """主函数"""
    translator = None
    try:
        translator = VRChatTranslator()
        translator.run()
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序运行出错: {e}")
    finally:
        if translator:
            translator.cleanup()

if __name__ == "__main__":
    main()