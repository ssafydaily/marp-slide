# LangGraph — 감독이 전문가를 선택하고 결과를 받아 다음 행동을 결정한다.
import os
from typing import Literal

import requests
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import AIMessage, SystemMessage
from langgraph.graph import StateGraph, START, END, MessagesState
from pydantic import BaseModel, Field

load_dotenv()
llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-5-nano"))


@tool
def get_post(post_id: int) -> str:
    """게시글 번호로 제목과 작성자 번호(userId)를 조회한다."""
    resp = requests.get(
        f"https://jsonplaceholder.typicode.com/posts/{post_id}", timeout=5
    )
    resp.raise_for_status()
    data = resp.json()
    return f"제목: {data['title']}\n작성자 번호(userId): {data['userId']}"


@tool
def get_user(user_id: int) -> str:
    """사용자 번호(userId)로 이름을 조회한다."""
    resp = requests.get(
        f"https://jsonplaceholder.typicode.com/users/{user_id}", timeout=5
    )
    resp.raise_for_status()
    return resp.json()["name"]


post_expert = create_agent(
    model=llm,
    tools=[get_post],
    name="post_expert",
    system_prompt=(
        "get_post로 요청한 게시글을 조회하세요. "
        "최종 답변에 제목과 작성자 번호(userId)를 반드시 포함하세요."
    ),
)
user_expert = create_agent(
    model=llm,
    tools=[get_user],
    name="user_expert",
    system_prompt=(
        "사용자 요청 또는 앞선 게시글 전문가의 답변에서 사용자 번호(userId)를 확인하세요. "
        "게시글 번호가 아닌 userId로 get_user를 호출하고 작성자 이름을 답하세요."
    ),
)


# 감독의 출력 형식: 다음 행선지와 전문가에게 전달할 요청(또는 최종 답변).
class Route(BaseModel):
    next: Literal["post_expert", "user_expert", "FINISH"]
    message: str = Field(description="전문가에게 맡길 구체적인 요청 또는 최종 답변")


class TeamState(MessagesState):
    next: str


supervisor = llm.with_structured_output(Route)
supervisor_prompt = (
    "당신은 게시글 전문가와 사용자 전문가를 관리하는 감독입니다. "
    "게시글 제목이나 작성자 번호가 필요하면 post_expert, "
    "사용자 번호로 이름을 조회하려면 user_expert를 선택하세요. "
    "전문가에게 맡길 요청을 message에 적고, 알고 있는 번호를 정확히 전달하세요. "
    "게시글 번호와 작성자 번호(userId)는 다릅니다. 필요한 정보는 전문가에게 조회시키세요. "
    "이미 조회한 결과는 재사용하세요. 답할 정보가 모이면 FINISH를 선택하고 "
    "message에 사용자에게 줄 최종 답변을 한국어로 적으세요."
)


def call_supervisor(state: TeamState):
    decision = supervisor.invoke(
        [SystemMessage(content=supervisor_prompt)] + state["messages"]
    )
    return {
        "next": decision.next,
        "messages": [AIMessage(
            content=f"[{decision.next}] {decision.message}", name="supervisor"
        )],
    }


# 각 전문가는 내부적으로 모델과 도구를 반복 호출한다.
# 공유 상태에는 최종 답변만 추가해 감독에게 돌려준다.
def call_post_expert(state: MessagesState):
    result = post_expert.invoke({"messages": state["messages"]})
    return {"messages": [result["messages"][-1]]}


def call_user_expert(state: MessagesState):
    result = user_expert.invoke({"messages": state["messages"]})
    return {"messages": [result["messages"][-1]]}


# 감독 → 선택한 전문가 → 감독을 반복하다 FINISH이면 종료한다.
builder = StateGraph(TeamState)
builder.add_node("supervisor", call_supervisor)
builder.add_node("post_expert", call_post_expert)
builder.add_node("user_expert", call_user_expert)
builder.add_edge(START, "supervisor")
builder.add_conditional_edges(
    "supervisor",
    lambda state: state["next"],
    {"post_expert": "post_expert", "user_expert": "user_expert", "FINISH": END},
)
builder.add_edge("post_expert", "supervisor")
builder.add_edge("user_expert", "supervisor")
graph = builder.compile()

# 감독의 선택과 전문가의 결과를 차례로 확인한다.
# "사용자 1번 이름이 뭐야?"로 바꾸면 사용자 전문가만 선택하는지 비교할 수 있다.
for state in graph.stream(
    {"messages": [{"role": "user", "content": "5번 게시글을 쓴 사람 이름이 뭐야?"}]},
    config={"recursion_limit": 20},
    stream_mode="values",
):
    state["messages"][-1].pretty_print()
