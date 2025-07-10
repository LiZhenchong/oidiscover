#!/usr/bin/env python3
"""
AI数据探索器 - Gradio版本启动脚本
"""

import os
import sys
from pathlib import Path

def setup_environment():
    """设置环境"""
    # 添加当前目录到Python路径
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    # 检查.env文件
    env_file = current_dir / ".env"
    env_example = current_dir / ".env.example"
    
    if not env_file.exists() and env_example.exists():
        print("🔧 检测到 .env 文件不存在，正在创建...")
        env_example.rename(env_file)
        print("✅ 已创建 .env 文件，请编辑并添加你的API密钥")
        print(f"📝 编辑文件: {env_file}")
        return False
    
    return True

def check_dependencies():
    """检查依赖"""
    required_packages = [
        "gradio", "pandas", "requests", "matplotlib", 
        "seaborn", "openpyxl", "python-dotenv"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ 缺少以下依赖包:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n🔧 请运行以下命令安装依赖:")
        print("   pip install -e .")
        print("   或者:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True

def main():
    """主函数"""
    print("🚀 启动 AI数据探索器 (Gradio版本)")
    print("=" * 50)
    
    # 设置环境
    if not setup_environment():
        return
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 导入并启动应用
    try:
        from gradio_app import create_interface
        
        print("✅ 正在启动Gradio应用...")
        demo = create_interface()
        
        print("🌐 应用已启动!")
        print("📱 本地访问: http://localhost:7860")
        print("⏹️  按 Ctrl+C 停止应用")
        print("=" * 50)
        
        demo.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            show_error=True
        )
        
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()