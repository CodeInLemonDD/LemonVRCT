#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VRChat Voice Translation Software Launcher
VRChat语音翻译软件启动器
Directly launches the main program and provides configuration interface options
直接启动主程序并提供配置界面选项
"""

import os
import sys
import threading
import time

def main():
    """主启动函数 / Main launcher function"""
    print("=" * 50)
    print("VRChat Voice Translation Software")
    print("VRChat语音翻译软件")
    print("=" * 50)
    
    # 显示菜单
    show_menu()

def show_menu():
    """显示菜单 / Show menu"""
    while True:
        print("\n" + "=" * 30)
        print("Control Menu / 控制菜单")
        print("=" * 30)
        print("1. Start Main Program / 启动主程序")
        print("2. Open Configuration Interface / 打开配置界面")
        print("3. Exit / 退出")
        
        try:
            choice = input("\nPlease enter your choice (1-3): / 请输入选择 (1-3): ").strip()
            
            if choice == "1":
                start_main_program()
            elif choice == "2":
                open_config_gui()
            elif choice == "3":
                print("Exiting program... / 正在退出程序...")
                time.sleep(1)
                break
            else:
                print("Invalid choice, please enter 1, 2 or 3 / 无效选择，请输入1、2或3")
                
        except (KeyboardInterrupt, EOFError):
            print("\nExiting program / 退出程序")
            break

def start_main_program():
    """启动主程序 / Start main program"""
    print("Starting main program... / 正在启动主程序...")
    try:
        # 直接导入并运行主程序
        import vrchat_translator
        translator = vrchat_translator.VRChatTranslator()
        
        # 在新线程中运行主程序
        def run_translator():
            try:
                translator.run()
            except Exception as e:
                print(f"Main program error: {e} / 主程序错误: {e}")
        
        thread = threading.Thread(target=run_translator, daemon=True)
        thread.start()
        
        print("✓ Main program started / 主程序已启动")
        print("✓ Press K to start recording, release K to stop and translate / 按K键开始录音，松开K键停止并翻译")
        print("✓ Program is running in background / 程序正在后台运行")
        
    except Exception as e:
        print(f"✗ Failed to start main program: {e} / 启动主程序失败: {e}")
        print("Please ensure all dependencies are installed / 请确保已安装所有依赖包")

def open_config_gui():
    """打开配置界面 / Open configuration interface"""
    print("Opening configuration interface... / 正在打开配置界面...")
    try:
        # 直接导入并运行配置界面
        import config_gui
        config_gui.main()
        
    except Exception as e:
        print(f"✗ Failed to open configuration interface: {e} / 打开配置界面失败: {e}")
        print("Please ensure all dependencies are installed / 请确保已安装所有依赖包")

if __name__ == "__main__":
    main()
