import streamlit as st

# ── Dupin Color Constants ──
COGNAC = "#C4823A"
COGNAC_LIGHT = "#E8B87A"
COGNAC_DARK = "#965E25"
CHARCOAL = "#3D3D35"
SMOKE = "#8C8878"
FAINT = "#B8B4A8"
PARCHMENT = "#F0EDE6"
AGED_PAPER = "#E8E3D8"
BORDER = "#D0CAC0"
PATINA = "#5C7A6E"
PATINA_LIGHT = "#8FAF9F"
ALERT = "#A64B2A"
NEUTRAL_50 = "#FAF8F5"

# ── SVG Icon Library ──

ICONS = {
    "magnifier": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>',
    "chat": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>',
    "document": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>',
    "users": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
    "chart": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>',
    "link": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>',
    "lightbulb": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18h6"/><path d="M10 22h4"/><path d="M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg>',
    "warning": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
    "settings": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>',
    "check": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>',
    "clock": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
    "plus": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>',
    "folder": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>',
    "target": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>',
    "layers": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>',
    "arrow_left": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>',
    "pipe": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4 18c0-2.2 1.8-4 4-4h4c2.2 0 4-1.8 4-4V6"/><circle cx="16" cy="5" r="2"/><path d="M2 20h4"/></svg>',
}


def icon(name, size=20, color=COGNAC):
    """Return an SVG icon string."""
    template = ICONS.get(name, "")
    return template.format(size=size, color=color)


def render_hero_banner(title, subtitle=""):
    """Render a decorative hero banner with Dupin-themed illustration."""
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {AGED_PAPER} 0%, {PARCHMENT} 50%, {AGED_PAPER} 100%);
        border-radius: 16px;
        padding: 2.5rem 2.5rem 2rem;
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden;
        border: 1px solid {BORDER};
    ">
        <div style="position: absolute; right: 2rem; top: 50%; transform: translateY(-50%); opacity: 0.06;">
            <svg width="180" height="180" viewBox="0 0 180 180" fill="none">
                <circle cx="90" cy="90" r="80" stroke="{CHARCOAL}" stroke-width="2"/>
                <circle cx="90" cy="90" r="55" stroke="{CHARCOAL}" stroke-width="1.5"/>
                <circle cx="90" cy="90" r="30" stroke="{CHARCOAL}" stroke-width="1"/>
                <line x1="90" y1="10" x2="90" y2="170" stroke="{CHARCOAL}" stroke-width="0.5"/>
                <line x1="10" y1="90" x2="170" y2="90" stroke="{CHARCOAL}" stroke-width="0.5"/>
                <line x1="30" y1="30" x2="150" y2="150" stroke="{CHARCOAL}" stroke-width="0.5"/>
                <line x1="150" y1="30" x2="30" y2="150" stroke="{CHARCOAL}" stroke-width="0.5"/>
            </svg>
        </div>
        <div style="position: relative; z-index: 1;">
            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem;">
                {icon("magnifier", 32, COGNAC)}
                <h1 style="margin: 0 !important; padding: 0 !important; font-size: 2.25rem !important;">{title}</h1>
            </div>
            <p style="color: {SMOKE} !important; font-size: 1.05rem; margin: 0; max-width: 500px; line-height: 1.6;">
                {subtitle}
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_metric_card(icon_name, label, value, color=COGNAC):
    """Render a styled metric card with icon."""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">{icon(icon_name, 28, color)}</div>
        <div class="metric-label">{label}</div>
        <div class="metric-value" style="color: {color};">{value}</div>
    </div>
    """, unsafe_allow_html=True)


def render_status_pill(status):
    """Render a colored status badge."""
    return f'<span class="status-pill {status}">{status.replace("_", " ").title()}</span>'


def render_persona_card(name, role="", department=""):
    """Render a persona card with generated avatar."""
    initials = "".join(w[0].upper() for w in name.split()[:2]) if name else "?"
    avatar_colors = [COGNAC, PATINA, COGNAC_DARK, ALERT, "#5F5C52", PATINA_LIGHT]
    color = avatar_colors[hash(name) % len(avatar_colors)]
    dept_line = f'<span style="font-size:0.75rem; color:{FAINT};">  {department}</span>' if department else ""
    st.markdown(f"""
    <div class="persona-card">
        <div class="persona-avatar" style="background-color: {color};">{initials}</div>
        <div class="persona-info">
            <div class="persona-name">{name}</div>
            <div class="persona-role">{role}{dept_line}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_progress_ring(percent, label="Complete"):
    """Render a circular progress indicator."""
    percent = max(0, min(100, percent))
    circumference = 2 * 3.14159 * 36
    offset = circumference - (percent / 100) * circumference
    color = PATINA if percent >= 75 else COGNAC if percent >= 40 else ALERT

    st.markdown(f"""
    <div class="progress-ring-container">
        <svg width="90" height="90" viewBox="0 0 90 90">
            <circle cx="45" cy="45" r="36" fill="none" stroke="{BORDER}" stroke-width="6"/>
            <circle cx="45" cy="45" r="36" fill="none" stroke="{color}" stroke-width="6"
                    stroke-dasharray="{circumference}" stroke-dashoffset="{offset}"
                    stroke-linecap="round" transform="rotate(-90 45 45)"
                    style="transition: stroke-dashoffset 0.5s ease;"/>
            <text x="45" y="45" text-anchor="middle" dominant-baseline="central"
                  fill="{CHARCOAL}" font-family="Playfair Display, serif"
                  font-size="18" font-weight="700">{percent}%</text>
        </svg>
        <div class="progress-ring-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)


def render_empty_state(icon_name, message, hint=""):
    """Render an illustrated empty state."""
    hint_html = f'<div class="empty-hint">{hint}</div>' if hint else ""
    st.markdown(f"""
    <div class="empty-state">
        <div class="empty-icon">{icon(icon_name, 56, FAINT)}</div>
        <div class="empty-message">{message}</div>
        {hint_html}
    </div>
    """, unsafe_allow_html=True)


def render_section_header(icon_name, title, color=COGNAC):
    """Render a section header with icon."""
    st.markdown(f"""
    <div class="section-header">
        {icon(icon_name, 22, color)}
        <h3>{title}</h3>
    </div>
    """, unsafe_allow_html=True)


def render_info_field(label, value, placeholder="Not set"):
    """Render a styled info field."""
    display_val = value if value else f'<em style="color:{FAINT};">{placeholder}</em>'
    st.markdown(f"""
    <div class="info-field">
        <div class="field-label">{label}</div>
        <div class="field-value">{display_val}</div>
    </div>
    """, unsafe_allow_html=True)


def render_status_flow(current_status):
    """Render a visual status flow: draft -> active -> completed."""
    steps = ["draft", "active", "completed"]
    current_idx = steps.index(current_status) if current_status in steps else 0

    html = '<div class="status-flow">'
    for i, step in enumerate(steps):
        if i < current_idx:
            dot_class = "done"
            icon_html = icon("check", 14, "white")
        elif i == current_idx:
            dot_class = "current"
            icon_html = str(i + 1)
        else:
            dot_class = "pending"
            icon_html = str(i + 1)

        html += f'''
        <div class="flow-step" style="display:flex;flex-direction:column;align-items:center;">
            <div class="flow-dot {dot_class}">{icon_html}</div>
            <div class="flow-label">{step.title()}</div>
        </div>
        '''
        if i < len(steps) - 1:
            line_class = "done" if i < current_idx else ""
            html += f'<div class="flow-line {line_class}"></div>'

    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def render_feature_preview_card(icon_name, title, description):
    """Render a feature preview card for coming-soon features."""
    st.markdown(f"""
    <div class="feature-preview-card">
        <div class="feature-icon">{icon(icon_name, 36, COGNAC)}</div>
        <div class="feature-title">{title}</div>
        <div class="feature-desc">{description}</div>
    </div>
    """, unsafe_allow_html=True)
