#!/usr/bin/env python3
"""
诊断脚本 - 检查Agent配置和响应
"""
import asyncio
from agent_manager import ExcelColorAgent, create_default_system_prompt


async def test_agent():
    print("=" * 60)
    print("Agent配置测试")
    print("=" * 60)

    # 创建Agent
    print("\n1. 创建Agent...")
    agent = ExcelColorAgent(
        model_id="global.anthropic.claude-opus-4-5-20251101-v1:0",
        system_prompt=create_default_system_prompt(),
        selected_tools=["analyze_excel", "apply_color_scale"],
        scale_type="three_color",
        color_scheme="red_yellow_green",
        max_tokens=4096
    )

    print(f"✅ Agent创建成功")
    print(f"   Model ID: {agent.model_id}")
    print(f"   Max Tokens: {agent.max_tokens}")
    print(f"   Scale Type: {agent.scale_type}")
    print(f"   Color Scheme: {agent.color_scheme}")

    # 测试简单对话
    print("\n2. 测试Agent响应...")
    print("   提示: '你好，请简单介绍你的功能'")

    response = await agent.invoke("你好，请简单介绍你的功能")

    print("\n3. 响应结果:")
    result_dict = response.to_dict()

    # 提取文本
    text_parts = []
    if "messages" in result_dict:
        for message in result_dict["messages"]:
            if message.get("role") == "assistant":
                for block in message.get("content", []):
                    if block.get("type") == "textBlock":
                        text_parts.append(block.get("text", ""))

    full_text = "".join(text_parts)

    print(f"   回复长度: {len(full_text)} 字符")
    print(f"   回复内容:")
    print("   " + "-" * 56)
    for line in full_text.split("\n"):
        print(f"   {line}")
    print("   " + "-" * 56)

    # 检查是否被截断
    if full_text.endswith("...") or len(full_text) < 50:
        print("\n⚠️  警告: 回复可能被截断")
    else:
        print("\n✅ 回复正常")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(test_agent())
