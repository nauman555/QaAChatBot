from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

#   required pakages 
#   db , llm , tools , agent , memory , system promt 

from langchain_groq import ChatGroq
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent
import streamlit as st

db = SQLDatabase.from_uri("sqlite:///todolistdb.db")  # Create a SQLDatabase instance from the SQLite database URI


db.run("""CREATE TABLE IF NOT EXISTS tasks 
        (
        id INTEGER PRIMARY KEY, 
        title TEXT not null, description TEXT, 
        status TEXT check(status in ('pending', 'in_progress', 'completed'))  default 'pending'   , created_at TIMESTAMP default CURRENT_TIMESTAMP
        );
        """)  # Create a table for tasks if it doesn't exist

#llm , tools , memory  , system prompt

llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0, max_tokens=512)  # Initialize the language model with specified parameters
toolkit = SQLDatabaseToolkit(db=db, llm=llm)  # Create a toolkit for interacting with the SQL database using the language model
tools = [tool for tool in toolkit.get_tools() if tool.name == "sql_db_query"]


system_prompt = """You manage tasks in the SQLite tasks table.

Rules:
- For requests to list, show, or find tasks, execute SELECT statements only. Never change data for a read request.
- Execute INSERT, UPDATE, or DELETE only when the user explicitly requests that change.
- Order task results by created_at DESC and limit each result set to 10 rows.
- After a requested change, verify it with a SELECT query.
- If a requested task does not exist, respond with "Task not found."
- Return task results as a table with columns: id, title, description, status, created_at.
- When creating a task without a description, derive one from its title.

Table schema: tasks(id, title, description, status, created_at). Status values are pending, in_progress, and completed.
"""

@st.cache_resource #deecorator:  it will not recreate the agent on every run, improving performance.

def get_agent():
        agent = create_agent(
                model=llm,
                tools=tools,
                checkpointer=InMemorySaver(),  # Use an in-memory saver for conversation state
                system_prompt=system_prompt
        )
        return agent

agent = get_agent()  # Initialize the agent

st.subheader(" TaskBot - Manage your Tasks")  # Display a subheader in the Streamlit app


if "messages" not in st.session_state:  # Check if the session state has a "messages" key
    st.session_state.messages = []  # Initialize an empty list for messages in the session state

for message in st.session_state.messages:  # Iterate through the messages in the session state
    with st.chat_message(message["role"]):  # Create a chat message for each message in the session state
        st.markdown(message["content"])  # Display the content of the message in the chat interface


prompt = st.chat_input("Ask anything related to your tasks ")  # Create a text area for user input

if prompt:  # If the user has entered a prompt
    st.chat_message("user").markdown(prompt)  # Display the user's message in the chat interface
    st.session_state.messages.append({"role": "user", "content": prompt})  # Append the user's message to the session state
    with st.chat_message("assistant"):  # Create a chat message for the assistant's response
          with st.spinner("Thinking..."):  # Show a spinner while the agent processes the request
                response = agent.invoke(
                        {
                        "messages": [{"role": "user", "content": prompt}]
                        },
                        { "configurable": {"thread_id": "1" } }  # Specify the thread ID for the conversation context.
                )
                result =  response["messages"][-1].content # Extract the agent's response from the messages
                st.markdown(result)  # Display the agent's response in the chat interface
                st.session_state.messages.append({"role": "assistant", "content": result})  # Append the assistant's message to the session state
