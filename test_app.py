#!/usr/bin/env python3
"""
测试AI数据探索器应用功能
"""

import os
import pandas as pd
from gradio_app import DataExplorer

def test_basic_functionality():
    """测试基本功能"""
    print("🧪 开始测试AI数据探索器...")
    
    # 创建探索器实例
    explorer = DataExplorer()
    
    # 测试1: 检查测试数据文件
    test_file = "test_sales_data.xlsx"
    if os.path.exists(test_file):
        print("✅ 测试数据文件存在")
        
        # 测试2: 加载Excel文件
        overview, preview = explorer.load_excel(test_file)
        if "数据概览" in overview and preview:
            print("✅ Excel文件加载成功")
            print(f"📊 数据行数: {explorer.df.shape[0]}")
            print(f"📊 数据列数: {explorer.df.shape[1]}")
        else:
            print("❌ Excel文件加载失败")
            return False
        
        # 测试3: 检查API密钥
        from gradio_app import DEEPSEEK_API_KEY
        if DEEPSEEK_API_KEY and DEEPSEEK_API_KEY != "your-api-key-here":
            print("✅ Deepseek API密钥已配置")
        else:
            print("⚠️ Deepseek API密钥未配置")
        
        # 测试4: 简单数据分析
        test_query = "显示数据的基本信息"
        try:
            history = []
            result, chart = explorer.analyze_data(test_query, history)
            if result and len(result) > 0:
                print("✅ AI分析功能正常")
            else:
                print("❌ AI分析功能异常")
        except Exception as e:
            print(f"⚠️ AI分析测试失败: {e}")
        
    else:
        print("❌ 测试数据文件不存在，请先运行: python create_test_data.py")
        return False
    
    print("\n🎉 基本功能测试完成!")
    print("🚀 启动应用: python start_gradio.py")
    print("🌐 访问地址: http://127.0.0.1:7860")
    
    return True

if __name__ == "__main__":
    test_basic_functionality()