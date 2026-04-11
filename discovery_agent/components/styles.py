import streamlit as st


def inject_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Playfair+Display:ital,wght@0,700;1,400&family=Courier+Prime&display=swap');

    :root {
        /* Backgrounds */
        --dupin-bg: #F0EDE6;
        --dupin-surface: #E8E3D8;
        --dupin-bg-dark: #1E1D18;
        --dupin-surface-dark: #2C2A24;

        /* Text */
        --dupin-text: #3D3D35;
        --dupin-text-muted: #8C8878;
        --dupin-text-faint: #B8B4A8;

        /* Accent */
        --dupin-cognac: #C4823A;
        --dupin-cognac-light: #E8B87A;
        --dupin-cognac-dark: #965E25;

        /* Semantic */
        --dupin-success: #5C7A6E;
        --dupin-success-light: #8FAF9F;
        --dupin-error: #A64B2A;

        /* Borders */
        --dupin-border: #D0CAC0;
        --dupin-border-dark: #3D3D35;

        /* Neutral ramp */
        --dupin-neutral-50: #FAF8F5;
        --dupin-neutral-300: #D0CAC0;
        --dupin-neutral-600: #5F5C52;
        --dupin-neutral-800: #2C2A24;

        /* Fonts */
        --dupin-font-display: 'Playfair Display', Georgia, serif;
        --dupin-font-body: 'Inter', 'Helvetica Neue', sans-serif;
        --dupin-font-mono: 'Courier Prime', 'Courier New', monospace;

        /* Shadows (warm-tinted) */
        --shadow-sm: 0 1px 3px rgba(61,61,53,0.08);
        --shadow-md: 0 4px 12px rgba(61,61,53,0.10);
        --shadow-lg: 0 8px 24px rgba(61,61,53,0.12);
        --shadow-accent: 0 0 0 3px rgba(196,130,58,0.25);

        /* Radius */
        --radius-sm: 4px;
        --radius-md: 6px;
        --radius-lg: 10px;
        --radius-xl: 16px;
    }

    /* ── Global ── */
    .stApp {
        background-color: var(--dupin-bg) !important;
        font-family: var(--dupin-font-body) !important;
    }

    .stApp > header {
        background-color: transparent !important;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background-color: var(--dupin-neutral-50) !important;
        border-right: 1px solid var(--dupin-border) !important;
    }

    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown span {
        color: var(--dupin-text-muted) !important;
    }

    /* ── Typography ── */
    h1 {
        font-family: var(--dupin-font-display) !important;
        color: var(--dupin-text) !important;
        font-weight: 700 !important;
        letter-spacing: -0.01em !important;
        line-height: 1.2 !important;
    }

    h2 {
        font-family: var(--dupin-font-display) !important;
        color: var(--dupin-text) !important;
        font-weight: 700 !important;
        letter-spacing: -0.01em !important;
        line-height: 1.2 !important;
    }

    h3 {
        font-family: var(--dupin-font-display) !important;
        color: var(--dupin-text) !important;
        font-weight: 700 !important;
        font-size: 1.25rem !important;
        line-height: 1.4 !important;
    }

    h4 {
        font-family: var(--dupin-font-display) !important;
        font-weight: 400 !important;
        font-style: italic !important;
        color: var(--dupin-text-muted) !important;
        line-height: 1.4 !important;
    }

    p, li, span, label, .stMarkdown {
        color: var(--dupin-text) !important;
    }

    /* ── Buttons ── */
    .stButton > button[kind="primary"],
    button[data-testid="stFormSubmitButton"] > button {
        background-color: var(--dupin-cognac) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-md) !important;
        font-family: var(--dupin-font-body) !important;
        font-weight: 500 !important;
        padding: 0.5rem 1.25rem !important;
        transition: all 0.2s ease !important;
        box-shadow: var(--shadow-sm) !important;
    }

    .stButton > button[kind="primary"]:hover {
        background-color: var(--dupin-cognac-dark) !important;
        box-shadow: var(--shadow-md) !important;
        transform: translateY(-1px) !important;
    }

    .stButton > button[kind="primary"]:active {
        box-shadow: var(--shadow-accent) !important;
    }

    .stButton > button[kind="secondary"],
    .stButton > button:not([kind="primary"]) {
        background-color: transparent !important;
        color: var(--dupin-text) !important;
        border: 1.5px solid var(--dupin-border) !important;
        border-radius: var(--radius-md) !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button[kind="secondary"]:hover,
    .stButton > button:not([kind="primary"]):hover {
        border-color: var(--dupin-cognac) !important;
        color: var(--dupin-cognac) !important;
        background-color: var(--dupin-surface) !important;
    }

    /* ── Cards / Containers ── */
    div[data-testid="stVerticalBlockBorderWrapper"] > div:has(> div[data-testid="stVerticalBlock"]) {
        background-color: var(--dupin-neutral-50) !important;
        border: 1px solid var(--dupin-border) !important;
        border-radius: var(--radius-lg) !important;
        box-shadow: var(--shadow-sm) !important;
        transition: all 0.25s ease !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"]:hover > div:has(> div[data-testid="stVerticalBlock"]) {
        box-shadow: var(--shadow-md) !important;
        transform: translateY(-2px);
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0 !important;
        border-bottom: 2px solid var(--dupin-border) !important;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 0.75rem 1.25rem !important;
        font-family: var(--dupin-font-body) !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        letter-spacing: 0.04em !important;
        color: var(--dupin-text-muted) !important;
        border-bottom: 2px solid transparent !important;
        transition: all 0.2s ease !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: var(--dupin-cognac) !important;
    }

    .stTabs [aria-selected="true"] {
        color: var(--dupin-cognac) !important;
        border-bottom-color: var(--dupin-cognac) !important;
    }

    .stTabs [data-baseweb="tab-highlight"] {
        background-color: var(--dupin-cognac) !important;
    }

    /* ── Inputs ── */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea textarea {
        border: 1.5px solid var(--dupin-border) !important;
        border-radius: var(--radius-md) !important;
        font-family: var(--dupin-font-body) !important;
        background-color: var(--dupin-neutral-50) !important;
        transition: border-color 0.2s ease !important;
    }

    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea textarea:focus {
        border-color: var(--dupin-cognac) !important;
        box-shadow: var(--shadow-accent) !important;
    }

    /* ── Select Slider ── */
    .stSlider > div > div > div > div {
        background-color: var(--dupin-cognac) !important;
    }

    /* ── Radio ── */
    .stRadio label span[data-testid="stMarkdownContainer"] {
        font-size: 0.875rem !important;
    }

    /* ── Chat ── */
    .stChatMessage {
        border-radius: var(--radius-lg) !important;
        padding: 0.75rem 1rem !important;
        margin-bottom: 0.5rem !important;
    }

    [data-testid="stChatMessageContent"] {
        font-family: var(--dupin-font-body) !important;
        font-size: 0.95rem !important;
        line-height: 1.6 !important;
    }

    .stChatInput > div {
        border: 1.5px solid var(--dupin-border) !important;
        border-radius: var(--radius-lg) !important;
        background-color: var(--dupin-neutral-50) !important;
    }

    .stChatInput > div:focus-within {
        border-color: var(--dupin-cognac) !important;
        box-shadow: var(--shadow-accent) !important;
    }

    /* ── Expander ── */
    .streamlit-expanderHeader {
        font-family: var(--dupin-font-body) !important;
        font-weight: 500 !important;
        color: var(--dupin-text) !important;
        border-radius: var(--radius-md) !important;
    }

    /* ── Metrics ── */
    [data-testid="stMetricValue"] {
        font-family: var(--dupin-font-display) !important;
        color: var(--dupin-cognac) !important;
        font-size: 2rem !important;
    }

    [data-testid="stMetricLabel"] {
        font-family: var(--dupin-font-body) !important;
        color: var(--dupin-text-muted) !important;
        font-size: 0.75rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.12em !important;
    }

    /* ── Code blocks ── */
    .stCode, code {
        font-family: var(--dupin-font-mono) !important;
        border-radius: var(--radius-md) !important;
        border: 1px solid var(--dupin-border) !important;
    }

    /* ── Divider ── */
    hr {
        border-color: var(--dupin-border) !important;
        opacity: 0.5 !important;
    }

    /* ── Alert boxes ── */
    .stAlert {
        border-radius: var(--radius-lg) !important;
        border: none !important;
    }

    /* ── Form ── */
    [data-testid="stForm"] {
        border: 1.5px solid var(--dupin-border) !important;
        border-radius: var(--radius-lg) !important;
        padding: 1.5rem !important;
        background-color: var(--dupin-neutral-50) !important;
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
        background: var(--dupin-text-muted);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover { background: var(--dupin-cognac); }

    /* ═══ Custom component classes ═══ */

    .metric-card {
        background: var(--dupin-neutral-50);
        border: 1px solid var(--dupin-border);
        border-radius: var(--radius-lg);
        padding: 1.25rem;
        text-align: center;
        box-shadow: var(--shadow-sm);
        transition: all 0.25s ease;
    }
    .metric-card:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-2px);
    }
    .metric-card .metric-value {
        font-family: var(--dupin-font-display);
        font-size: 2rem;
        font-weight: 700;
        color: var(--dupin-cognac);
        margin: 0.25rem 0;
    }
    .metric-card .metric-label {
        font-family: var(--dupin-font-body);
        font-size: 0.625rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: var(--dupin-text-muted);
        margin-bottom: 0.25rem;
    }
    .metric-card .metric-icon {
        margin-bottom: 0.5rem;
    }

    .status-pill {
        display: inline-block;
        padding: 0.2rem 0.75rem;
        border-radius: 9999px;
        font-family: var(--dupin-font-body);
        font-size: 0.625rem;
        font-weight: 500;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }
    .status-pill.draft { background: var(--dupin-surface); color: var(--dupin-text-muted); }
    .status-pill.active { background: #E0EDE7; color: var(--dupin-success); }
    .status-pill.completed { background: #E8E3D8; color: var(--dupin-neutral-600); }
    .status-pill.expired { background: #F2E0D6; color: var(--dupin-error); }
    .status-pill.new { background: #F5EBD8; color: var(--dupin-cognac-dark); }
    .status-pill.in_progress { background: #E0EDE7; color: var(--dupin-success); }

    .progress-ring-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.5rem;
    }
    .progress-ring-label {
        font-family: var(--dupin-font-body);
        font-size: 0.625rem;
        font-weight: 500;
        color: var(--dupin-text-muted);
        text-transform: uppercase;
        letter-spacing: 0.12em;
    }

    .empty-state {
        text-align: center;
        padding: 3rem 2rem;
        color: var(--dupin-text-muted);
    }
    .empty-state .empty-icon { margin-bottom: 1rem; opacity: 0.3; }
    .empty-state .empty-message {
        font-family: var(--dupin-font-body);
        font-size: 1rem;
        line-height: 1.6;
        color: var(--dupin-text-muted);
    }
    .empty-state .empty-hint {
        font-family: var(--dupin-font-body);
        font-size: 0.875rem;
        color: var(--dupin-text-faint);
        margin-top: 0.5rem;
    }

    .section-header {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        margin-bottom: 0.75rem;
    }
    .section-header h3 {
        margin: 0 !important;
        padding: 0 !important;
    }

    .info-field {
        background: var(--dupin-surface);
        border-radius: var(--radius-md);
        padding: 1rem 1.25rem;
        margin-bottom: 0.75rem;
    }
    .info-field .field-label {
        font-family: var(--dupin-font-body);
        font-size: 0.625rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: var(--dupin-text-muted);
        margin-bottom: 0.35rem;
    }
    .info-field .field-value {
        font-family: var(--dupin-font-body);
        font-size: 0.95rem;
        color: var(--dupin-text);
        line-height: 1.6;
    }

    .persona-card {
        background: var(--dupin-neutral-50);
        border: 1px solid var(--dupin-border);
        border-radius: var(--radius-lg);
        padding: 1rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 0.5rem;
    }
    .persona-avatar {
        width: 40px;
        height: 40px;
        border-radius: 9999px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: var(--dupin-font-display);
        font-weight: 700;
        font-size: 1rem;
        color: white;
        flex-shrink: 0;
    }
    .persona-info .persona-name {
        font-family: var(--dupin-font-body);
        font-weight: 600;
        font-size: 0.95rem;
        color: var(--dupin-text);
    }
    .persona-info .persona-role {
        font-family: var(--dupin-font-body);
        font-size: 0.8rem;
        color: var(--dupin-text-muted);
    }

    .status-flow {
        display: flex;
        align-items: center;
        gap: 0;
        margin: 1rem 0;
    }
    .status-flow .flow-step {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .status-flow .flow-dot {
        width: 32px;
        height: 32px;
        border-radius: 9999px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: var(--dupin-font-body);
        font-size: 0.75rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .status-flow .flow-dot.done {
        background: var(--dupin-success);
        color: white;
    }
    .status-flow .flow-dot.current {
        background: var(--dupin-cognac);
        color: white;
        box-shadow: var(--shadow-accent);
    }
    .status-flow .flow-dot.pending {
        background: var(--dupin-surface);
        color: var(--dupin-text-muted);
        border: 2px solid var(--dupin-border);
    }
    .status-flow .flow-line {
        width: 40px;
        height: 2px;
        background: var(--dupin-border);
    }
    .status-flow .flow-line.done {
        background: var(--dupin-success);
    }
    .status-flow .flow-label {
        font-family: var(--dupin-font-body);
        font-size: 0.625rem;
        font-weight: 500;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: var(--dupin-text-muted);
        margin-top: 0.25rem;
    }

    .feature-preview-card {
        background: var(--dupin-neutral-50);
        border: 1px solid var(--dupin-border);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        text-align: center;
        box-shadow: var(--shadow-sm);
    }
    .feature-preview-card .feature-icon { margin-bottom: 0.75rem; opacity: 0.5; }
    .feature-preview-card .feature-title {
        font-family: var(--dupin-font-display);
        font-size: 1rem;
        font-weight: 700;
        color: var(--dupin-text);
        margin-bottom: 0.4rem;
    }
    .feature-preview-card .feature-desc {
        font-family: var(--dupin-font-body);
        font-size: 0.875rem;
        color: var(--dupin-text-muted);
        line-height: 1.6;
    }

    .improvement-card {
        border-left: 4px solid var(--dupin-border);
        padding-left: 1rem;
        margin-bottom: 0.5rem;
    }
    .improvement-card.new_info { border-left-color: var(--dupin-cognac); }
    .improvement-card.correction { border-left-color: var(--dupin-error); }
    .improvement-card.gap { border-left-color: var(--dupin-cognac-light); }
    .improvement-card.conflicting_assumption { border-left-color: var(--dupin-success); }

    </style>
    """, unsafe_allow_html=True)
