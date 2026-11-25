"""Reusable Streamlit UI components for ActiPulse AI - Premium Sports-Tech Design."""

from __future__ import annotations

import html
from pathlib import Path

import streamlit as st

from modules import NON_MEDICAL_DISCLAIMER


def load_custom_css(css_path: str | Path = Path("assets") / "style.css") -> None:
    """Inject the premium sports-tech stylesheet into the Streamlit page."""
    path = Path(css_path)
    if path.exists():
        css_content = path.read_text(encoding="utf-8")
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)


def render_page_hero(eyebrow: str, title: str, subtitle: str) -> None:
    """Render a premium sports-tech hero header with athletic styling."""
    st.markdown(
        f"""
        <div class="ap-hero ap-pattern-bg">
            <div class="ap-hero-eyebrow">{html.escape(eyebrow).upper()}</div>
            <h1>{html.escape(title).upper()}</h1>
            <p>{html.escape(subtitle)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_card(label: str, value: str, hint: str, icon: str = "📊") -> None:
    """Render a premium athletic performance KPI metric card."""
    st.markdown(
        f"""
        <div class="ap-card">
            <div class="ap-kpi-label">
                <span class="ap-icon-neon">{html.escape(icon)}</span>
                {html.escape(label).upper()}
            </div>
            <div class="ap-kpi-value ap-kpi-highlight">{html.escape(value)}</div>
            <div class="ap-kpi-hint">{html.escape(hint)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stat_card(label: str, value: str, unit: str, change: str | None = None) -> None:
    """Render a large athletic performance statistic card."""
    change_html = f'<div class="ap-kpi-badge">↑ {html.escape(change)}</div>' if change else ""
    
    st.markdown(
        f"""
        <div class="ap-card ap-fade-in">
            <div class="ap-kpi-label">{html.escape(label).upper()}</div>
            <div style="display: flex; align-items: baseline; gap: 0.5rem; margin-bottom: 0.5rem;">
                <div class="ap-kpi-value">{html.escape(value)}</div>
                <div style="font-size: 1rem; color: var(--ap-grey-light); font-weight: 600;">{html.escape(unit)}</div>
            </div>
            {change_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_placeholder_section(
    title: str,
    description: str,
    process_badge: str,
    planned_capabilities: list[str],
) -> None:
    """Render a structured placeholder card for upcoming features."""
    items_html = "".join(
        f"<li style='margin-bottom:0.4rem; color:#9CA3AF; font-size:0.9rem;'>{html.escape(item)}</li>"
        for item in planned_capabilities
    )
    st.markdown(
        f"""
        <div class="ap-card" style="margin-bottom: 1.5rem;">
            <div style="display:flex; justify-content:space-between; align-items:center; gap:1rem; flex-wrap:wrap; margin-bottom:0.75rem;">
                <div class="ap-section-title" style="margin:0;">{html.escape(title)}</div>
                <span class="ap-badge-neon">{html.escape(process_badge)}</span>
            </div>
            <p class="ap-section-desc" style="margin-bottom:1rem;">{html.escape(description)}</p>
            <ul style="margin:0; padding-left:1.5rem;">
                {items_html}
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_non_medical_disclaimer() -> None:
    """Render the mandatory non-medical interpretation notice."""
    st.markdown(
        f"""
        <div class="ap-disclaimer">
            <strong>⚠️ ACTIVITY DIARY SCOPE:</strong> {html.escape(NON_MEDICAL_DISCLAIMER)}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_feature_card(icon: str, title: str, description: str, status: str = "active") -> None:
    """Render a feature card with athletic styling."""
    status_badge = '<span class="ap-badge-neon">ACTIVE</span>' if status == "active" else '<span class="ap-badge-neon">COMING SOON</span>'
    
    st.markdown(
        f"""
        <div class="ap-card" style="text-align: center; padding: 2rem 1.5rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem; color: var(--ap-green-neon);">{icon}</div>
            <div class="ap-section-title" style="margin-bottom: 0.75rem;">{html.escape(title).upper()}</div>
            <p class="ap-section-desc" style="margin-bottom: 1rem; font-size:0.85rem;">{html.escape(description)}</p>
            {status_badge}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stat_badge(label: str, value: str, color: str = "neon") -> None:
    """Render an inline stat badge with athletic styling."""
    badge_class = "ap-badge-neon" if color == "neon" else "ap-badge-success"
    
    st.markdown(
        f"""
        <div class="{badge_class}" style="display: inline-flex; margin: 0.25rem;">
            <span style="font-weight: 600;">{html.escape(label)}:</span>
            <span style="font-weight: 800; margin-left: 0.4rem;">{html.escape(value)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_athletic_header(title: str, subtitle: str | None = None) -> None:
    """Render a bold athletic section header."""
    subtitle_html = f'<p class="ap-section-desc">{html.escape(subtitle)}</p>' if subtitle else ""
    
    st.markdown(
        f"""
        <div style="margin: 2rem 0 1.5rem 0;">
            <h2 class="ap-section-title" style="font-size: 1.75rem; margin-bottom: 0.5rem; letter-spacing: -0.02em;">
                {html.escape(title).upper()}
            </h2>
            {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_progress_ring(percentage: float, label: str, color: str = "neon") -> None:
    """Render a circular progress indicator with athletic styling."""
    # SVG circle progress
    radius = 45
    circumference = 2 * 3.14159 * radius
    offset = circumference - (percentage / 100) * circumference
    stroke_color = "#AFFA00" if color == "neon" else "#CFED89"
    
    st.markdown(
        f"""
        <div class="ap-card" style="text-align: center; padding: 2rem 1rem;">
            <svg width="120" height="120" style="transform: rotate(-90deg);">
                <circle cx="60" cy="60" r="{radius}" fill="none" stroke="#2A2A2A" stroke-width="8"/>
                <circle cx="60" cy="60" r="{radius}" fill="none" stroke="{stroke_color}" stroke-width="8"
                        stroke-dasharray="{circumference}" stroke-dashoffset="{offset}"
                        stroke-linecap="round" style="transition: stroke-dashoffset 0.5s ease;"/>
                <text x="60" y="65" fill="#FFFFFF" font-size="20" font-weight="800" 
                      text-anchor="middle" transform="rotate(90 60 60)">{percentage:.0f}%</text>
            </svg>
            <div class="ap-kpi-label" style="margin-top: 1rem; justify-content: center;">
                {html.escape(label).upper()}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
