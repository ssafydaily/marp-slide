import os

import requests
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()
llm = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL", "gpt-5-nano"),
)


@tool
def get_post(post_id: int) -> str:
    """게시글 번호(post_id)를 받아 해당 게시글의 제목을 반환한다."""
    resp = requests.get(
        f"https://jsonplaceholder.typicode.com/posts/{post_id}", timeout=5
    )
    resp.raise_for_status()
    # return '데이터를 불러오는데 실패했습니다. 다시 시도해 주세요.'
    return resp.json()["title"]


# 한 번의 모델 응답에서 도구를 하나씩 호출해 반복 흐름을 확인한다.
llm_with_tools = llm.bind_tools([get_post], parallel_tool_calls=False)


def call_model(state: MessagesState):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


builder = StateGraph(MessagesState)
builder.add_node("model", call_model)
builder.add_node("tools", ToolNode([get_post]))
builder.add_edge(START, "model")
builder.add_conditional_edges(
    "model", tools_condition, {"tools": "tools", END: END}
)
builder.add_edge("tools", "model")
graph = builder.compile()

# 도구 호출이 있으면 tools로, 없으면 END로 이동한다.
# recursion_limit은 도구 호출 횟수가 아닌 그래프 실행 단계 수의 상한이다.
for state in graph.stream(
    {"messages": [{"role": "user", "content": "3번, 5번, 7번 게시글 제목을 각각 조회해줘"}]},
    config={"recursion_limit": 4},
    stream_mode="values",
):
    state["messages"][-1].pretty_print()
