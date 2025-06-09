#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 Addy 语音助手的工具系统
这个脚本用于验证各种工具是否正常工作
"""

import sys
import os
import configparser
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from addy_core.tools.tool_manager import ToolManager
from addy_core.nlp_module import NLPModule
from addy_core.task_executor import TaskExecutor

def setup_logging():
    """设置日志记录"""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('test_tools.log', encoding='utf-8')
        ]
    )

def create_test_config():
    """创建测试配置"""
    config = configparser.ConfigParser()
    
    # 基本配置
    config['Tools'] = {
        'enabled_tools': 'file_tool,system_tool,calculator_tool',
        'log_level': 'INFO'
    }
    
    config['FileTool'] = {
        'default_directory': str(Path.home() / 'Documents'),
        'max_file_size': '10'
    }
    
    config['SystemTool'] = {
        'allow_shutdown': 'false',
        'allow_process_management': 'true'
    }
    
    config['CalculatorTool'] = {
        'precision': '10',
        'enable_scientific': 'true'
    }
    
    config['Paths'] = {
        'data_dir': 'data',
        'screenshots_dir': 'screenshots'
    }
    
    return config

def test_speak(text):
    """测试用的语音输出函数"""
    print(f"[Addy]: {text}")

def test_tool_manager():
    """测试工具管理器"""
    print("\n=== 测试工具管理器 ===")
    
    config = create_test_config()
    tool_manager = ToolManager(config=config, speak_func=test_speak)
    
    # 测试工具注册
    available_tools = tool_manager.get_available_tools()
    registered_tool_names = [tool_info['name'] for tool_info in available_tools]
    print(f"已注册的工具: {registered_tool_names}")
    
    # 测试支持的意图
    supported_intents = tool_manager.get_supported_intents()
    print(f"支持的意图数量: {len(supported_intents)}")
    print(f"部分支持的意图: {list(supported_intents)[:10]}")
    
    return tool_manager

def test_nlp_module():
    """测试NLP模块"""
    print("\n=== 测试NLP模块 ===")
    
    nlp = NLPModule(nlp_engine='rule_based')
    
    # 测试各种意图识别
    test_inputs = [
        "计算 2 + 3 * 4",
        "获取系统信息",
        "创建文件 test.txt",
        "查看CPU使用率",
        "转换 100 米到公里",
        "列出所有进程",
        "搜索文件 *.py",
        "获取当前音量"
    ]
    
    for text in test_inputs:
        result = nlp.parse_intent(text)
        print(f"输入: '{text}' -> 意图: {result['intent']}, 实体: {result['entities']}")
    
    return nlp

def test_task_executor():
    """测试任务执行器"""
    print("\n=== 测试任务执行器 ===")
    
    config = create_test_config()
    executor = TaskExecutor(config=config, tts_engine_speak_func=test_speak)
    
    # 测试一些安全的任务
    test_intents = [
        {
            'intent': 'calculate',
            'entities': {'expression': '2 + 3 * 4'},
            'original_text': '计算 2 + 3 * 4'
        },
        {
            'intent': 'get_system_info',
            'entities': {},
            'original_text': '获取系统信息'
        },
        {
            'intent': 'get_cpu_usage',
            'entities': {},
            'original_text': '查看CPU使用率'
        },
        {
            'intent': 'convert_unit',
            'entities': {'value': '100', 'from_unit': '米', 'to_unit': '公里'},
            'original_text': '转换 100 米到公里'
        },
        {
            'intent': 'get_volume',
            'entities': {},
            'original_text': '获取当前音量'
        }
    ]
    
    for intent_data in test_intents:
        print(f"\n执行任务: {intent_data['original_text']}")
        try:
            result = executor.execute(intent_data)
            print(f"执行结果: {result}")
        except Exception as e:
            print(f"执行错误: {e}")
    
    return executor

def test_integration():
    """集成测试"""
    print("\n=== 集成测试 ===")
    
    config = create_test_config()
    nlp = NLPModule(nlp_engine='rule_based')
    executor = TaskExecutor(config=config, tts_engine_speak_func=test_speak)
    
    # 端到端测试
    test_commands = [
        "计算 10 + 20",
        "获取系统信息",
        "查看内存使用率",
        "转换 1000 克到公斤"
    ]
    
    for command in test_commands:
        print(f"\n处理命令: '{command}'")
        try:
            # NLP解析
            intent_data = nlp.parse_intent(command)
            print(f"解析结果: {intent_data}")
            
            # 任务执行
            result = executor.execute(intent_data)
            print(f"执行结果: {result}")
        except Exception as e:
            print(f"处理错误: {e}")

def main():
    """主函数"""
    print("Addy 工具系统测试")
    print("=" * 50)
    
    # 设置日志
    setup_logging()
    
    try:
        # 创建必要的目录
        os.makedirs('data', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        os.makedirs('screenshots', exist_ok=True)
        
        # 运行测试
        test_tool_manager()
        test_nlp_module()
        test_task_executor()
        test_integration()
        
        print("\n=== 测试完成 ===")
        print("所有测试已完成，请查看输出结果和日志文件。")
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()