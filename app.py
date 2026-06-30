import streamlit as st
import requests

# 1. Page Configuration Setup
st.set_page_config(page_title="AI Chat Assistant", page_icon="🤖")
st.title("🤖 Production AI Chatbot")
st.caption("Powered by FastAPI, Streamlit, and Meta-Llama-3")

# 2. Define the URL where your FastAPI server is running
FASTAPI_URL =  "http://127.0.0.1:8000/chat"

# 3. Create a unique session ID for this user so history doesn't mix up
if "user_id" not in st.session_state:
    st.session_state.user_id = "user_mayur_10"

# 4. Initialize a UI-only visual chat history list
if "ui_messages" not in st.session_state:
    st.session_state.ui_messages = []

# 5. Display all previous messages on the screen neatly
for message in st.session_state.ui_messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 6. Capture new input from the chat text box
user_input = st.chat_input("Type your message here...")

if user_input:
    # Render the user's message on the screen immediately
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.ui_messages.append({"role": "user", "content": user_input})

    # Prepare the exact JSON package your FastAPI expects
    payload = {
        "user_id": st.session_state.user_id,
        "prompt": user_input
    }

    # Send the package over the network and wait for the response
    with st.spinner("AI is thinking..."):
        try:
            response = requests.post(FASTAPI_URL, json=payload)
            
            if response.status_code == 200:
                # Extract the response text string
                ai_text = response.json().get("response")
                
                # Render the AI's response on the UI screen
                with st.chat_message("assistant"):
                    st.write(ai_text)
                st.session_state.ui_messages.append({"role": "assistant", "content": ai_text})
            else:
                st.error(f"Backend Server Error: Status Code {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            st.error("Could not connect to FastAPI! Is your backend server running?")
