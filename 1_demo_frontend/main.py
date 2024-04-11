import openai
from PIL import Image
import streamlit as st
import time
import base64

import requests


im = Image.open("static/img/valere.jpeg")
st.set_page_config(
    page_title="Smart Document Analyzer",
    page_icon=im,
    layout="wide",
)



tab1, tab2 = st.tabs(["Smart Assistant", "Document Analyzer"])

def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
    f"""
    <style>
    [data-testid=stSidebar] {{
        background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
        background-size: 50%;
        background-repeat: no-repeat
    }}
    </style>
    """,
    unsafe_allow_html=True
    )
   



with st.sidebar:

    add_bg_from_local('static/img/valere.jpeg')
    tab3, tab4 = st.tabs(["History", "Settings"])
    with tab3:
        st.title("Assistant History")
    with tab4:
        st.title("Assistant Settings")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "I'm Erick. How can I help you?"}]

with tab1:
    st.title("Erick")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container

    with tab1:
        with st.chat_message("user"):
            st.markdown(prompt)
        # Display assitant message in chat message container
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            # Simulate stream of response with milliseconds delay
            with requests.post('http://127.0.0.1:8000/api/conversation/1234/message', stream=True, json={"prompt":prompt}) as r:
                for chunk in r.iter_content(10):
                    #get content in response
                    print(chunk)
                    full_response += chunk.decode("utf-8")
                # Add a blinking cursor to simulate typing
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})