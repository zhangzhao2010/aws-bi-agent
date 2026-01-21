# 快速启动指南

## 🚀 一键启动

```bash
./run.sh
```

或手动启动：

```bash
streamlit run app.py
```

## ⚙️ 启动前准备

### 1. 配置AWS凭证

**方式1：使用 AWS CLI 配置**
```bash
aws configure
```

**方式2：设置环境变量**
```bash
export AWS_ACCESS_KEY_ID=你的Access_Key
export AWS_SECRET_ACCESS_KEY=你的Secret_Key
export AWS_DEFAULT_REGION=us-east-1
```

### 2. 安装依赖（首次运行）

```bash
pip install -r requirements.txt
```

## 📖 使用流程

1. **访问应用**
   - 浏览器打开：http://localhost:8501

2. **配置参数**（左侧栏）
   - 色阶类型：双色阶 / 三色阶
   - 配色方案：红→绿、绿→红等
   - 工具选择：默认全选

3. **上传Excel文件**
   - 点击"上传Excel文件"按钮
   - 支持 .xlsx 和 .xls 格式

4. **输入需求**
   - 示例："为Sheet1的数据刷色阶"
   - 示例："分析这个文件的结构"

5. **下载结果**
   - Agent处理完成后会显示下载按钮
   - 点击下载处理后的Excel文件

## 💡 使用示例

### 示例1：基础用法
```
用户上传: AWS_Billing.xlsx
用户输入: 为Sheet1的数据刷色阶

Agent会：
1. 自动分析文件结构
2. 识别表头和数据范围
3. 应用色阶到数据区
4. 提供下载链接
```

### 示例2：指定范围
```
用户输入: 为Sheet2的B2到E100区域应用色阶

Agent会：
1. 直接对指定范围应用色阶
2. 使用左侧栏配置的色阶类型和方案
```

### 示例3：先分析再处理
```
用户输入: 先分析一下这个Excel文件

Agent会：
1. 返回所有sheet名称
2. 展示前100行数据结构
3. 告知总行数和列数

用户输入: 好的，为Sheet1刷色阶

Agent会：
1. 基于之前的分析结果
2. 应用色阶
```

## ⚠️ 注意事项

1. **AWS权限**
   - 需要有 Bedrock 服务的调用权限
   - 确认 Claude Opus 4.5 模型可用

2. **数据类型**
   - 色阶仅适用于数值数据
   - 文本列不适合应用色阶

3. **文件保存**
   - 原文件不会被修改
   - 生成的新文件名为：原文件名_colored.xlsx

4. **会话管理**
   - 点击"开启新会话"会清空聊天记录和临时文件
   - 每个会话有独立的临时目录

## 🐛 常见问题

### Q: 提示 "cannot import name 'Tool'" 错误？
A: 已修复。确保使用最新版本的代码。工具现在使用 `@tool` 装饰器而不是 `Tool` 类。

### Q: 提示 "'Agent' object has no attribute 'run'" 错误？
A: 已修复。Agent 现在使用异步方法 `invoke_async()` 而不是 `run()`。

### Q: 提示 AWS 凭证未配置？
A: 运行 `aws configure` 或设置环境变量

### Q: 提示模型不可用？
A: 检查你的 AWS 区域是否支持 Bedrock 和 Claude Opus 4.5

### Q: Agent 没有应用色阶？
A: 检查：
- 是否选择了正确的 sheet
- 数据列是否为数值类型
- 范围格式是否正确（如 B2:E10）

### Q: 下载的文件没有色阶？
A: 用 Excel 或 WPS 打开，确认是否有条件格式（色阶可能在某些在线预览工具中不显示）

### Q: 启动时报错 "asyncio" 相关错误？
A: 这是正常的，Streamlit 会自动处理异步调用。如果应用无法启动，检查 Python 版本是否 >= 3.7

## 📊 测试文件

项目目录中包含 `Spend_Chart_Daily.xlsx` 测试文件，可以用来测试功能。

## 🔧 开发调试

### 查看日志
```bash
# Streamlit 会在终端输出日志
streamlit run app.py --logger.level=debug
```

### 修改 System Prompt
在左侧栏的 System Prompt 文本框中直接编辑，然后发送新消息时会重新创建 Agent。

### 测试工具单独运行
```python
from tools.analyze_excel_tool import analyze_excel
from tools.color_scale_tool import apply_color_scale

# 测试分析工具
result = analyze_excel("test.xlsx")
print(result)

# 测试色阶工具
result = apply_color_scale(
    "test.xlsx",
    "Sheet1",
    "B2:E10",
    "three_color",
    "red_yellow_green"
)
print(result)
```

## 📞 获取帮助

遇到问题？检查：
1. requirements.txt 中的依赖是否都安装成功
2. AWS 凭证是否正确配置
3. Python 版本是否 >= 3.8
4. 终端是否有报错信息

---

**祝使用愉快！** 🎉
