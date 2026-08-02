import streamlit as st
from pathlib import Path
from chat import ChatBot
from components.header import render_header
from components.sidebar import render_sidebar
from components.chat import render_chat
from utils.mock_data import INITIAL_MESSAGES
st.set_page_config(
    page_title="Meritech AI Knowledge Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)
import base64
def get_base64_image(image_path):
    if image_path.exists():
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")
    return ""
def load_css():
    css_path = Path(__file__).parent / "assets" / "style.css"
    bg_path = Path(__file__).parent / "assets" / "chat_background.jpg"
    
    with open(css_path) as f:
        css_content = f.read()
        
    if bg_path.exists():
        bg_base64 = get_base64_image(bg_path)
        css_content += f"""
        :root {{
            --chat-bg-image: url("data:image/jpeg;base64,{bg_base64}");
        }}
        """   
    try:
        st.html(f"<style>{css_content}</style>")
    except AttributeError:
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

def init_state():
    # Initialize your backend ChatBot instance once
    if "chatbot" not in st.session_state:
        st.session_state.chatbot = ChatBot()
        
    # Track the active session key
    if "current_session_id" not in st.session_state:
        st.session_state.current_session_id = ""

    # Track distinct chat history rooms dynamically
    if "messages_dict" not in st.session_state:
        st.session_state.messages_dict = {}

    # Maintain the sidebar tracking array
    if "chat_sessions" not in st.session_state:
        st.session_state.chat_sessions = []


def main():
    load_css()
    init_state()

    render_header()
    render_sidebar()
    
    # Pass the backend instance down into your chat rendering window
    render_chat(st.session_state.chatbot)


if __name__ == "__main__":
    main()
