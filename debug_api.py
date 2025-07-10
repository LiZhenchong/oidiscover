#!/usr/bin/env python3
"""
调试API调用和代码生成
"""

import os
import json
from gradio_app import DataExplorer

def debug_api_call():
    """调试API调用"""
    print("🔍 开始调试API调用...")
    
    explorer = DataExplorer()
    
    # 加载测试数据
    if os.path.exists("test_sales_data.xlsx"):
        explorer.load_excel("test_sales_data.xlsx")
        print("✅ 数据加载成功")
        
        # 准备简单的测试查询
        test_query = "显示数据的基本统计信息"
        print(f"📝 测试查询: {test_query}")
        
        # 准备数据摘要
        data_summary = {
            'columns': explorer.df.columns.tolist(),
            'shape': explorer.df.shape,
            'dtypes': explorer.df.dtypes.astype(str).to_dict(),
        }
        
        print(f"📊 数据摘要: {data_summary}")
        
        # 构建消息
        system_prompt = """你是数据分析师。分析数据并返回JSON格式:
        {
            "analysis": "分析结论",
            "code": "Python代码",
            "has_visualization": false
        }"""
        
        user_message = f"数据信息: {json.dumps(data_summary, ensure_ascii=False)}\n用户需求: {test_query}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        print("🔄 调用API...")
        response = explorer.call_deepseek_api(messages)
        
        if response:
            print(f"✅ API响应成功")
            print(f"📝 响应内容 (前200字符): {response[:200]}...")
            
            # 尝试解析JSON
            try:
                if '```json' in response:
                    json_start = response.find('```json') + 7
                    json_end = response.find('```', json_start)
                    if json_end != -1:
                        json_content = response[json_start:json_end].strip()
                    else:
                        json_content = response
                else:
                    json_content = response
                
                result = json.loads(json_content)
                print(f"✅ JSON解析成功")
                print(f"📊 分析: {result.get('analysis', 'N/A')[:100]}...")
                print(f"💻 代码: {result.get('code', 'N/A')[:100]}...")
                
            except Exception as e:
                print(f"❌ JSON解析失败: {e}")
                print(f"📝 原始响应: {response}")
        else:
            print("❌ API调用失败")
    else:
        print("❌ 测试数据文件不存在")

if __name__ == "__main__":
    debug_api_call()