from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="local-model",
    temperature=0,
    base_url="http://127.0.0.1:9999/v1",
    api_key="dummy"
)

response = llm.predict("Hello!")
print(response)