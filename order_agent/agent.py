import os
#ADK agent
from google.adk.agents import LlmAgent
#MCP Toolbox to ADK Tool
from google.adk.tools.mcp_tool import McpToolset
#HTTP conn to MCP
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

#Toolbox endpoint
TOOLBOX_MCP_URL = os.getenv("TOOLBOX_MCP_URL", "http://127.0.0.1:5000/mcp")

#Toolbox conn config making (same Toolbox)
def toolbox_conn() -> StreamableHTTPConnectionParams:
    #URL and timeout set
    return StreamableHTTPConnectionParams(url=TOOLBOX_MCP_URL, timeout = 10)

#readonly, no authorization and return
read_tools = McpToolset(
    #Toolbox conn
    connection_params=toolbox_conn(),
    #including Toolbox's tools
    tool_filter=["search_orders", "get_order", "low_stock_itmes"],
)

#writeonly, every action needs authorization
write_tools = McpToolset(
    connection_params= toolbox_conn(),
    tool_filter=["update_order_status"],
    require_confirmation=True,
)

#root agent
root_agent = LlmAgent(
    name="order_ops_agent",
    model=os.environ["GEMINI_MODEL"],
    description="주문 조회, 재고 부족 확인, 주문 상태 변경을 처리하는 영업지원 에이전트",
    instruction=(
        "너는 영업지원팀 주문 담당 에이전트로서, 주문 상태를 바꾸기 전에 반드시 get_order 로 현재 상태를 확인한다."
        "배송완료나 취소된 주문은 변경하지 말고 사유를 설명한다."
        "재고 부족 상품을 안내할 때는 부족 수량이 큰 순서로 표로 보여준다."
        "도구가 돌려준 값만 사실로 말한다."
    ),
    tools=[read_tools, write_tools],
)