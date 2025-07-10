#!/usr/bin/env python3
"""
快速启动Gradio应用
"""

if __name__ == "__main__":
    from gradio_app import create_interface
    
    print("🚀 启动AI数据探索器...")
    demo = create_interface()
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        show_error=True,
        quiet=False
    )