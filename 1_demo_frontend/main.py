import os
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

RAWDATAPATH = "temp"

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
   
def save_uploadedfile(uploadedfile):
    global RAWDATAPATH
    with open(os.path.join(RAWDATAPATH, uploadedfile.name), "wb") as f:

        f.write(uploadedfile.getbuffer())

        with st.spinner(text="Cargando . . ."):
            time.sleep(3)

    file_route = os.path.join(RAWDATAPATH, uploadedfile.name)

    print(file_route)

    return file_route


with st.sidebar:

    add_bg_from_local('static/img/valere.jpeg')
    tab3, tab4 = st.tabs(["History", "Settings"])
    with tab3:
        st.title("Assistant History")
    with tab4:
        st.title("Assistant Settings")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "I'm Erick. How can I help you?"}]
if "files" not in st.session_state:
    st.session_state.files = []


with tab1:
    st.title("Erick")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

with tab2:
    st.header("Share your Files")
    input_file = st.file_uploader("Upload a your files", accept_multiple_files=False)
    if st.button("Upload"):
        if input_file is not None and input_file not in st.session_state.files:
            input_files = save_uploadedfile(input_file)
            st.write(f"File is uploaded in {input_files}")
            st.session_state.files.append(input_file.name)
        else:
            st.write(f"File {input_file.name} is alredy uploaded")      

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
            response = requests.post('http://127.0.0.1:8000/api/conversation/1234/message', json={"prompt":prompt})
            full_response = response.json()["data"]["response"]
            message_placeholder.markdown(full_response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})