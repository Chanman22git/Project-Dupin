from __future__ import annotations
import streamlit as st
from components.graphics import (
    icon, render_section_header, render_empty_state,
    COGNAC, COGNAC_LIGHT, PATINA, SMOKE, CHARCOAL, FAINT, AGED_PAPER, BORDER, NEUTRAL_50,
)

ARTIFACT_TYPE_CONFIG = {
    "document": {"label": "Document", "icon": "document", "color": COGNAC},
    "flowchart": {"label": "Flow Diagram", "icon": "layers", "color": PATINA},
    "presentation": {"label": "Presentation", "icon": "chart", "color": COGNAC_LIGHT},
    "markdown": {"label": "Markdown", "icon": "document", "color": SMOKE},
}


def render_artifact_card(artifact):
    """Render a card for an artifact in the list view."""
    atype = artifact.get("artifact_type", "document")
    config = ARTIFACT_TYPE_CONFIG.get(atype, ARTIFACT_TYPE_CONFIG["document"])
    status = artifact.get("status", "draft")
    version = artifact.get("version", 1)
    content = artifact.get("content", "")
    preview = content[:150] + "..." if len(content) > 150 else content

    parent = artifact.get("parent_artifact_id")
    version_badge = (
        f'<span style="font-size:0.625rem;background:{AGED_PAPER};color:{SMOKE};'
        f'padding:0.15rem 0.5rem;border-radius:9999px;font-weight:500;">v{version}</span>'
    )
    status_color = PATINA if status == "final" else SMOKE
    status_badge = (
        f'<span style="font-size:0.625rem;color:{status_color};font-weight:600;'
        f'text-transform:uppercase;letter-spacing:0.08em;">{status}</span>'
    )

    st.markdown(f"""
    <div style="background:{NEUTRAL_50};border:1px solid {BORDER};border-radius:10px;
                padding:1rem 1.25rem;margin-bottom:0.75rem;transition:all 0.2s ease;"
         onmouseover="this.style.boxShadow='0 4px 12px rgba(61,61,53,0.10)'"
         onmouseout="this.style.boxShadow='none'">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;">
            <div style="display:flex;align-items:center;gap:0.5rem;">
                {icon(config["icon"], 16, config["color"])}
                <span style="font-size:0.65rem;font-weight:600;color:{config['color']};
                      text-transform:uppercase;letter-spacing:0.08em;">{config["label"]}</span>
                {version_badge}
            </div>
            {status_badge}
        </div>
        <div style="font-family:'Playfair Display',serif;font-size:1rem;font-weight:700;
                    color:{CHARCOAL};margin-bottom:0.3rem;">{artifact.get("name", "Untitled")}</div>
        <div style="font-size:0.8rem;color:{SMOKE};line-height:1.4;font-family:'Courier Prime',monospace;">
            {preview}
        </div>
        <div style="font-size:0.7rem;color:{FAINT};margin-top:0.5rem;">
            {artifact.get("updated_at", "")[:16]}
            {"  ·  iterated from previous version" if parent else ""}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_artifact_preview(artifact):
    """Render a full preview of an artifact's content."""
    atype = artifact.get("artifact_type", "document")
    content = artifact.get("content", "")

    if not content:
        render_empty_state("document", "No content generated yet",
                           "Chat with Dupin to generate this artifact.")
        return

    if atype == "flowchart":
        # Render mermaid diagram
        # Extract mermaid code if wrapped in code block
        import re
        mermaid_match = re.search(r'```mermaid\s*(.*?)\s*```', content, re.DOTALL)
        if mermaid_match:
            mermaid_code = mermaid_match.group(1)
        else:
            mermaid_code = content

        st.markdown(f"""
        <div style="background:white;border:1px solid {BORDER};border-radius:10px;
                    padding:1.5rem;text-align:center;">
            <pre class="mermaid">{mermaid_code}</pre>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
        <script>mermaid.initialize({{startOnLoad:true, theme:'neutral'}});</script>
        """, unsafe_allow_html=True)

    elif atype == "presentation":
        # Render slides
        slides = content.split("---")
        for i, slide in enumerate(slides):
            slide = slide.strip()
            if not slide:
                continue
            st.markdown(f"""
            <div style="background:white;border:1px solid {BORDER};border-radius:10px;
                        padding:2rem;margin-bottom:1rem;min-height:200px;
                        box-shadow:0 2px 8px rgba(61,61,53,0.06);">
                <div style="font-size:0.625rem;color:{FAINT};text-transform:uppercase;
                      letter-spacing:0.12em;margin-bottom:1rem;">Slide {i + 1}</div>
            """, unsafe_allow_html=True)
            st.markdown(slide)
            st.markdown("</div>", unsafe_allow_html=True)

    else:
        # Document or markdown — render as markdown
        st.markdown(f"""
        <div style="background:white;border:1px solid {BORDER};border-radius:10px;
                    padding:1.5rem;">
        """, unsafe_allow_html=True)
        st.markdown(content)
        st.markdown("</div>", unsafe_allow_html=True)
