from langchain.prompts import PromptTemplate

template = "Hello {name}"
prompt = PromptTemplate(template=template, input_variables=["name"])

try:
    result = prompt.format(name="World")
    print(result)
except Exception as e:
    print(f"Error: {e}")