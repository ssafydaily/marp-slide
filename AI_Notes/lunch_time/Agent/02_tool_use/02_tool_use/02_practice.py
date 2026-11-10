import os

import requests
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_tool_call
from langchain.tools import tool
from langchain_core.messages import ToolMessage

load_dotenv()
llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-5-nano"))

# 도구 1: 게시글 번호로 제목·본문·작성자 ID(userId)를 조회
@tool
def get_post(post_id: int) -> str:
    """게시글 번호(post_id)를 받아 제목, 본문, 작성자 번호(userId)를 반환한다."""
    resp = requests.get(
        f"https://jsonplaceholder.typicode.com/posts/{post_id}", timeout=5
    )
    resp.raise_for_status()
    data = resp.json()
    return (
        f"제목: {data['title']}\n본문: {data['body']}\n작성자 번호(userId): {data['userId']}"
    )


# 도구 2: 사용자 번호로 이름·이메일을 조회
@tool
def get_user(user_id: int) -> str:
    """사용자 번호(user_id)를 받아 이름과 이메일을 반환한다."""
    resp = requests.get(
        f"https://jsonplaceholder.typicode.com/users/{user_id}", timeout=5
    )
    resp.raise_for_status()
    data = resp.json()
    return f"이름: {data['name']}\n이메일: {data['email']}"


# 도구 실행 중 오류(예: 존재하지 않는 번호 요청)가 나면 예외를 그대로 발생시키는 대신 대신
# 모델이 이해할 수 있는 메시지로 바꿔서 돌려준다
@wrap_tool_call
def handle_tool_errors(request, handler) -> ToolMessage:
    try:
        return handler(request)
    except Exception as e:
        return ToolMessage(
            content=f"도구 호출 오류: 입력값을 확인하고 다시 시도해 주세요. ({e})",
            tool_call_id=request.tool_call["id"],
        )


agent = create_agent(
    model=llm,
    tools=[get_post, get_user],
    middleware=[handle_tool_errors],
)

queries = [
    "5번 게시글을 쓴 사람 이름이 뭐야?",
    "9999번 게시글을 쓴 사람 이름이 뭐야?",
]

for i, query in enumerate(queries, start=1):
    print(f"\n===== Request {i} =====")
    print(f"UserMessage: {query}")

    for step in agent.stream({"messages": [{"role": "user", "content": query}]}):
        for payload in step.values():
            for message in payload.get("messages", []):
                message_type = type(message).__name__
                label = "UserMessage" if message_type == "HumanMessage" else message_type

                content = (message.content or "").strip()
                if content:
                    print(f"{label}: {content}")

                # AI가 tool call만 반환해 본문이 비어 있을 때도 흐름이 보이도록 출력
                if label == "AIMessage" and getattr(message, "tool_calls", None):
                    for call in message.tool_calls:
                        print(f"AIMessage: tool_call -> {call['name']}({call['args']})")