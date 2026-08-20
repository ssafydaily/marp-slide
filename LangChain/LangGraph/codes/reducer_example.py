from typing_extensions import TypedDict, Annotated
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, START, END

def add_names(left:list[str], right:list[str]):
    return left + right

class MyState(TypedDict):
    names: Annotated[list[str], add_names]
    temp: str
    total: Annotated[int, lambda l, r: l + r]

def my_node(state: MyState):
    print('running my_node')
    print(state)
    print('---------')
    return {"temp": "수정된 문자열", "names": ["아이유"], "total": 1}

graph = StateGraph(MyState)

graph.add_node("my_node", my_node)
graph.add_edge(START, "my_node")
graph.add_edge("my_node", END)
agent = graph.compile()

result = agent.invoke({"temp": "테스트 문자열", "names": ["서강준"], "total": 1})
print(result)