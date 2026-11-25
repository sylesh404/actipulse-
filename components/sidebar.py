"""Sidebar navigation component for ActiPulse AI - Premium Sports-Tech Design."""

from __future__ import annotations

import streamlit as st

from modules import APP_NAME, APP_SUBTITLE, APP_VERSION
from modules.llm_provider import get_llm_manager

NAVIGATION_PAGES: tuple[tuple[str, str], ...] = (
    ("Home Dashboard", "🏠 Home Dashboard"),
    ("Upload Activity", "📤 Upload Activity"),
    ("Activity Analytics", "📊 Activity Analytics"),
    ("Activity Comparison", "⚖️ Activity Comparison"),
    ("Smart Timeline", "⏱️ Smart Timeline"),
    ("Pattern Detection", "🔍 Pattern Detection"),
    ("AI Activity Diary", "📝 AI Activity Diary"),
    ("AI Assistant", "💬 AI Assistant"),
    ("AI Settings", "⚙️ AI Settings"),
    ("Advanced Reports", "📊 Advanced Reports"),
)


def render_sidebar() -> str:
    """Render the premium sports-tech branded sidebar navigation."""
    with st.sidebar:
        # Premium Athletic Brand Header
        st.markdown(
            f"""
            <div class="ap-brand">
                <span class="ap-brand-badge">AI-POWERED ANALYTICS</span>
                <div class="ap-brand-title">ACTIPULSE AI</div>
                <div class="ap-brand-subtitle">Movement Intelligence Platform</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        labels = [label for _, label in NAVIGATION_PAGES]
        label_to_key = {label: key for key, label in NAVIGATION_PAGES}
        
        # Handle programmatic navigation from session state
        default_index = 0
        if "selected_page" in st.session_state:
            target_page = st.session_state["selected_page"]
            for idx, (key, label) in enumerate(NAVIGATION_PAGES):
                if key == target_page:
                    default_index = idx
                    break
            del st.session_state["selected_page"]

        selected_label = st.radio(
            "Navigation",
            options=labels,
            index=default_index,
            label_visibility="collapsed",
            key="sidebar_nav_selection",
        )

        st.markdown("<hr style='border-color: #333333; margin: 1.5rem 0;'>", unsafe_allow_html=True)

        # AI Provider Status
        try:
            manager = get_llm_manager()
            statuses = manager.get_provider_status()
            configured_provider = manager.get_configured_provider()
            
            groq_icon = "✓" if statuses.get("groq", {}).connected else "✗"
            gemini_icon = "✓" if statuses.get("gemini", {}).connected else "✗"
            
            provider_display = configured_provider.upper() if configured_provider != "auto" else "AUTO"
            
            st.markdown(
                f"""
                <div style="font-size:0.75rem; color:#9CA3AF; line-height:1.8; font-weight:500;">
                    <div style="margin-bottom:0.5rem;"><strong style="color:#AFFA00;">VERSION</strong> {APP_VERSION}</div>
                    <div style="margin-bottom:0.5rem;"><strong style="color:#AFFA00;">AI MODE</strong> {provider_display}</div>
                    <div style="display:flex; gap:1rem; margin-bottom:0.5rem;">
                        <span><strong style="color:#AFFA00;">GROQ</strong> {groq_icon}</span>
                        <span><strong style="color:#AFFA00;">GEMINI</strong> {gemini_icon}</span>
                    </div>
                    <div><strong style="color:#AFFA00;">STATUS</strong> ONLINE</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        except Exception:
            st.markdown(
                f"""
                <div style="font-size:0.75rem; color:#9CA3AF; line-height:1.8; font-weight:500;">
                    <div><strong style="color:#AFFA00;">VERSION</strong> {APP_VERSION}</div>
                    <div><strong style="color:#AFFA00;">STATUS</strong> INITIALIZING...</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    return label_to_key[selected_label]
