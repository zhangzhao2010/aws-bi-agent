"""
Excel分析工具 - Strands Agent Tool
"""
from strands import tool, ToolContext
from utils.excel_analyzer import analyze_excel_file
from typing import Optional


@tool(context=True)
def analyze_excel(file_path: str = "", sheet_name: Optional[str] = None, preview_rows: int = 100, tool_context: ToolContext = None) -> dict:
    """分析Excel文件结构，返回sheet信息和前N行数据预览。

    此工具会读取Excel文件并返回：
    1. 所有sheet的名称列表
    2. 每个sheet的前N行数据（包含单元格值和数据类型）
    3. 每个sheet的总行数和总列数
    4. Sheet的维度范围

    使用场景：
    - 用户上传Excel文件后，先调用此工具了解文件结构
    - 需要判断哪些行是表头，哪些行是数据
    - 需要确定数据的范围以便应用色阶

    重要：file_path参数可以省略，系统会自动使用用户已上传的文件。

    Args:
        file_path: Excel文件的完整路径（可选，默认使用已上传的文件）
        sheet_name: 可选，指定要分析的sheet名称。如果不提供，则分析所有sheet
        preview_rows: 预览的行数，默认100行

    Returns:
        包含sheet列表、数据预览和维度信息的字典，格式如：
        {
          "success": true,
          "data": {
            "sheets": ["Sheet1", "Sheet2"],
            "sheet_data": {
              "Sheet1": {
                "total_rows": 150,
                "total_columns": 10,
                "dimensions": "A1:J150",
                "preview_rows": [...]
              }
            }
          }
        }
    """
    try:
        # 如果没有提供file_path，尝试从invocation_state获取
        actual_file_path = file_path
        if not file_path or file_path == "":
            if tool_context and tool_context.invocation_state:
                uploaded_files = tool_context.invocation_state.get("uploaded_files", {})
                if uploaded_files:
                    # 使用第一个上传的文件
                    actual_file_path = list(uploaded_files.values())[0]
                else:
                    return {
                        "success": False,
                        "error": "没有找到已上传的文件，请先上传Excel文件"
                    }
            else:
                return {
                    "success": False,
                    "error": "请提供file_path参数或先上传文件"
                }

        result = analyze_excel_file(actual_file_path, sheet_name, preview_rows)
        return {
            "success": True,
            "data": result
        }
    except FileNotFoundError:
        return {
            "success": False,
            "error": f"文件不存在: {actual_file_path if 'actual_file_path' in locals() else file_path}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"分析失败: {str(e)}"
        }
