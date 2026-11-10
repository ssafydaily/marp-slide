import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


load_dotenv()
# llm = ChatOpenAI(
#     model=os.getenv("OPENAI_MODEL", "gpt-5-nano"),
#     api_key=os.environ["GMS_KEY"],
#     base_url="https://gms.ssafy.io/gmsapi/api.openai.com/v1/",
# )

prompt = PromptTemplate.from_template("부산 날씨 알려줘.")

llm = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL", "gpt-5-nano"),
)

outputparser = StrOutputParser()

chatbot = prompt | llm | outputparser

result = chatbot.invoke(
    {"messages": [{"role": "user", "content": "부산 날씨 알려줘."}]}
)

print(result)
