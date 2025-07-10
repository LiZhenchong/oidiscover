# 🤖 AI数据探索器 (Gradio + E2B版本)

一个基于Gradio和E2B的智能数据分析工具，支持Excel文件上传和自然语言交互式数据探索。

## ✨ 功能特点

- 📊 **Excel文件支持**: 直接上传.xlsx/.xls文件
- 🤖 **AI对话分析**: 用自然语言描述需求，AI自动生成分析和图表
- 🔒 **安全执行**: 使用E2B沙箱安全执行生成的代码
- 📈 **图表生成**: 自动生成各种数据可视化图表
- 💬 **对话记忆**: 支持多轮对话，AI记住上下文
- 🎨 **现代界面**: 基于Gradio的美观易用界面

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd oidiscover

# 安装依赖
pip install -e .
```

### 2. 配置API密钥

复制 `.env.example` 为 `.env` 并配置API密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# Deepseek API配置 (必需)
DEEPSEEK_API_KEY=sk-your-deepseek-api-key-here

# E2B API配置 (推荐，用于安全代码执行)
E2B_API_KEY=your-e2b-api-key-here
```

### 3. 启动应用

```bash
# 使用启动脚本 (推荐)
python run_gradio.py

# 或直接运行
python gradio_app.py
```

应用将在 http://localhost:7860 启动

## 📖 使用说明

### 1. 上传数据
- 点击"📁 上传Excel文件"
- 选择你的.xlsx或.xls文件
- 系统会自动显示数据概览和预览

### 2. 数据探索
在对话框中输入你的需求，例如：
- "分析销售数据的趋势"
- "生成各产品类别的销量对比图"
- "找出异常值"
- "创建相关性分析"

### 3. 查看结果
- AI会提供分析结论
- 如果适用，会生成相应的图表
- 可以查看生成的Python代码

## 💡 示例查询

```
📊 基础分析
- "显示数据的基本统计信息"
- "分析数据质量，找出缺失值"

📈 趋势分析  
- "生成销售额的月度趋势图"
- "分析用户增长趋势"

📊 对比分析
- "比较不同产品类别的表现"
- "生成地区销售对比柱状图"

🔍 深度分析
- "进行相关性分析"
- "找出数据中的异常模式"
```

## 🔧 技术架构

### 核心组件
- **Gradio**: 现代化Web界面
- **E2B**: 安全代码沙箱执行
- **Deepseek API**: AI分析和代码生成
- **Pandas**: 数据处理
- **Matplotlib/Seaborn**: 数据可视化

### 安全特性
- 🔒 E2B沙箱隔离执行用户代码
- 🛡️ 严格的文件类型验证
- 🚫 禁止执行危险操作
- 📝 代码审查和日志记录

## ⚙️ 配置选项

在 `.env` 文件中可配置：

```env
# API配置
DEEPSEEK_API_KEY=your_key
E2B_API_KEY=your_key

# 应用配置
MAX_FILE_SIZE_MB=50          # 最大文件大小
MAX_CONVERSATION_HISTORY=10  # 对话历史长度
```

## 🔍 故障排除

### 常见问题

**Q: E2B API密钥未设置**
A: 应用会自动回退到本地执行模式，但功能受限。建议注册E2B账号获取API密钥。

**Q: 图表显示中文乱码**
A: 应用已自动配置中文字体支持，如仍有问题请检查系统字体。

**Q: 文件上传失败**
A: 检查文件格式是否为.xlsx或.xls，文件大小是否超限。

### 获取帮助

1. 查看控制台错误日志
2. 检查API密钥配置
3. 确认网络连接正常
4. 提交Issue到项目仓库

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

---

💡 **提示**: 首次使用建议先用小型测试数据集熟悉功能，然后再处理大型数据文件。