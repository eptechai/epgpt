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
   
def save_uploadedfiles(uploadedfiles, state):
    global RAWDATAPATH
    file_route = []
    for file in uploadedfiles:
        filename = os.path.join(RAWDATAPATH, file.name)
        if filename not in state:
            with open(filename, "wb") as f:

                f.write(file.getbuffer())

                with st.spinner(text="Loading . . ."):
                    time.sleep(3)
            st.write(f"File is uploaded in {filename}")
            file_route.append(filename)
        else:
            st.write(f"File {file.name} is alredy uploaded") 

    

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
    input_files = st.file_uploader("Upload a your files", accept_multiple_files=True)
    if st.button("Upload"):
        print(input_files)
        files_state = st.session_state.files
        uploaded_files = save_uploadedfiles(input_files, files_state)
        st.session_state.files.extend(uploaded_files)
             

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
            response = requests.post('http://52.90.22.153:8000/api/conversation/1234/message', json={"prompt":prompt})
            full_response = response.json()["data"]["response"]
            message_placeholder.markdown(full_response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})