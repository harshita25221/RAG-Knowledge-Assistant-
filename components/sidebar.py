import streamlit as st
from utils.mock_data import STATS, DOCUMENTS, CHAT_SESSIONS


def render_sidebar():
    with st.sidebar:
        # New chat shortcut
        st.markdown('<div class="sidebar-section-label">Shortcuts</div>', unsafe_allow_html=True)
        if st.button("＋  New Chat", type="primary", use_container_width=True):
            from datetime import datetime
            
            # 1. Generate a unique session identifier
            new_id = f"CHAT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # 2. Make sure state dictionaries are safely initialized
            if "chat_sessions" not in st.session_state:
                st.session_state.chat_sessions = []
            if "messages_dict" not in st.session_state:
                st.session_state.messages_dict = {}
                
            # 3. Set the active pointer and append the new structural map tracking entries
            st.session_state.current_session_id = new_id
            st.session_state.chat_sessions.insert(0, {"id": new_id, "active": True})
            st.session_state.messages_dict[new_id] = []
            
            # 4. Refresh page immediately to render the blank layout canvas
            st.rerun()

        # Stat cards
        # Calculate real-time dynamic numbers based on your actual data variables
        real_doc_count = len(DOCUMENTS)
        real_session_count = len(st.session_state.get("chat_sessions", []))

        # Calculate total queries across all session message histories safely
        real_query_count = 0
        if "messages_dict" in st.session_state:
            for session_id, messages in st.session_state.messages_dict.items():
                # Count only the messages sent by the user
                real_query_count += sum(1 for msg in messages if msg.get("role") == "user")

        # Map the real-time counts back into your layout loop variables
        dynamic_stats = [
            {"label": "Documents", "value": real_doc_count, "color": "#22C55E"},
            {"label": "Sessions", "value": real_session_count, "color": "#60A5FA"},
            {"label": "Queries", "value": real_query_count, "color": "#A78BFA"},
        ]

        # Render using your exact original HTML string templates and CSS classes
        stat_html = '<div class="stat-grid">'
        for s in dynamic_stats:
            stat_html += f"""
            <div class="stat-card">
                <div class="stat-value" style="color:{s['color']}">{s['value']}</div>
                <div class="stat-label">{s['label']}</div>
            </div>"""
        stat_html += "</div>"
        st.markdown(stat_html, unsafe_allow_html=True)

        # Upload
        st.markdown('<div class="sidebar-section-label">Upload Documents</div>', unsafe_allow_html=True)
        st.file_uploader(
            "Drag & drop files here",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=True,
            label_visibility="collapsed",
        )
        st.caption("Supports: PDF, DOCX, TXT (Max 50MB)")

        # Uploaded documents
        st.markdown('<div class="sidebar-section-label">Knowledge Base</div>', unsafe_allow_html=True)
        doc_html = ""
        for d in DOCUMENTS:
            badge_class = "badge-pdf" if d["type"] == "PDF" else "badge-docx"
            doc_html += f"""
            <div class="doc-row">
                <div class="doc-name">📄 {d['name']}</div>
                <div class="doc-meta">
                    <span class="badge {badge_class}">{d['type']}</span>
                    <span>{d['date']}</span>
                </div>
            </div>"""
        st.markdown(doc_html, unsafe_allow_html=True)

        # Chat sessions
        st.markdown('<div class="sidebar-section-label">Chat Sessions</div>', unsafe_allow_html=True)

# Checks if any sessions exist; if empty, shows a subtle placeholder note
        live_sessions = st.session_state.get("chat_sessions", CHAT_SESSIONS)
        active_id = st.session_state.get("current_session_id")

        if not live_sessions:
            st.markdown('<div style="color: #64748b; font-size: 0.85rem; padding: 10px 5px; font-style: italic;">No active sessions.</div>', unsafe_allow_html=True)
        else:
            for s in live_sessions:
                is_active = (s['id'] == active_id)
                btn_label = f"💬 {s['id']}" + ("  (Active)" if is_active else "")
                btn_type = "secondary"
                
                if st.button(btn_label, key=f"session_btn_{s['id']}", type=btn_type, use_container_width=True):
                    st.session_state.current_session_id = s['id']
                    st.rerun()
                    
        if st.button("🗑️  Clear All Sessions", type="primary", use_container_width=True):
            st.session_state.chat_sessions = []
            st.session_state.messages_dict = {}
            st.session_state.current_session_id = ""
            st.rerun()

