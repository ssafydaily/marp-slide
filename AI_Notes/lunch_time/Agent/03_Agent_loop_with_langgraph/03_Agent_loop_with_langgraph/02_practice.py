import os

import requests
from typing import Annotated
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langgraph.graph import StateGraph, START, END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict


load_dotenv()
llm = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL", "gpt-5-nano"),
)

# State 정의
class State(TypedDict):
    messages: Annotated[list, add_messages]




@tool
def get_post(post_id: int) -> str:
    """게시글 번호(post_id)를 받아 해당 게시글의 제목을 반환한다."""
    resp = requests.get(
        f"https://jsonplaceholder.typicode.com/posts/{post_id}", timeout=5
    )
    resp.raise_for_status()
    return resp.json()["title"]


# 2회차 middleware의 오류 처리를 ToolNode에 연결한다.
# 반환한 문자열은 ToolNode가 tool_call_id를 포함한 ToolMessage로 만들어준다.
def handle_tool_errors(e: Exception) -> str:
    return f"도구 호출 오류: 입력값을 확인하고 다시 시도해 주세요. ({e})"


llm_with_tools = llm.bind_tools([get_post], parallel_tool_calls=False)


def call_model(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


builder = StateGraph(State)
builder.add_node("model", call_model)
builder.add_node("tools", ToolNode([get_post], handle_tool_errors=handle_tool_errors))
builder.add_edge(START, "model")
builder.add_conditional_edges(
    "model", tools_condition, {"tools": "tools", END: END}
)
builder.add_edge("tools", "model")
graph = builder.compile()

# 정상 조회와 오류 메시지를 받은 뒤의 모델 응답을 비교한다.
queries = [
    "3번, 5번, 7번 게시글 제목을 각각 조회해줘",
    "9999번 게시글 제목을 조회해줘",
]

for query in queries:
    # 도구 호출이 없어지면 종료한다. 계속 호출하면 실행 단계 상한에서
    # GraphRecursionError가 발생한다. 이 제한은 도구 오류 처리와 별개다.
    for state in graph.stream(
        {"messages": [{"role": "user", "content": query}]},
        config={"recursion_limit": 4},
        stream_mode="values",
    ):
        state["messages"][-1].pretty_print()
