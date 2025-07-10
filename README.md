# AI Data Explorer

一个基于Streamlit和Deepseek API的AI数据探索工具，可以上传数据文件并通过自然语言查询进行智能分析。

## 功能特性

- 📊 支持多种数据格式：CSV、Excel、JSON
- 🤖 基于Deepseek API的智能数据分析
- 📈 自动生成数据可视化图表
- 💬 自然语言查询界面
- 🔍 详细的数据摘要和统计信息

## 技术栈

- **前端框架**: Streamlit
- **数据处理**: Pandas
- **可视化**: Matplotlib, Seaborn
- **AI服务**: Deepseek API
- **包管理**: uv

## 安装和运行

### 前置要求

- Python 3.8+
- uv (Python包管理器)

### 安装uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# 或者使用pip
pip install uv
```

### 项目设置

1. 克隆项目
```bash
git clone <repository-url>
cd oidiscover
```

2. 使用uv创建虚拟环境并安装依赖
```bash
uv sync
```

3. 激活虚拟环境
```bash
uv shell
```

4. 运行应用
```bash
streamlit run app1.py
```

### 配置API密钥

在运行应用之前，请确保你有有效的Deepseek API密钥。当前代码中已经包含了一个示例密钥，但建议你：

1. 注册Deepseek账户获取API密钥
2. 在`app1.py`中替换API密钥

## 使用方法

1. 启动应用后，在侧边栏可以看到API配置状态
2. 上传你的数据文件（CSV、Excel或JSON格式）
3. 在文本框中输入你想要了解的数据问题
4. 点击"Analyze"按钮开始分析
5. 查看AI生成的分析结果、可视化和代码

## 项目结构

```
oidiscover/
├── app1.py              # 主应用文件
├── pyproject.toml       # 项目配置和依赖
├── .python-version      # Python版本指定
├── README.md           # 项目说明
└── .gitignore          # Git忽略文件
```

## 开发

### 安装开发依赖

```bash
uv sync --extra dev
```

### 代码格式化

```bash
uv run black .
```

### 代码检查

```bash
uv run flake8 .
```

## 许可证

MIT License
