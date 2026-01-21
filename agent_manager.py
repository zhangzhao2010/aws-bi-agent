"""
Agent管理器
封装Strands Agent，处理与模型的交互
"""
from strands import Agent
from strands.models.bedrock import BedrockModel
from typing import List, Dict, Any, Iterator
from tools.analyze_excel_tool import analyze_excel
from tools.color_scale_tool import apply_color_scale


class ExcelColorAgent:
    """Excel色阶处理Agent"""

    def __init__(
        self,
        model_id: str,
        system_prompt: str,
        selected_tools: List[str],
        scale_type: str = "three_color",
        color_scheme: str = "red_yellow_green",
        max_tokens: int = 4096
    ):
        """
        初始化Agent

        Args:
            model_id: Bedrock模型ID
            system_prompt: 系统提示词
            selected_tools: 选中的工具列表
            scale_type: 色阶类型
            color_scheme: 色彩方案
            max_tokens: 最大输出token数
        """
        self.model_id = model_id
        self.scale_type = scale_type
        self.color_scheme = color_scheme
        self.max_tokens = max_tokens

        # 构建完整的system prompt
        full_system_prompt = self._build_system_prompt(system_prompt, scale_type, color_scheme)

        # 创建可用工具
        self.available_tools = {
            "analyze_excel": analyze_excel,
            "apply_color_scale": apply_color_scale
        }

        # 根据选择构建工具列表
        tools = [self.available_tools[tool_name] for tool_name in selected_tools if tool_name in self.available_tools]

        # 创建Bedrock模型
        model = BedrockModel(
            model_id=model_id,
            max_tokens=self.max_tokens,  # 使用配置的最大输出token数
            temperature=0.7              # 设置温度参数
        )

        # 创建Agent
        self.agent = Agent(
            name="excel_color_agent",
            model=model,
            system_prompt=full_system_prompt,
            tools=tools
        )

    def _build_system_prompt(self, base_prompt: str, scale_type: str, color_scheme: str) -> str:
        """构建包含配置信息的system prompt"""
        config_info = f"""

当前配置：
- 色阶类型: {scale_type}
- 色彩方案: {color_scheme}

调用 apply_color_scale 工具时，请使用以上配置的 scale_type 和 color_scheme 参数。
"""
        return base_prompt + config_info

    async def invoke(self, prompt: str, invocation_state: Dict[str, Any] = None):
        """
        运行Agent（非流式异步）

        Args:
            prompt: 用户消息
            invocation_state: 调用状态信息

        Returns:
            包含Agent响应和完整消息历史的元组 (response, messages)
        """
        response = await self.agent.invoke_async(prompt, invocation_state=invocation_state)
        # 同时返回完整的消息历史
        messages = self.agent.messages if hasattr(self.agent, 'messages') else []
        return response, messages

    async def stream(self, prompt: str, invocation_state: Dict[str, Any] = None):
        """
        运行Agent（流式异步）

        Args:
            prompt: 用户消息
            invocation_state: 调用状态信息

        Yields:
            流式响应块
        """
        async for chunk in self.agent.stream_async(prompt, invocation_state=invocation_state):
            yield chunk


def create_default_system_prompt() -> str:
    """创建默认的system prompt"""
    return """你是一个Excel数据处理专家助手，帮助用户为Excel表格添加色阶。

你有以下工具：
1. analyze_excel: 分析Excel文件结构，返回sheet信息和数据预览
2. apply_color_scale: 为指定范围应用色阶

**重要提示：用户已上传的Excel文件会自动传递给工具，你不需要提供file_path参数。**

工作流程：
1. 用户上传文件后，主动调用 analyze_excel 工具分析文件
   - **不需要**传递file_path参数，已上传的文件会自动使用
   - 只需传递 sheet_name（可选）和 preview_rows（可选）
2. 仔细查看返回的 preview_rows 数据（前100行），判断：
   - 哪一行是表头（通常是文本标签）
   - 从哪一行开始是数值数据
   - 哪些列包含需要刷色阶的数据（数值列）
3. 根据用户需求（如"为Sheet1数据刷色阶"）和分析结果，确定：
   - sheet_name: 用户指定的sheet
   - cell_range: 数据范围（格式：B2:E150，要跳过表头）
4. 调用 apply_color_scale 工具应用色阶
   - **不需要**传递file_path参数，已上传的文件会自动使用
   - 必需参数：sheet_name, cell_range, scale_type, color_scheme
5. 完成后告知用户具体应用的范围和单元格数量

注意事项：
- 表头通常是第一行或多行，包含列标签文本
- 数据区是纯数字的行，表头之后开始
- 如果分析结果不清晰（如空行很多、数据分散），询问用户确认范围
- 透视表通常左上角有多层表头，要小心识别
- 必须跳过表头，只为数据单元格刷色阶
- 只为包含数值的列应用色阶，文本列不适合

示例对话：
用户：为Sheet1的数据刷色阶

你的操作：
1. 调用 analyze_excel() - 不传file_path，系统会自动使用已上传的文件
2. 查看 preview_rows，判断第1行是表头（包含"日期"、"金额"等文字）
3. 判断第2行开始是数据（包含日期和数字）
4. 确定数值列（如B、C、D列是金额数据）
5. 调用 apply_color_scale(sheet_name="Sheet1", cell_range="B2:D100", scale_type="...", color_scheme="...")
   - 跳过A列的日期，只刷数值列
   - 不传file_path参数
6. 告知用户已完成

重要：
- **从不要求用户提供文件路径**，文件已经上传到系统中
- 在调用 apply_color_scale 时，scale_type 和 color_scheme 参数会根据用户在界面左侧栏的选择自动设置
- 工具调用示例：analyze_excel() 或 analyze_excel(sheet_name="Sheet1")
- 工具调用示例：apply_color_scale(sheet_name="Sheet1", cell_range="B2:D100", scale_type="three_color", color_scheme="red_yellow_green")
"""
