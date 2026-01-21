"""
Excel色阶处理Agent - Streamlit应用
"""
import streamlit as st
import uuid
import json
import asyncio
from pathlib import Path
from agent_manager import ExcelColorAgent, create_default_system_prompt
from utils.file_manager import FileManager

# 页面配置
st.set_page_config(
    page_title="Excel色阶处理Agent",
    page_icon="🎨",
    layout="wide"
)

# 初始化session state
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = {}

if "agent" not in st.session_state:
    st.session_state.agent = None

if "file_manager" not in st.session_state:
    st.session_state.file_manager = FileManager()

if "output_files" not in st.session_state:
    st.session_state.output_files = []


def reset_session():
    """重置会话"""
    # 清理临时文件
    if "file_manager" in st.session_state and "session_id" in st.session_state:
        st.session_state.file_manager.cleanup_session(
            st.session_state.session_id)

    # 重置所有状态
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.session_state.uploaded_files = {}
    st.session_state.agent = None
    st.session_state.output_files = []
    st.rerun()


def create_agent(model_id: str, system_prompt: str, tools: list, scale_type: str, color_scheme: str, max_tokens: int = 4096):
    """创建或更新Agent"""
    try:
        agent = ExcelColorAgent(
            model_id=model_id,
            system_prompt=system_prompt,
            selected_tools=tools,
            scale_type=scale_type,
            color_scheme=color_scheme,
            max_tokens=max_tokens
        )
        st.session_state.agent = agent
        return True
    except Exception as e:
        st.error(f"创建Agent失败: {str(e)}")
        return False


def display_tool_call(tool_name: str, tool_input: dict, tool_output: dict):
    """展示工具调用信息"""
    with st.expander(f"🔧 工具调用: {tool_name}", expanded=False):
        st.json({
            "tool": tool_name,
            "input": tool_input,
            "output": tool_output
        })


def extract_text_from_chunk(chunk):
    """从Strands流式chunk中提取文本"""
    if isinstance(chunk, dict) and "event" in chunk:
        event = chunk["event"]
        if isinstance(event, dict) and "contentBlockDelta" in event:
            content_delta = event["contentBlockDelta"]
            if isinstance(content_delta, dict):
                delta = content_delta.get("delta", {})
                if "text" in delta:
                    return delta["text"]
    return ""


def process_agent_response(agent_result, agent_messages=None):
    """处理Agent响应，提取文本和工具调用

    Args:
        agent_result: AgentResult对象
        agent_messages: Agent的完整消息历史（可选）
    """
    result = {
        "text": "",
        "tool_calls": []
    }

    # 将AgentResult转换为字典
    result_dict = agent_result.to_dict()

    # 提取最终的文本响应
    if "message" in result_dict:
        message = result_dict["message"]
        if message.get("role") == "assistant":
            content = message.get("content", [])
            for content_block in content:
                if "text" in content_block:
                    result["text"] += content_block["text"]

    # 从完整消息历史中提取工具调用信息
    if agent_messages:
        tool_use_map = {}  # 映射 toolUseId 到工具调用索引

        for msg in agent_messages:
            # 提取工具调用
            if msg.get("role") == "assistant":
                for block in msg.get("content", []):
                    # 注意：键名是 toolUse (驼峰) 不是 tool_use (下划线)
                    if "toolUse" in block:
                        tool_use = block["toolUse"]
                        tool_use_id = tool_use.get("toolUseId", "")
                        tool_call = {
                            "name": tool_use.get("name", ""),
                            "input": tool_use.get("input", {}),
                            "output": None
                        }
                        result["tool_calls"].append(tool_call)
                        if tool_use_id:
                            tool_use_map[tool_use_id] = len(
                                result["tool_calls"]) - 1

            # 提取工具结果
            elif msg.get("role") == "user":
                # 工具结果在 role=user 的消息中
                for block in msg.get("content", []):
                    # 注意：键名是 toolResult (驼峰) 不是 tool_result (下划线)
                    if "toolResult" in block:
                        tool_result = block["toolResult"]
                        tool_use_id = tool_result.get("toolUseId", "")

                        if tool_use_id in tool_use_map:
                            idx = tool_use_map[tool_use_id]
                            # 提取工具的实际输出
                            content = tool_result.get("content", [])
                            if content:
                                # content 是一个列表，通常第一个元素包含结果
                                first_content = content[0] if isinstance(
                                    content, list) else content
                                # 可能是 {"json": {...}} 或 {"text": "..."}
                                tool_output = None
                                if isinstance(first_content, dict):
                                    if "json" in first_content:
                                        tool_output = first_content["json"]
                                    elif "text" in first_content:
                                        tool_output = first_content["text"]
                                    else:
                                        tool_output = first_content
                                else:
                                    tool_output = first_content

                                # 如果工具输出是字符串，尝试解析为字典
                                if isinstance(tool_output, str):
                                    try:
                                        import json
                                        tool_output = json.loads(tool_output)
                                    except:
                                        try:
                                            import ast
                                            tool_output = ast.literal_eval(
                                                tool_output)
                                        except:
                                            pass  # 保持字符串

                                result["tool_calls"][idx]["output"] = tool_output

    return result


# ========== 侧边栏 ==========
with st.sidebar:
    st.title("🎨 Excel色阶处理Agent")

    # 新会话按钮
    if st.button("🆕 开启新会话", use_container_width=True):
        reset_session()

    st.divider()

    # 模型配置
    st.subheader("模型配置")
    model_id = st.text_input(
        "Model ID",
        value="global.anthropic.claude-opus-4-5-20251101-v1:0",
        help="AWS Bedrock模型ID"
    )

    max_tokens = st.number_input(
        "最大输出Token数",
        min_value=512,
        max_value=8192,
        value=4096,
        step=512,
        help="控制模型单次回复的最大长度"
    )

    # System Prompt
    st.subheader("System Prompt")
    system_prompt = st.text_area(
        "系统提示词",
        value=create_default_system_prompt(),
        height=300,
        help="定义Agent的行为和工作流程"
    )

    st.divider()

    # 色阶配置
    st.subheader("色阶配置")

    scale_type_options = {
        "双色阶（渐变）": "two_color",
        "三色阶（低-中-高）": "three_color"
    }
    scale_type_label = st.selectbox(
        "色阶类型",
        options=list(scale_type_options.keys()),
        index=1
    )
    scale_type = scale_type_options[scale_type_label]

    # 根据色阶类型显示不同的配色方案
    if scale_type == "two_color":
        color_scheme_options = {
            "红→绿 (成本：红高绿低)": "red_green",
            "绿→红 (收益：绿高红低)": "green_red",
            "蓝→红 (温度)": "blue_white_red"
        }
    else:  # three_color
        color_scheme_options = {
            "红→黄→绿 (传统)": "red_yellow_green",
            "绿→黄→红 (反向)": "green_yellow_red",
            "蓝→白→红 (温度)": "blue_white_red"
        }

    color_scheme_label = st.selectbox(
        "色彩方案",
        options=list(color_scheme_options.keys()),
        index=0
    )
    color_scheme = color_scheme_options[color_scheme_label]

    st.divider()

    # 工具选择
    st.subheader("工具选择")
    tools = st.multiselect(
        "可用工具",
        options=["analyze_excel", "apply_color_scale"],
        default=["analyze_excel", "apply_color_scale"],
        help="选择Agent可以使用的工具"
    )

    # 显示会话信息
    st.divider()
    st.caption(f"会话ID: {st.session_state.session_id[:8]}...")

# ========== 主区域 ==========
st.title("Excel色阶处理助手")

# 文件上传
uploaded_file = st.file_uploader(
    "📎 上传Excel文件",
    type=["xlsx", "xls"],
    help="上传需要处理的Excel文件"
)

# 处理文件上传
if uploaded_file is not None:
    file_name = uploaded_file.name
    if file_name not in st.session_state.uploaded_files:
        # 保存文件
        file_path = st.session_state.file_manager.save_uploaded_file(
            uploaded_file,
            st.session_state.session_id
        )
        st.session_state.uploaded_files[file_name] = file_path
        st.success(f"✅ 文件已上传: {file_name}")

# 显示已上传的文件
if st.session_state.uploaded_files:
    with st.expander("📁 已上传的文件", expanded=False):
        for name, path in st.session_state.uploaded_files.items():
            st.text(f"• {name}")

st.divider()

# 聊天历史
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        # 显示工具调用
        if "tool_calls" in message and message["tool_calls"]:
            for tool_call in message["tool_calls"]:
                display_tool_call(
                    tool_call["name"],
                    tool_call["input"],
                    tool_call.get("output", {})
                )

        # 显示下载按钮
        if "output_file" in message:
            output_file = message["output_file"]
            if Path(output_file).exists():
                with open(output_file, "rb") as f:
                    file_data = f.read()
                    file_name = Path(output_file).name
                    st.download_button(
                        label=f"📥 下载处理后的文件: {file_name}",
                        data=file_data,
                        file_name=file_name,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

# 用户输入
if prompt := st.chat_input("输入您的需求..."):
    # 检查是否有上传的文件
    if not st.session_state.uploaded_files:
        st.warning("⚠️ 请先上传Excel文件")
    else:
        # 创建Agent（如果还没有或配置变更）
        if st.session_state.agent is None:
            with st.spinner("正在初始化Agent..."):
                if not create_agent(model_id, system_prompt, tools, scale_type, color_scheme, max_tokens):
                    st.stop()

        # 添加用户消息
        st.session_state.messages.append({"role": "user", "content": prompt})

        # 显示用户消息
        with st.chat_message("user"):
            st.markdown(prompt)

        # 构建调用状态（包含已上传文件的路径）
        invocation_state = {
            "uploaded_files": st.session_state.uploaded_files,
            "session_id": st.session_state.session_id
        }

        # Agent处理
        with st.chat_message("assistant"):
            try:
                # 调用Agent（流式输出）
                collected_chunks = []
                # 存储文本段落：[{"type": "text", "content": "..."}, {"type": "tool", "name": "..."}]
                text_segments = []
                text_placeholder = st.empty()

                async def stream_response():
                    async for chunk in st.session_state.agent.stream(prompt, invocation_state=invocation_state):
                        # 收集所有chunk
                        collected_chunks.append(chunk)

                        # 检查是否是完整的message
                        if isinstance(chunk, dict) and "message" in chunk:
                            message = chunk["message"]
                            role = message.get("role")

                            # 处理assistant角色的消息
                            if role == "assistant":
                                content_blocks = message.get("content", [])

                                # 遍历content数组，按顺序处理text和toolUse
                                for block in content_blocks:
                                    if "text" in block:
                                        # 显示文本
                                        text = block["text"]
                                        text_segments.append(
                                            {"type": "text", "content": text})
                                        st.markdown(text)

                                    elif "toolUse" in block:
                                        # 显示工具调用
                                        tool_use = block["toolUse"]
                                        tool_name = tool_use.get("name", "")
                                        text_segments.append(
                                            {"type": "tool", "name": tool_name})
                                        st.info(f"🔧 调用工具: {tool_name}")

                            # 处理user角色的消息（工具返回结果）
                            elif role == "user":
                                content_blocks = message.get("content", [])

                                for block in content_blocks:
                                    if "toolResult" in block:
                                        # 工具返回结果，可以选择显示或不显示
                                        # 这里我们不显示，因为通常工具结果会被agent处理后再输出给用户
                                        pass

                # 运行流式输出
                asyncio.run(stream_response())

                # 清除占位符（不需要了，因为已经在stream中直接显示）
                text_placeholder.empty()

                # 提取完整文本（从text_segments中）
                full_response = "".join(
                    [seg["content"] for seg in text_segments if seg["type"] == "text"])

                # 流式完成后获取完整消息历史
                messages = st.session_state.agent.agent.messages if hasattr(
                    st.session_state.agent.agent, 'messages') else []

                # 从消息历史中提取工具调用信息
                processed = {"text": full_response, "tool_calls": []}
                if messages:
                    tool_use_map = {}
                    for msg in messages:
                        if msg.get("role") == "assistant":
                            for block in msg.get("content", []):
                                if "toolUse" in block:
                                    tool_use = block["toolUse"]
                                    tool_use_id = tool_use.get("toolUseId", "")
                                    tool_call = {
                                        "name": tool_use.get("name", ""),
                                        "input": tool_use.get("input", {}),
                                        "output": None
                                    }
                                    processed["tool_calls"].append(tool_call)
                                    if tool_use_id:
                                        tool_use_map[tool_use_id] = len(
                                            processed["tool_calls"]) - 1
                        elif msg.get("role") == "user":
                            for block in msg.get("content", []):
                                if "toolResult" in block:
                                    tool_result = block["toolResult"]
                                    tool_use_id = tool_result.get(
                                        "toolUseId", "")
                                    if tool_use_id in tool_use_map:
                                        idx = tool_use_map[tool_use_id]
                                        content = tool_result.get(
                                            "content", [])
                                        if content:
                                            first_content = content[0] if isinstance(
                                                content, list) else content
                                            tool_output = None
                                            if isinstance(first_content, dict):
                                                if "json" in first_content:
                                                    tool_output = first_content["json"]
                                                elif "text" in first_content:
                                                    tool_output = first_content["text"]
                                                else:
                                                    tool_output = first_content
                                            else:
                                                tool_output = first_content

                                            # 解析字符串为字典
                                            if isinstance(tool_output, str):
                                                try:
                                                    import json
                                                    tool_output = json.loads(
                                                        tool_output)
                                                except:
                                                    try:
                                                        import ast
                                                        tool_output = ast.literal_eval(
                                                            tool_output)
                                                    except:
                                                        pass

                                            processed["tool_calls"][idx]["output"] = tool_output

                # 调试信息
                print("\n" + "="*60)
                print(f"DEBUG: 流式输出完成")
                print(f"DEBUG: 文本长度: {len(full_response)}")
                print(f"DEBUG: 工具调用数量: {len(processed['tool_calls'])}")
                print("="*60)

                # 显示工具调用
                for tool_call in processed["tool_calls"]:
                    display_tool_call(
                        tool_call["name"],
                        tool_call["input"],
                        tool_call.get("output", {})
                    )

                # 检查是否有输出文件
                output_file = None
                for tool_call in processed["tool_calls"]:
                    if tool_call["name"] == "apply_color_scale" and tool_call.get("output"):
                        output = tool_call["output"]

                        # 如果output是字符串，尝试解析为字典
                        if isinstance(output, str):
                            try:
                                import json
                                # 尝试JSON解析
                                output = json.loads(output)
                            except:
                                # 如果JSON解析失败，尝试eval（不安全但可能是Python字典字符串）
                                try:
                                    import ast
                                    output = ast.literal_eval(output)
                                except:
                                    print(f"警告: 无法解析工具输出: {output[:100]}")
                                    continue

                        # 现在检查是否为字典并提取output_file
                        if isinstance(output, dict) and output.get("success"):
                            output_file = output.get("output_file")
                            print(f"✅ 找到输出文件: {output_file}")
                            break

                # 保存助手消息
                assistant_message = {
                    "role": "assistant",
                    # 存储时也限制长度
                    "content": full_response[:500] if len(full_response) > 500 else full_response,
                    "tool_calls": processed["tool_calls"]
                }

                # 显示下载按钮（在保存消息之前）
                if output_file:
                    assistant_message["output_file"] = output_file
                    if output_file not in st.session_state.output_files:
                        st.session_state.output_files.append(output_file)

                    try:
                        if Path(output_file).exists():
                            with open(output_file, "rb") as f:
                                file_data = f.read()
                            file_name = Path(output_file).name

                            # 使用session时间戳确保key唯一
                            import time
                            download_key = f"download_{int(time.time() * 1000)}"

                            st.download_button(
                                label=f"📥 下载处理后的文件: {file_name}",
                                data=file_data,
                                file_name=file_name,
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                key=download_key
                            )
                        else:
                            st.warning(f"⚠️ 输出文件未找到: {output_file}")
                    except Exception as download_error:
                        st.error(f"生成下载按钮时出错: {str(download_error)}")

                # 最后保存消息（确保前面的显示都完成）
                st.session_state.messages.append(assistant_message)

            except Exception as e:
                error_msg = f"❌ 处理出错: {str(e)}"
                message_placeholder.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })

# 页面底部信息
st.divider()
st.caption("💡 提示：先上传Excel文件，然后输入需求，例如：'为Sheet1的数据刷色阶'")
