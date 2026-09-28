import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from search1api_langchain import Search1APIToolkit
from search1api_langchain import Search1APISearchTool

load_dotenv()  # Load environment variables from .env file

api_key = os.getenv("SEARCH1API_API_KEY") or os.getenv("SEARCH1API_KEY")
if not api_key:
    raise ValueError(
        "Missing Search1API key. Add SEARCH1API_API_KEY or SEARCH1API_KEY to your .env file."
    )

llm = ChatGroq(
    model="openai/gpt-oss-20b",
)

search = Search1APISearchTool()

# results = search.invoke(
#      "What is the capital of France?"
# )

agent = create_agent(
    model=llm,
   tools=[search],
    system_prompt="You are a helpful assistant that can search the web using Search1API."
)

response = agent.invoke(
    {"messages": [{"role": "user", "content": "What changed in LangChain this month?"}]}
)
print(response)