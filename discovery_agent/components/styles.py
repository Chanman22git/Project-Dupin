import streamlit as st


def inject_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');

    :root {
        --brown-primary: #8B7355;
        --brown-dark: #6B5740;
        --brown-light: #C4956A;
        --bg-warm: #FAFAF8;
        --bg-secondary: #F2EDE8;
        --bg-card: #FFFFFF;
        --text-primary: #3D3529;
        --text-secondary: #6B6156;
        --text-muted: #A89F91;
        --border-light: #E8E0D8;
        --success: #7A9E7E;
        --warning: #D4A056;
        --error: #C27C6E;
        --shadow-sm: 0 1px 3px rgba(59, 53, 41, 0.06);
        --shadow-md: 0 4px 12px rgba(59, 53, 41, 0.08);
        --shadow-lg: 0 8px 24px rgba(59, 53, 41, 0.1);
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
    }

    /* ── Global ── */
    .stApp {
        background-color: var(--bg-warm) !important;
        font-family: 'Inter', sans-serif !important;
    }

    .stApp > header {
        background-color: transparent !important;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid var(--border-light) !important;
    }

    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown span {
        color: var(--text-secondary) !important;
    }

    /* ── Typography ── */
    h1, h2, h3 {
        font-family: 'Playfair Display', serif !important;
        color: var(--text-primary) !important;
    }

    h1 { font-weight: 700 !important; letter-spacing: -0.02em !important; }
    h2 { font-weight: 600 !important; }
    h3 { font-weight: 600 !important; font-size: 1.15rem !important; }

    p, li, span, label, .stMarkdown {
        color: var(--text-primary) !important;
    }

    /* ── Buttons ── */
    .stButton > button[kind="primary"],
    button[data-testid="stFormSubmitButton"] > button {
        background-color: var(--brown-primary) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
        font-weight: 500 !important;
        padding: 0.5rem 1.25rem !important;
        transition: all 0.2s ease !important;
        box-shadow: var(--shadow-sm) !important;
    }

    .stButton > button[kind="primary"]:hover {
        background-color: var(--brown-dark) !important;
        box-shadow: var(--shadow-md) !important;
        transform: translateY(-1px) !important;
    }

    .stButton > button[kind="secondary"],
    .stButton > button:not([kind="primary"]) {
        background-color: transparent !important;
        color: var(--brown-primary) !important;
        border: 1.5px solid var(--border-light) !important;
        border-radius: var(--radius-sm) !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button[kind="secondary"]:hover,
    .stButton > button:not([kind="primary"]):hover {
        border-color: var(--brown-primary) !important;
        background-color: var(--bg-secondary) !important;
    }

    /* ── Cards / Containers ── */
    div[data-testid="stVerticalBlockBorderWrapper"] > div:has(> div[data-testid="stVerticalBlock"]) {
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border-light) !important;
        border-radius: var(--radius-md) !important;
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
        border-bottom: 2px solid var(--border-light) !important;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 0.75rem 1.25rem !important;
        font-weight: 500 !important;
        color: var(--text-muted) !important;
        border-bottom: 2px solid transparent !important;
        transition: all 0.2s ease !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: var(--brown-primary) !important;
    }

    .stTabs [aria-selected="true"] {
        color: var(--brown-primary) !important;
        border-bottom-color: var(--brown-primary) !important;
    }

    .stTabs [data-baseweb="tab-highlight"] {
        background-color: var(--brown-primary) !important;
    }

    /* ── Inputs ── */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea textarea {
        border: 1.5px solid var(--border-light) !important;
        border-radius: var(--radius-sm) !important;
        font-family: 'Inter', sans-serif !important;
        transition: border-color 0.2s ease !important;
    }

    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea textarea:focus {
        border-color: var(--brown-primary) !important;
        box-shadow: 0 0 0 2px rgba(139, 115, 85, 0.15) !important;
    }

    /* ── Select Slider ── */
    .stSlider > div > div > div > div {
        background-color: var(--brown-primary) !important;
    }

    /* ── Radio ── */
    .stRadio label span[data-testid="stMarkdownContainer"] {
        font-size: 0.9rem !important;
    }

    /* ── Chat ── */
    .stChatMessage {
        border-radius: var(--radius-md) !important;
        padding: 0.75rem 1rem !important;
        margin-bottom: 0.5rem !important;
    }

    [data-testid="stChatMessageContent"] {
        font-size: 0.95rem !important;
        line-height: 1.6 !important;
    }

    .stChatInput > div {
        border: 1.5px solid var(--border-light) !important;
        border-radius: var(--radius-md) !important;
    }

    .stChatInput > div:focus-within {
        border-color: var(--brown-primary) !important;
        box-shadow: 0 0 0 2px rgba(139, 115, 85, 0.15) !important;
    }

    /* ── Expander ── */
    .streamlit-expanderHeader {
        font-weight: 500 !important;
        color: var(--text-primary) !important;
        border-radius: var(--radius-sm) !important;
    }

    /* ── Metrics ── */
    [data-testid="stMetricValue"] {
        font-family: 'Playfair Display', serif !important;
        color: var(--brown-primary) !important;
        font-size: 2rem !important;
    }

    [data-testid="stMetricLabel"] {
        color: var(--text-muted) !important;
        font-size: 0.85rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }

    /* ── Code blocks (link display) ── */
    .stCode {
        border-radius: var(--radius-sm) !important;
        border: 1px solid var(--border-light) !important;
    }

    /* ── Divider ── */
    hr {
        border-color: var(--border-light) !important;
        opacity: 0.5 !important;
    }

    /* ── Alert boxes ── */
    .stAlert {
        border-radius: var(--radius-md) !important;
        border: none !important;
    }

    /* ── Form ── */
    [data-testid="stForm"] {
        border: 1.5px solid var(--border-light) !important;
        border-radius: var(--radius-md) !important;
        padding: 1.5rem !important;
        background-color: var(--bg-card) !important;
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
        background: var(--text-muted);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover { background: var(--brown-primary); }

    /* ── Custom component classes ── */
    .metric-card {
        background: var(--bg-card);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-md);
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
        font-family: 'Playfair Display', serif;
        font-size: 2rem;
        font-weight: 700;
        color: var(--brown-primary);
        margin: 0.25rem 0;
    }
    .metric-card .metric-label {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: var(--text-muted);
        margin-bottom: 0.25rem;
    }
    .metric-card .metric-icon {
        margin-bottom: 0.5rem;
    }

    .status-pill {
        display: inline-block;
        padding: 0.2rem 0.75rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.03em;
    }
    .status-pill.draft { background: var(--bg-secondary); color: var(--text-muted); }
    .status-pill.active { background: #E8F5E9; color: #2E7D32; }
    .status-pill.completed { background: #E3F2FD; color: #1565C0; }
    .status-pill.expired { background: #FBE9E7; color: #BF360C; }
    .status-pill.new { background: #FFF8E1; color: #F57F17; }

    .progress-ring-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.5rem;
    }
    .progress-ring-label {
        font-size: 0.8rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .empty-state {
        text-align: center;
        padding: 3rem 2rem;
        color: var(--text-muted);
    }
    .empty-state .empty-icon { margin-bottom: 1rem; opacity: 0.4; }
    .empty-state .empty-message {
        font-size: 1rem;
        line-height: 1.6;
    }
    .empty-state .empty-hint {
        font-size: 0.85rem;
        color: var(--text-muted);
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
        background: var(--bg-secondary);
        border-radius: var(--radius-sm);
        padding: 1rem 1.25rem;
        margin-bottom: 0.75rem;
    }
    .info-field .field-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: var(--text-muted);
        margin-bottom: 0.35rem;
    }
    .info-field .field-value {
        font-size: 0.95rem;
        color: var(--text-primary);
        line-height: 1.5;
    }

    .persona-card {
        background: var(--bg-card);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-md);
        padding: 1rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 0.5rem;
    }
    .persona-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        font-size: 1rem;
        color: white;
        flex-shrink: 0;
    }
    .persona-info .persona-name {
        font-weight: 600;
        font-size: 0.95rem;
        color: var(--text-primary);
    }
    .persona-info .persona-role {
        font-size: 0.8rem;
        color: var(--text-muted);
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
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .status-flow .flow-dot.done {
        background: var(--success);
        color: white;
    }
    .status-flow .flow-dot.current {
        background: var(--brown-primary);
        color: white;
        box-shadow: 0 0 0 4px rgba(139, 115, 85, 0.2);
    }
    .status-flow .flow-dot.pending {
        background: var(--bg-secondary);
        color: var(--text-muted);
        border: 2px solid var(--border-light);
    }
    .status-flow .flow-line {
        width: 40px;
        height: 2px;
        background: var(--border-light);
    }
    .status-flow .flow-line.done {
        background: var(--success);
    }
    .status-flow .flow-label {
        font-size: 0.75rem;
        color: var(--text-muted);
        margin-top: 0.25rem;
    }

    .feature-preview-card {
        background: var(--bg-card);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-md);
        padding: 1.5rem;
        text-align: center;
        box-shadow: var(--shadow-sm);
    }
    .feature-preview-card .feature-icon { margin-bottom: 0.75rem; opacity: 0.6; }
    .feature-preview-card .feature-title {
        font-family: 'Playfair Display', serif;
        font-size: 1rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.4rem;
    }
    .feature-preview-card .feature-desc {
        font-size: 0.85rem;
        color: var(--text-muted);
        line-height: 1.5;
    }

    /* ── Improvement cards ── */
    .improvement-card {
        border-left: 4px solid var(--border-light);
        padding-left: 1rem;
        margin-bottom: 0.5rem;
    }
    .improvement-card.new_info { border-left-color: #1565C0; }
    .improvement-card.correction { border-left-color: var(--error); }
    .improvement-card.gap { border-left-color: var(--warning); }
    .improvement-card.conflicting_assumption { border-left-color: #7B1FA2; }

    </style>
    """, unsafe_allow_html=True)
