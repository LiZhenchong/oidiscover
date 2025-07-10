import os
import json
import io
from typing import List, Tuple, Optional

# 设置环境变量以避免代理问题
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('https_proxy', None)
os.environ.pop('http_proxy', None)
os.environ.pop('all_proxy', None)
os.environ.pop('ALL_PROXY', None)

import gradio as gr
import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv

# 尝试导入E2B，如果失败则跳过
try:
    from e2b import Sandbox
    E2B_AVAILABLE = True
except ImportError:
    E2B_AVAILABLE = False
    print("⚠️ E2B未安装，将使用本地代码执行")

# Load environment variables
load_dotenv()

# Configuration
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-5b8931fa8b954025a3443faa16867476")
E2B_API_KEY = os.getenv("E2B_API_KEY", "e2b_57ae96f0d05b0238e0c3c50c144df93f8347ac53")  # 需要设置E2B API密钥
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

class DataExplorer:
    def __init__(self):
        self.df = None
        self.conversation_history = []
        self.sandbox = None

    def load_excel(self, file_path) -> Tuple[str, str]:
        """加载Excel文件"""
        try:
            if file_path is None:
                return "请先上传Excel文件", ""

            # 检查是否为有效文件路径
            if isinstance(file_path, str):
                if not os.path.isfile(file_path):
                    return "上传的不是有效的文件", ""
                actual_path = file_path
            else:
                # 如果是Gradio的文件对象
                actual_path = file_path.name if hasattr(file_path, 'name') else str(file_path)

            # 检查文件扩展名
            if not actual_path.lower().endswith(('.xlsx', '.xls')):
                return "请上传Excel文件（.xlsx或.xls格式）", ""

            # 读取Excel文件
            self.df = pd.read_excel(actual_path)

            if self.df.empty:
                return "Excel文件为空", ""

            # 数据清理
            self.df = self._clean_dataframe(self.df)

            # 生成数据概览
            overview = self._generate_data_overview()

            # 显示前几行数据
            preview = self.df.head().to_html(classes='table table-striped', escape=False)

            return overview, preview

        except Exception as e:
            return f"加载文件失败: {str(e)}", ""

    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """清理数据框"""
        # 清理列名
        df.columns = [str(col).strip() for col in df.columns]

        # 处理缺失值和数据类型
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].fillna('').astype(str)
            else:
                df[col] = df[col].fillna(0)

        return df

    def _generate_data_overview(self) -> str:
        """生成数据概览"""
        if self.df is None:
            return "没有加载数据"

        overview = f"""
        📊 **数据概览**

        - 数据行数: {self.df.shape[0]:,}
        - 数据列数: {self.df.shape[1]}
        - 列名: {', '.join(self.df.columns.tolist())}

        📋 **数据类型**
        """

        for col in self.df.columns:
            non_null_count = self.df[col].count()
            overview += f"\n- {col}: {self.df[col].dtype} ({non_null_count:,} 非空值)"

        return overview

    def call_deepseek_api(self, messages: List[dict]) -> Optional[str]:
        """调用Deepseek API"""
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": 0.1
        }

        try:
            response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']
        except Exception as e:
            return f"API调用失败: {str(e)}"

    def analyze_data(self, user_query: str, history) -> Tuple[list, str]:
        """分析数据并生成回答"""
        if self.df is None:
            new_message = {"role": "assistant", "content": "❌ 请先上传Excel文件"}
            return history + [{"role": "user", "content": user_query}, new_message], None

        # 准备数据摘要
        data_summary = {
            'columns': self.df.columns.tolist(),
            'shape': self.df.shape,
            'dtypes': self.df.dtypes.astype(str).to_dict(),
            'sample_data': self.df.head(3).to_dict(),
            'description': self.df.describe().to_dict() if self.df.select_dtypes(include=['number']).shape[1] > 0 else {}
        }

        # 构建提示词
        system_prompt = """你是一个专业的数据分析师。根据用户的需求分析Excel数据，并生成相应的Python代码。

要求：
1. 仔细分析用户的需求
2. 生成清晰、准确的分析结论
3. 如果需要生成图表，请使用matplotlib和seaborn
4. 代码中使用变量名 'df' 来引用数据
5. 如果生成图表，必须在代码最后加上：plt.savefig('chart.png', dpi=150, bbox_inches='tight')
6. 设置图表标题和标签为中文
7. 确保代码可以直接执行，处理可能的数据类型问题

返回格式：
```json
{
    "analysis": "你的分析结论",
    "code": "生成的Python代码",
    "has_visualization": true/false
}
```

示例代码结构：
```python
import matplotlib.pyplot as plt
import pandas as pd

# 数据分析代码
result = df.describe()
print(result)

# 如果需要图表
plt.figure(figsize=(10, 6))
# 绘图代码
plt.title('图表标题')
plt.xlabel('X轴标签')
plt.ylabel('Y轴标签')
plt.savefig('chart.png', dpi=150, bbox_inches='tight')
```"""

        user_message = f"""
数据信息：
{json.dumps(data_summary, ensure_ascii=False, indent=2)}

用户需求：{user_query}

请分析数据并提供解答。
"""

        # 构建对话历史
        messages = [{"role": "system", "content": system_prompt}]

        # 添加最近的对话历史
        for msg in history[-6:]:  # 只保留最近3轮对话(用户+助手)
            if isinstance(msg, dict) and "role" in msg:
                messages.append(msg)

        messages.append({"role": "user", "content": user_message})

        # 调用API
        response = self.call_deepseek_api(messages)

        if not response or "API调用失败" in response:
            error_msg = {"role": "assistant", "content": f"❌ {response}"}
            return history + [{"role": "user", "content": user_query}, error_msg], None

        try:
            # 提取JSON内容
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

            analysis = result.get("analysis", "")
            code = result.get("code", "")

            # 执行代码并获取结果
            print(f"🔍 Debug: 准备执行代码 - 长度: {len(code) if code else 0}")
            execution_result, chart_path = self._execute_code_in_sandbox(code)
            print(f"🔍 Debug: 执行结果 - 输出: {execution_result[:100] if execution_result else 'None'}")
            print(f"🔍 Debug: 图表路径: {chart_path}")

            # 构建回答
            answer = f"📊 **分析结果**\n\n{analysis}"

            if execution_result:
                answer += f"\n\n💻 **执行结果**\n```\n{execution_result}\n```"

            if code:
                answer += f"\n\n🔍 **生成的代码**\n```python\n{code}\n```"

            assistant_msg = {"role": "assistant", "content": answer}
            # 确保chart_path是有效的文件路径或None
            valid_chart_path = None
            if chart_path and os.path.isfile(chart_path):
                valid_chart_path = chart_path
            
            return history + [{"role": "user", "content": user_query}, assistant_msg], valid_chart_path

        except Exception as e:
            error_msg = f"❌ 处理响应失败: {str(e)}\n\n原始响应:\n{response}"
            error_response = {"role": "assistant", "content": error_msg}
            return history + [{"role": "user", "content": user_query}, error_response], None

    def _execute_code_in_sandbox(self, code: str) -> Tuple[str, Optional[str]]:
        """在E2B沙箱中执行代码"""
        if not code.strip():
            return "", None

        try:
            # 如果没有E2B或API密钥，使用本地执行
            if not E2B_AVAILABLE or not E2B_API_KEY:
                return self._execute_code_locally(code)

            # 尝试使用E2B沙箱执行
            with Sandbox() as sandbox:
                # 上传数据到沙箱
                df_csv = self.df.to_csv(index=False)
                sandbox.filesystem.write("data.csv", df_csv)

                # 准备执行代码
                full_code = f"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 读取数据
df = pd.read_csv('data.csv')

{code}
"""

                # 执行代码
                result = sandbox.run_code(full_code)

                output = ""
                if result.stdout:
                    output += result.stdout
                if result.stderr:
                    output += f"错误: {result.stderr}"

                # 检查是否生成了图片
                chart_path = None
                if sandbox.filesystem.exists("chart.png"):
                    chart_content = sandbox.filesystem.read("chart.png")
                    chart_path = "temp_chart.png"
                    with open(chart_path, "wb") as f:
                        f.write(chart_content)

                return output, chart_path

        except Exception as e:
            # 如果E2B执行失败，尝试本地执行
            print(f"⚠️ E2B执行失败，尝试本地执行: {str(e)}")
            return self._execute_code_locally(code)

    def _execute_code_locally(self, code: str) -> Tuple[str, Optional[str]]:
        """本地执行代码（备用方案）"""
        try:
            # 设置matplotlib后端
            import matplotlib
            matplotlib.use('Agg')

            # 准备执行环境
            local_vars = {
                'df': self.df.copy(),
                'pd': pd,
                'plt': plt,
                'sns': sns
            }

            # 捕获输出
            output_buffer = io.StringIO()

            # 重定向print输出
            import sys
            old_stdout = sys.stdout
            sys.stdout = output_buffer

            try:
                # 执行代码
                exec(code, globals(), local_vars)

                # 恢复stdout
                sys.stdout = old_stdout

                output = output_buffer.getvalue()

                # 检查是否生成了图片
                chart_path = None
                if os.path.exists("chart.png") and os.path.isfile("chart.png"):
                    chart_path = os.path.abspath("chart.png")

                return output, chart_path

            except Exception as e:
                sys.stdout = old_stdout
                return f"执行错误: {str(e)}", None

        except Exception as e:
            return f"本地执行失败: {str(e)}", None

# 创建应用实例
explorer = DataExplorer()

def create_interface():
    """创建Gradio界面"""

    with gr.Blocks(title="AI数据探索器", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 🤖 AI数据探索器")
        gr.Markdown("上传Excel文件，然后输入你的数据分析需求，AI将为你生成图表和解答！")

        with gr.Row():
            with gr.Column(scale=1):
                # 文件上传区域
                file_upload = gr.File(
                    label="📁 上传Excel文件",
                    file_types=[".xlsx", ".xls"],
                    type="filepath"
                )

                # 数据概览
                data_overview = gr.Markdown(label="📊 数据概览")

                # 数据预览
                data_preview = gr.HTML(label="👀 数据预览")

            with gr.Column(scale=2):
                # 对话界面
                chatbot = gr.Chatbot(
                    label="💬 AI对话",
                    height=400,
                    show_label=True,
                    type="messages"
                )

                # 用户输入
                user_input = gr.Textbox(
                    label="💭 输入你的数据探索需求",
                    placeholder="例如：帮我分析销售趋势，生成一个折线图",
                    lines=2
                )

                with gr.Row():
                    submit_btn = gr.Button("🚀 分析", variant="primary")
                    clear_btn = gr.Button("🗑️ 清空对话")

                # 图表显示
                chart_output = gr.Image(
                    label="📈 生成的图表",
                    show_label=True
                )

        # 示例问题
        gr.Markdown("### 💡 示例问题")
        example_questions = [
            "分析数据的基本统计信息",
            "生成销售额的趋势图",
            "显示各类别的分布情况",
            "找出数据中的异常值",
            "创建相关性分析热力图"
        ]

        with gr.Row():
            for question in example_questions:
                gr.Button(question, size="sm").click(
                    fn=lambda q=question: q,
                    outputs=user_input
                )

        # 事件处理
        file_upload.change(
            fn=explorer.load_excel,
            inputs=[file_upload],
            outputs=[data_overview, data_preview]
        )

        submit_btn.click(
            fn=explorer.analyze_data,
            inputs=[user_input, chatbot],
            outputs=[chatbot, chart_output]
        ).then(
            fn=lambda: "",  # 清空输入框
            outputs=user_input
        )

        user_input.submit(
            fn=explorer.analyze_data,
            inputs=[user_input, chatbot],
            outputs=[chatbot, chart_output]
        ).then(
            fn=lambda: "",  # 清空输入框
            outputs=user_input
        )

        clear_btn.click(
            fn=lambda: ([], ""),
            outputs=[chatbot, chart_output]
        )

    return demo

if __name__ == "__main__":
    # 检查环境变量
    if not E2B_API_KEY:
        print("⚠️  警告: 未设置E2B_API_KEY环境变量，将使用本地代码执行（功能受限）")
        print("请在 .env 文件中设置: E2B_API_KEY=your_api_key")

    # 启动应用
    demo = create_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )