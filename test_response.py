#!/usr/bin/env python3
"""
测试Agent响应是否完整
"""
import asyncio
import json
from agent_manager import ExcelColorAgent, create_default_system_prompt


async def test_full_workflow():
    print("=" * 80)
    print("测试完整工作流程")
    print("=" * 80)

    # 创建Agent
    agent = ExcelColorAgent(
        model_id="global.anthropic.claude-opus-4-5-20251101-v1:0",
        system_prompt=create_default_system_prompt(),
        selected_tools=["analyze_excel", "apply_color_scale"],
        scale_type="three_color",
        color_scheme="red_yellow_green",
        max_tokens=4096
    )

    # 模拟上传文件
    invocation_state = {
        "uploaded_files": {
            "Spend_Chart_Daily.xlsx": "/Users/allenzh/Documents/Amazon/2-业务/客户/2025/LivU/color/Spend_Chart_Daily.xlsx"
        },
        "session_id": "test_session"
    }

    print("\n发送请求: 为Sheet1的数据刷色阶")
    print("-" * 80)

    # 调用Agent
    response = await agent.invoke("为Sheet1的数据刷色阶", invocation_state=invocation_state)

    print("\n获取响应结果...")
    result_dict = response.to_dict()

    # 保存完整响应到文件
    with open("agent_response.json", "w", encoding="utf-8") as f:
        json.dump(result_dict, f, ensure_ascii=False, indent=2)
    print("✅ 完整响应已保存到 agent_response.json")

    # 提取并显示文本内容
    print("\n" + "=" * 80)
    print("文本响应内容:")
    print("=" * 80)

    text_parts = []
    if "messages" in result_dict:
        for message in result_dict["messages"]:
            if message.get("role") == "assistant":
                for block in message.get("content", []):
                    if block.get("type") == "textBlock":
                        text = block.get("text", "")
                        text_parts.append(text)

    full_text = "".join(text_parts)
    print(full_text)

    print("\n" + "=" * 80)
    print(f"响应长度: {len(full_text)} 字符")
    print(f"是否完整: {'✅ 是' if not full_text.endswith('...') else '⚠️ 可能被截断'}")

    # 提取工具调用
    print("\n" + "=" * 80)
    print("工具调用:")
    print("=" * 80)

    tool_count = 0
    if "messages" in result_dict:
        for message in result_dict["messages"]:
            if message.get("role") == "assistant":
                for block in message.get("content", []):
                    if block.get("type") == "toolUseBlock":
                        tool_count += 1
                        print(f"\n工具 #{tool_count}: {block.get('name')}")
                        print(f"  输入: {json.dumps(block.get('input', {}), ensure_ascii=False)}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(test_full_workflow())
