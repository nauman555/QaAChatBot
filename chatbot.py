import os
from pyexpat.errors import messages
from turtle import st
import getpass
import streamlit as st

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()



api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    api_key = getpass.getpass("Enter your Google AI API key: ")
    os.environ["GOOGLE_API_KEY"] = api_key

llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash"

)

st.title("Google Gemini Chatbot")
st.markdown("This is a simple chatbot using Google Gemini API.")

if "messages" not in st.session_state:
    st.session_state.messages=[]

    
for message in st.session_state.messages:
    role = message["role"]
    content = message["content"]
    st.chat_message(role).markdown(content)

   


query = st.chat_input("Ask me anything:")   
if query:
        st.session_state.messages.append({"role": "user", "content": query})    
        st.chat_message("user").markdown(query)
        with st.spinner("Generating response..."):
            response = llm.invoke(query)
            st.session_state.messages.append({"role": "assistant", "content": response.content[0]['text']})
            st.chat_message("assistant").markdown(response.content[0]['text'])