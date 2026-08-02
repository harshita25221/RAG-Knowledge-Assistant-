import streamlit as st
from datetime import datetime
from utils.mock_data import CANNED_ANSWERS, DEFAULT_ANSWER
from chat import ChatBot

import base64
from pathlib import Path

def _get_base64_image(filename):
    img_path = Path(__file__).parent.parent / "assets" / filename
    if img_path.exists():
        with open(img_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return None

# Load avatars once
BOT_B64 = _get_base64_image("bot.png")
USER_B64 = _get_base64_image("user.jpg")

BOT_AVATAR_HTML = f'<img src="data:image/png;base64,{BOT_B64}" class="bot-avatar-small" style="object-fit: cover;">' if BOT_B64 else '<div class="bot-avatar-small">🤖</div>'
USER_AVATAR_HTML = f'<img src="data:image/jpeg;base64,{USER_B64}" class="user-avatar-small" style="object-fit: cover;">' if USER_B64 else '<div class="user-avatar-small">HJ</div>'
BOT_HEADER_HTML = f'<img src="data:image/png;base64,{BOT_B64}" class="chat-bot-icon" style="object-fit: cover; width: 38px; height: 38px; border-radius: 50%;">' if BOT_B64 else '<div class="chat-bot-icon">🤖</div>'


def _bot_answer(question: str):
    """Very small keyword matcher so the demo chat feels alive."""
    q = question.lower()
    for keyword, answer in CANNED_ANSWERS.items():
        if keyword in q:
            sources = None
            if keyword == "sick":
                sources = [{"document": "Leave_Policy.docx", "page": "Page 5", "score": 0.92}]
            elif keyword == "leave":
                sources = [{"document": "Leave_Policy.docx", "page": "Page 2", "score": 0.89}]
            return answer, sources
    return DEFAULT_ANSWER, None


def _render_message(msg):
    role = msg["role"]
    time = msg.get("time", "")
    import re
    
    # Process the raw text into proper HTML before inserting into the DOM
    raw_content = msg["content"]
    # Bold
    parsed = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', raw_content)
    # Lists
    parsed = parsed.replace("\n- ", "<br>• ")
    # Newlines
    content_html = parsed.replace("\n", "<br>")
    
    html_str = ""
    if role == "user":
        html_str += f"""
            <div class="msg-row user">
                <div class="bubble user">
                    {content_html}
                    <div class="msg-time">{time}</div>
                </div>
                {USER_AVATAR_HTML}
            </div>
            """
    else:
        html_str += f"""
            <div class="msg-row assistant">
                {BOT_AVATAR_HTML}
                <div class="bubble assistant">
                    {content_html}
                    <div class="msg-time">{time}</div>
                </div>
            </div>
            """
        if msg.get("sources"):
            rows = ""
            for s in msg["sources"]:
                rows += f"""
                <tr>
                    <td>{s['document']}</td>
                    <td>{s['page']}</td>
                    <td class="score-pill">{s['score']:.2f}</td>
                </tr>"""
            html_str += f"""
                <div class="sources-card">
                    <div class="sources-title">🛈 Sources Used</div>
                    <table class="sources-table">
                        <tr><th>Document</th><th>Page</th><th>Relevance Score</th></tr>
                        {rows}
                    </table>
                </div>
                """
    return html_str


def render_chat(chatbot): # Lowercase parameter name to match python standards
    full_html = '<div class="chat-panel">'

    # Fetch active real-time session ID or use placeholder if none exists yet
    active_session = st.session_state.get("current_session_id", "No Active Session")

    # Header
    full_html += f"""
        <div class="chat-header">
            <div class="chat-header-left">
                {BOT_HEADER_HTML}
                <div>
                    <div class="chat-title">AI Chat Assistant</div>
                    <div class="chat-subtitle">Your intelligent knowledge companion</div>
                </div>
            </div>
            <div class="session-id-pill">Session ID: {active_session}</div>
        </div>
        """

    # Body - Pulls dynamically from the active chat room sequence array
    full_html += '<div class="chat-body">'
    active_messages = st.session_state.messages_dict.get(active_session, [])
    if not active_messages:
        welcome_msg = {
            "role": "assistant",
            "content": "Hey, I am Meritech AI Knowledge Assistant. Please write your queries in the inbox, I am here to help you!",
            "time": datetime.now().strftime("%I:%M %p")
        }
        full_html += _render_message(welcome_msg)
    else:
        for msg in active_messages:
            full_html += _render_message(msg)
    full_html += '</div>'

    full_html += '<div class="disclaimer">AI responses may not always be accurate. Please verify important information.</div>'
    full_html += '</div>'  # close chat-panel

    # Remove all newlines from the HTML string so Streamlit's markdown parser 
    # doesn't mistakenly apply block-level markdown parsing (like lists or code blocks) inside our HTML.
    safe_html = full_html.replace("\n", " ")
    
    st.markdown(safe_html, unsafe_allow_html=True)



    # Input
    # Input
    question = st.chat_input("Type your question here...")
    if question:
        # 1. Thread Watcher: If zero sessions exist, generate the initial baseline entry
        if not st.session_state.get("current_session_id"):
            new_id = f"CHAT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            st.session_state.current_session_id = new_id
            st.session_state.chat_sessions.insert(0, {"id": new_id, "active": True})
            st.session_state.messages_dict[new_id] = []

        active_session = st.session_state.current_session_id
        now = datetime.now().strftime("%I:%M %p")
        
        # 2. Append User query message log to active thread
        st.session_state.messages_dict[active_session].append(
            {"role": "user", "content": question, "time": now}
        )
        
        # 3. Stream data processing through your local Ollama backend model connection
        with st.spinner("Analyzing knowledge documents..."):
            try:
                # Calls your ChatBot backend instance method bot._ask(query, session_id)
                bot_response = chatbot._ask(query=question, session_id=active_session)
            except Exception as err:
                bot_response = f"Backend Connection Error: {err}"
            
        # 4. Append live model response back down into your layout loop
        st.session_state.messages_dict[active_session].append(
            {"role": "assistant", "content": bot_response, "time": now, "sources": None}
        )
        st.rerun()
