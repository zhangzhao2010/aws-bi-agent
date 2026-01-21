# Excel色阶处理Agent Demo

基于 Strands Agent SDK 和 AWS Bedrock 的智能Excel色阶处理工具。

## 功能特性

- 🎨 **智能识别数据范围**：自动分析Excel文件结构，识别表头和数据区域
- 🔧 **多种色阶配置**：支持双色阶和三色阶，多种配色方案可选
- 💬 **对话式交互**：通过自然语言指令完成Excel处理任务
- 📊 **透视表支持**：能够处理复杂的透视表结构
- ⬇️ **文件下载**：处理完成后可直接下载带色阶的Excel文件

## 技术栈

- **前端框架**: Streamlit
- **Agent框架**: Strands Agent SDK
- **LLM模型**: AWS Bedrock (Claude Opus 4.5)
- **Excel处理**: openpyxl

## 项目结构

```
color/
├── app.py                      # Streamlit主程序
├── agent_manager.py            # Agent管理器
├── tools/                      # Agent工具
│   ├── analyze_excel_tool.py   # Excel分析工具
│   └── color_scale_tool.py     # 色阶应用工具
├── utils/                      # 工具类
│   ├── excel_analyzer.py       # Excel分析逻辑
│   └── file_manager.py         # 文件管理
├── temp/                       # 临时文件目录
└── requirements.txt            # 依赖包
```

## 安装

1. 克隆项目

```bash
cd color
```

2. 安装依赖

```bash
pip install -r requirements.txt
```

3. 配置AWS凭证

确保已配置AWS凭证，以便访问Bedrock服务：

```bash
aws configure
```

或设置环境变量：

```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

## 使用方法

1. 启动应用

```bash
streamlit run app.py
```

2. 在浏览器中打开显示的URL（通常是 http://localhost:8501）

3. 配置参数（左侧栏）
   - 选择色阶类型（双色阶/三色阶）
   - 选择配色方案
   - 选择可用工具

4. 上传Excel文件

5. 输入需求，例如：
   - "为Sheet1的数据刷色阶"
   - "分析这个Excel文件的结构"
   - "为Sheet2的B2到E100区域应用色阶"

6. 下载处理后的文件

## 示例对话

```
用户: 为Sheet1的数据刷色阶

Agent: 我先分析一下文件结构...
[调用 analyze_excel 工具]

Agent: 分析完成！我看到Sheet1包含：
- 第1行是表头（包含"日期"、"金额"等列）
- 第2-150行是数据
- B、C、D、E列是数值列

现在为B2:E150区域应用色阶...
[调用 apply_color_scale 工具]

Agent: ✅ 完成！已为Sheet1的B2:E150区域（596个单元格）应用三色色阶。
[显示下载按钮]
```

## 支持的色阶配置

### 双色阶
- 红→绿（成本：红高绿低）
- 绿→红（收益：绿高红低）
- 蓝→红（温度）

### 三色阶
- 红→黄→绿（传统）
- 绿→黄→红（反向）
- 蓝→白→红（温度）

## Agent工作流程

1. **文件分析阶段**
   - 调用 `analyze_excel` 工具读取Excel结构
   - 获取前100行数据和总行数
   - 返回sheet列表、数据维度、单元格预览

2. **范围判断阶段**
   - 根据preview数据判断表头位置
   - 识别数值列（适合应用色阶）
   - 确定数据范围（跳过表头）

3. **色阶应用阶段**
   - 调用 `apply_color_scale` 工具
   - 根据用户配置选择色阶类型和方案
   - 生成新文件（原文件名_colored.xlsx）

4. **结果返回阶段**
   - 告知用户应用的范围和单元格数量
   - 提供文件下载链接

## 配置说明

### Model ID
默认使用：`global.anthropic.claude-opus-4-5-20251101-v1:0`

可以修改为其他Bedrock支持的模型ID。

### System Prompt
定义Agent的行为逻辑，包括：
- 工作流程
- 工具使用方式
- 数据识别规则
- 注意事项

可以根据需要自定义。

## 注意事项

1. **文件格式**：仅支持 `.xlsx` 和 `.xls` 格式
2. **数据类型**：色阶仅适用于数值数据，文本列不适合
3. **透视表**：透视表刷新后条件格式可能失效，需重新应用
4. **临时文件**：点击"开启新会话"会清理临时文件
5. **AWS权限**：需要有Bedrock的调用权限

## 开发说明

### 添加新工具

1. 在 `tools/` 目录下创建新的工具文件
2. 使用 `strands.Tool` 定义工具接口
3. 在 `agent_manager.py` 中注册工具
4. 在 `app.py` 的工具选择中添加选项

### 扩展色阶方案

在 `tools/color_scale_tool.py` 的 `COLOR_SCHEMES` 字典中添加新方案：

```python
COLOR_SCHEMES = {
    "two_color": {
        "your_scheme": {
            "start_type": "min",
            "start_color": "RRGGBB",
            "end_type": "max",
            "end_color": "RRGGBB"
        }
    }
}
```

## 故障排查

### Agent初始化失败
- 检查AWS凭证配置
- 确认Bedrock服务在当前区域可用
- 验证Model ID是否正确

### 文件分析失败
- 确认Excel文件格式正确
- 检查文件是否损坏
- 查看是否有权限读取文件

### 色阶应用失败
- 检查单元格范围格式（如 "B2:E10"）
- 确认sheet名称正确
- 验证目标单元格包含数值数据

## License
Apache-2.0
