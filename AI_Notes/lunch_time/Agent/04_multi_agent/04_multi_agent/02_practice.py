# 4회차 실습 — Deep Agents에 전문 에이전트 두 개를 등록해 작업을 맡긴다.
# 추가 패키지 설치: pip install deepagents
import os

import requests
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from deepagents import create_deep_agent
from langchain.tools import tool

load_dotenv()
llm = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL", "gpt-5-nano"),
)


@tool
def get_post(post_id: int) -> str:
    """게시글 번호로 제목과 작성자 번호(userId)를 반환한다."""
    resp = requests.get(
        f"https://jsonplaceholder.typicode.com/posts/{post_id}", timeout=5
    )
    resp.raise_for_status()
    data = resp.json()
    return f"제목: {data['title']}\n작성자 번호(userId): {data['userId']}"


@tool
def get_user(user_id: int) -> str:
    """사용자 번호(user_id)를 받아 이름과 이메일을 반환한다."""
    resp = requests.get(
        f"https://jsonplaceholder.typicode.com/users/{user_id}", timeout=5
    )
    resp.raise_for_status()
    data = resp.json()
    return f"이름: {data['name']}\n이메일: {data['email']}"


# example에서 직접 만든 감독·분기·복귀 구조를 Deep Agents의 task 도구가 담당한다.
# description은 상위 에이전트의 선택 기준, system_prompt는 전문가의 작업 지침이다.
post_expert = {
    "name": "post_expert",
    "description": "게시글 번호로 제목과 작성자 번호(userId)를 조회하는 전문가",
    "system_prompt": (
        "반드시 get_post로 조회하고 게시글 제목과 작성자 번호(userId)를 반환하세요."
    ),
    "tools": [get_post],
}

user_expert = {
    "name": "user_expert",
    "description": "사용자 번호(userId)로 이름과 이메일을 조회하는 전문가",
    "system_prompt": "반드시 get_user로 조회하고 이름과 이메일을 반환하세요.",
    "tools": [get_user],
}

# Deep Agents가 제공하는 task 도구로 전문가에게 작업을 맡긴다.
# 전문가들은 model을 생략하면 상위 에이전트의 OpenAI 모델을 사용한다.
agent = create_deep_agent(
    model=llm,
    subagents=[post_expert, user_expert],
    system_prompt=(
        "게시글 작성자를 찾을 때는 task 도구로 post_expert에게 먼저 조회를 맡기세요. "
        "반환받은 작성자 번호(userId)를 user_expert에게 전달해 이름을 조회하세요. "
        "게시글 번호와 사용자 번호를 혼동하지 마세요. "
        "두 전문가의 조회 결과를 바탕으로 한국어로 답하세요."
    ),
)

question = "5번 게시글을 쓴 사람 이름이 뭐야?"
# 상위 에이전트의 task 호출과 전문가가 돌려준 결과를 확인한다.
for state in agent.stream(
    {"messages": [{"role": "user", "content": question}]},
    stream_mode="values",
):
    state["messages"][-1].pretty_print()
