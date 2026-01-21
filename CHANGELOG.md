# 变更日志

## 2026-01-20 - 修复 Strands SDK API 兼容性问题

### 问题
1. **工具定义错误**：使用了不存在的 `Tool` 类
2. **Agent调用错误**：使用了不存在的 `.run()` 方法

### 根本原因
Strands SDK 的实际 API 与初始设计不同：
- 工具应使用 `@tool` 装饰器，而不是 `Tool` 类
- Agent 使用异步方法 `invoke_async()` 和 `stream_async()`，而不是同步方法

### 修复内容

#### 1. 工具定义方式 (`tools/`)
**之前（错误）：**
```python
from strands import Tool

def create_analyze_excel_tool() -> Tool:
    def analyze_excel(file_path: str, ...):
        ...
    return Tool(name="analyze_excel", func=analyze_excel, description="...")
```

**修复后（正确）：**
```python
from strands import tool

@tool
def analyze_excel(file_path: str, ...) -> dict:
    """分析Excel文件结构，返回sheet信息和前N行数据预览。

    Args:
        file_path: Excel文件的完整路径
        ...
    """
    ...
```

**关键变化：**
- 使用 `@tool` 装饰器
- docstring 的第一段作为工具描述
- Args 部分自动生成参数说明
- 直接使用函数，不需要包装

#### 2. Agent 方法调用 (`agent_manager.py`)
**之前（错误）：**
```python
def run(self, message: str, context: Dict[str, Any] = None):
    response = self.agent.run(message, context=context)
    return response
```

**修复后（正确）：**
```python
async def invoke(self, prompt: str, invocation_state: Dict[str, Any] = None):
    response = await self.agent.invoke_async(prompt, invocation_state=invocation_state)
    return response
```

**关键变化：**
- 方法变为异步 (`async def`)
- 使用 `invoke_async()` 而不是 `run()`
- 参数名从 `message` 改为 `prompt`
- 参数名从 `context` 改为 `invocation_state`

#### 3. Streamlit 异步调用 (`app.py`)
**之前（错误）：**
```python
response = st.session_state.agent.run(prompt, context=context)
```

**修复后（正确）：**
```python
import asyncio

response = asyncio.run(st.session_state.agent.invoke(prompt, invocation_state=invocation_state))
```

**关键变化：**
- 添加 `import asyncio`
- 使用 `asyncio.run()` 包装异步调用
- 参数名改为 `invocation_state`

#### 4. 响应处理 (`app.py`)
**修复前：**
```python
def process_agent_response(response):
    if hasattr(response, 'content'):
        for content_block in response.content:
            ...
```

**修复后：**
```python
def process_agent_response(agent_result):
    result_dict = agent_result.to_dict()

    if "messages" in result_dict:
        for message in result_dict["messages"]:
            if message.get("role") == "assistant":
                content = message.get("content", [])
                for content_block in content:
                    if content_block.get("type") == "textBlock":
                        result["text"] += content_block.get("text", "")
                    elif content_block.get("type") == "toolUseBlock":
                        ...
```

**关键变化：**
- 使用 `agent_result.to_dict()` 获取结构化数据
- 从 `messages` 中提取内容
- 按照 `role` 和 `type` 解析不同类型的内容块

### 验证

运行以下命令验证修复：

```bash
# 1. 测试工具导入
python3 -c "from tools.analyze_excel_tool import analyze_excel; print('✅ 工具导入成功')"

# 2. 测试 Agent 管理器导入
python3 -c "from agent_manager import ExcelColorAgent; print('✅ Agent 导入成功')"

# 3. 测试 App 导入
python3 -c "import app; print('✅ App 导入成功')"

# 4. 启动应用
streamlit run app.py
```

### Strands SDK API 参考

#### Agent 方法
- `invoke_async(prompt, invocation_state=None)` - 非流式异步调用
- `stream_async(prompt, invocation_state=None)` - 流式异步调用

#### 工具定义
- 使用 `@tool` 装饰器
- docstring 格式：
  - 第一段：工具描述
  - Args 部分：参数说明
  - Returns 部分：返回值说明

#### AgentResult 结构
```python
{
    "messages": [
        {
            "role": "assistant",
            "content": [
                {"type": "textBlock", "text": "..."},
                {"type": "toolUseBlock", "name": "...", "input": {...}}
            ]
        },
        {
            "role": "tool",
            "content": [
                {"type": "toolResultBlock", "toolUseId": "...", "content": [...]}
            ]
        }
    ]
}
```

### 后续优化建议

1. **流式输出**：目前使用非流式调用，可以改用 `stream_async()` 实现流式输出
2. **错误处理**：增强异步调用的错误处理
3. **性能优化**：考虑使用 Streamlit 的 `st.spinner` 显示进度

### 参考文档
- [Strands SDK - Custom Tools](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/tools/custom-tools/)
- [Strands SDK - Agent API](https://strandsagents.com/latest/documentation/)
