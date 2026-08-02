import streamlit as st
import base64
from pathlib import Path

def _get_base64_image(filename):
    img_path = Path(__file__).parent.parent / "assets" / filename
    if img_path.exists():
        with open(img_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return None

USER_B64 = _get_base64_image("user.jpg")
USER_AVATAR_HTML = f'<img src="data:image/jpeg;base64,{USER_B64}" class="avatar-circle" style="object-fit: cover; width: 34px; height: 34px; border-radius: 50%; border: 2px solid var(--accent-green);">' if USER_B64 else '<div class="avatar-circle">HJ</div>'


def render_header():
    st.markdown(
        f"""
        <div class="brand-bar">
            <div class="brand-left">
                <div class="brand-logo">
                    <svg width="32" height="20" viewBox="0 0 100 62" xmlns="http://www.w3.org/2000/svg">
                        <polygon points="10,38 22,26 34,38 22,50" fill="#003B82"/>
                        <polygon points="24,24 36,12 48,24 36,36" fill="#009F4D"/>
                        <polygon points="38,38 50,26 62,38 50,50" fill="#003B82"/>
                        <polygon points="52,24 64,12 76,24 64,36" fill="#009F4D"/>
                        <polygon points="66,38 78,26 90,38 78,50" fill="#003B82"/>
                    </svg>
                </div>
                <div>
                    <div class="brand-title">AI <span>KNOWLEDGE ASSISTANT</span></div>
                    <div class="brand-sub">Smart Answers. Trusted Information.</div>
                </div>
            </div>
            <div class="brand-right">
                <span>🔍&nbsp; Search documents...</span>
                <span>☀️</span>
                <div class="avatar-chip">
                    {USER_AVATAR_HTML}
                    <div>
                        <div class="avatar-name">User</div>
                        <div class="avatar-role">Admin</div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
