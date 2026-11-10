import os

import requests
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.tools import tool

load_dotenv()
llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-5-nano"))


# 도구 하나: 게시글 번호를 받아 실제 API에서 제목·내용을 가져온다
@tool
def get_post(post_id: int) -> str:
    """날씨 정보를 반환한다."""
    # """게시글 번호(post_id)를 받아 해당 게시글의 제목과 본문을 반환한다."""
    resp = requests.get(
        f"https://jsonplaceholder.typicode.com/posts/{post_id}", timeout=5
    )
    resp.raise_for_status()
    data = resp.json()
    return f"제목: {data['title']}\n본문: {data['body']}"


agent = create_agent(model=llm, tools=[get_post])
result = agent.invoke(
    {"messages": [{"role": "user", "content": "3번 게시글 제목이 뭐야?"}]}
)
print(result["messages"][-1].content)
