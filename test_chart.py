#!/usr/bin/env python3
"""
测试图表生成功能
"""

import os
from gradio_app import DataExplorer

def test_chart_generation():
    """测试图表生成是否正常"""
    print("🧪 测试图表生成功能...")
    
    explorer = DataExplorer()
    
    # 加载测试数据
    if os.path.exists("test_sales_data.xlsx"):
        overview, preview = explorer.load_excel("test_sales_data.xlsx")
        print("✅ 数据加载成功")
        
        # 测试图表生成
        test_query = "生成销售额的月度趋势图"
        print(f"🔍 测试查询: {test_query}")
        
        try:
            history = []
            result, chart_path = explorer.analyze_data(test_query, history)
            
            print(f"📊 返回结果: {len(result)} 条消息")
            print(f"🖼️ 图表路径: {chart_path}")
            
            if chart_path and os.path.isfile(chart_path):
                print("✅ 图表生成成功！")
                print(f"📁 图表文件: {chart_path}")
            else:
                print("⚠️ 图表未生成或路径无效")
                
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ 测试数据文件不存在")

if __name__ == "__main__":
    test_chart_generation()