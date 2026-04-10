# Discovery Agent — Full Project Specification

## Overview

Build a **Streamlit application** called "Discovery Agent" — an AI-powered user research platform that enables Product Managers (PMs) to conduct structured product discovery by deploying conversational AI agents to interview internal company users. The agent gathers insights about user journeys, use cases, expectations, and pain points, then synthesizes findings across multiple conversations.

---

## Tech Stack

- **Frontend**: Streamlit (multi-page app)
- **Backend**: Python
- **LLM**: Anthropic Claude API (claude-sonnet-4-20250514)
- **Database**: SQLite (via sqlite3)
- **Auth**: None for MVP (skip for now)

---

## Core Concepts & Data Model

### 1. Product Context
A product context is the top-level container. A PM creates one per product/initiative they're researching.

```
product_contexts:
  - id (UUID)
  - name (str)
  - description (text) — rich product description
  - documentation (text) — uploaded/pasted product docs, PRDs, specs
  - current_state (text) — what the product currently does (for discrepancy detection)
  - created_at (datetime)
  - updated_at (datetime)
  - context_conversation_history (JSON) — the PM's conversational history while defining this context
```

### 2. Discovery Session
Scoped research effort within a product context. Focused on a specific feature, scenario, use case, or persona.

```
discovery_sessions:
  - id (UUID)
  - product_context_id (FK)
  - name (str)
  - objective (text) — what the PM wants to learn
  - target_personas (JSON) — list of persona definitions [{name, description, key_characteristics}]
  - scope (text) — specific feature/scenario/use case being explored
  - agent_behavior (JSON) — PM-configured settings:
      - research_depth: "deep_researcher" | "balanced" | "listener" (default: "balanced")
      - clarification_mode: "realtime" | "flagged" | "balanced" (default: "balanced")
      - max_questions: int (optional, to keep conversations bounded)
      - focus_areas: [str] — specific things to probe on
      - avoid_areas: [str] — things to not ask about
  - status: "draft" | "active" | "completed"
  - created_at (datetime)
  - updated_at (datetime)
  - context_conversation_history (JSON) — PM's conversational history while defining this session
  - accumulated_insights (JSON) — insights gathered so far, used to refine questions (but not bias)
```

### 3. User Session Links
Unique, expiring links for individual users to converse with the agent.

```
user_session_links:
  - id (UUID)
  - discovery_session_id (FK)
  - user_name (str) — name/identifier of the user
  - user_role (str) — their role/persona
  - user_department (str, optional)
  - token (str, unique) — URL token for the link
  - expires_at (datetime)
  - status: "active" | "expired" | "completed"
  - created_at (datetime)
```

### 4. Conversations
Full conversation transcripts between agent and user.

```
conversations:
  - id (UUID)
  - user_session_link_id (FK)
  - discovery_session_id (FK)
  - messages (JSON) — [{role, content, timestamp}]
  - status: "in_progress" | "completed"
  - user_summary (text) — generated summary shown to user at end
  - started_at (datetime)
  - completed_at (datetime, nullable)
```

### 5. Insights
Extracted findings from conversations, tied to discovery sessions.

```
insights:
  - id (UUID)
  - discovery_session_id (FK)
  - conversation_id (FK, nullable — can span conversations)
  - type: "user_journey_step" | "pain_point" | "expectation" | "workflow" | "discrepancy" | "feature_request" | "behavior_pattern"
  - title (str)
  - description (text)
  - evidence (JSON) — [{conversation_id, relevant_quotes}]
  - persona_tags (JSON) — which personas this applies to
  - journey_stage (str, nullable) — which stage of the journey
  - priority: "high" | "medium" | "low"
  - status: "new" | "validated" | "conflicting" | "rejected"
  - created_at (datetime)
```

### 6. Discrepancies
Contradictions and conflicts detected across conversations or against product context.

```
discrepancies:
  - id (UUID)
  - discovery_session_id (FK)
  - type: "user_vs_user" | "user_vs_product"
  - description (text)
  - side_a (JSON) — {source, claim, evidence}
  - side_b (JSON) — {source, claim, evidence}
  - resolution_status: "unresolved" | "clarified_in_session" | "flagged_for_pm" | "resolved"
  - resolution_notes (text, nullable)
  - related_conversation_ids (JSON)
  - created_at (datetime)
```

### 7. User Journeys
Structured journey representations that accumulate across conversations.

```
user_journeys:
  - id (UUID)
  - discovery_session_id (FK)
  - product_context_id (FK)
  - persona (str)
  - journey_name (str)
  - stages (JSON) — [{
      stage_name,
      description,
      actions: [{action, detail}],
      pain_points: [str],
      emotions: [str],
      touchpoints: [str],
      expectations: [{description, priority}]
    }]
  - alternative_paths (JSON) — [{path_name, diverges_at_stage, stages: [...]}]
  - source_conversations (JSON) — [conversation_ids]
  - confidence: "high" | "medium" | "low"
  - is_partial (bool) — true if user only knew part of the journey
  - created_at (datetime)
  - updated_at (datetime)
```

### 8. Expectations
Separately tracked expectations tagged by persona, journey stage, and priority.

```
expectations:
  - id (UUID)
  - discovery_session_id (FK)
  - product_context_id (FK)
  - description (text)
  - persona_tags (JSON)
  - journey_stage (str, nullable)
  - priority: "critical" | "high" | "medium" | "low"
  - frequency (int) — how many users mentioned this
  - source_conversations (JSON)
  - status: "new" | "acknowledged" | "planned" | "rejected"
  - created_at (datetime)
```

### 9. Context Improvement Suggestions
Suggestions for improving product context based on discovery findings.

```
context_improvements:
  - id (UUID)
  - product_context_id (FK)
  - discovery_session_id (FK)
  - suggestion_type: "new_info" | "correction" | "gap" | "conflicting_assumption"
  - title (str)
  - description (text)
  - evidence (JSON)
  - status: "pending" | "accepted" | "rejected"
  - created_at (datetime)
```

---

## Application Pages & Routes

### Page 1: Home / Product Contexts (`app.py` or `pages/1_Home.py`)

**What the PM sees:**
- List of existing product contexts (cards with name, description, session count, last updated)
- "Create new product context" button

**Create Product Context flow:**
- This is CONVERSATIONAL. The PM chats with the agent to define the product context.
- The agent asks intelligent questions: "What product are you researching?", "Who are the primary users?", "What does the product currently do?", "What documentation do you have?"
- PM can paste documentation, describe features, etc.
- The agent synthesizes this into a structured product context.
- PM can also upload text/markdown documents as context.
- At any point, PM can say "save this context" and the agent structures it.

### Page 2: Product Context Detail (`pages/2_Product_Context.py`)

**What the PM sees:**
- Product context summary (editable via conversation — PM says "update the description to include X")
- List of discovery sessions under this context
- "Create new discovery session" button
- "Insights for improved context" panel — suggestions from discovery sessions that the PM can accept/reject
- "Generate cross-session report" button — aggregates insights across ALL discovery sessions in this product context

### Page 3: Discovery Session (`pages/3_Discovery_Session.py`)

**What the PM sees:**
- Session details (objective, personas, scope, agent behavior config)
- Conversational interface for PM to refine the session (same chat-to-configure pattern)
- Agent behavior configuration panel:
  - Slider: Research depth (deep researcher ↔ listener)
  - Toggle: Clarification mode (real-time / flagged / balanced)
  - Max questions per conversation (optional)
  - Focus areas (text input, comma-separated)
  - Avoid areas (text input, comma-separated)
- "Generate user links" section:
  - Form: user name, role, department (optional)
  - Link expiry (hours/days dropdown)
  - Generate button → produces unique URL
  - List of generated links with status (active/expired/completed), copy button
- Conversations panel:
  - List of completed/in-progress conversations
  - Click to view full transcript
- "Generate insights" button — runs analysis across all conversations in this session
- Insights panel (after generation):
  - Grouped by type (journey steps, pain points, expectations, discrepancies)
  - Each insight shows evidence (which conversations support it)
  - Discrepancies highlighted with both sides shown
  - "Suggest context improvements" button — flags things for the product context

### Page 4: User Conversation (`pages/4_User_Chat.py`)

**Accessed via unique link with token as query parameter.** No Streamlit sidebar (hide it).

**What the user sees:**
- Clean chat interface
- Welcome message explaining purpose (drawn from discovery session context)
- Conversational agent that:
  - Understands what persona the user is (from link config)
  - Asks about their workflows, use cases, pain points, expectations
  - Follows up intelligently based on responses
  - Clarifies contradictions with prior users in real-time (when in balanced/realtime mode) WITHOUT revealing what other users said — frames as "Some users have mentioned X, does that match your experience?"
  - Doesn't go on forever — respects max_questions if set, and naturally wraps up
  - Adapts question strategy based on accumulated_insights from prior conversations BUT starts fresh (doesn't assume anything, doesn't bias)
- At conversation end:
  - Agent provides a summary of what was discussed
  - User can confirm/correct the summary
  - Link becomes "completed"

**Expired links:**
- Show a message: "This session link has expired. Please contact your product manager for a new link."

### Page 5: Reports (`pages/5_Reports.py`)

**Accessed from Product Context or Discovery Session level.**

**Discovery Session Report includes:**
1. Executive summary
2. User journeys (structured + visual description)
   - Multiple paths shown, not overwritten
   - Partial journeys marked as such
   - Confidence levels indicated
3. Pain points (grouped by journey stage)
4. Expectations (tagged by persona, journey stage, priority)
5. Discrepancies found (with both sides and resolution status)
6. Key quotes and evidence
7. Recommended areas for further investigation

**Product Context Report (cross-session) includes:**
- Everything above but aggregated across sessions
- Trends across sessions
- Evolving journey map
- Conflicting findings between sessions

---

## Agent Behavior Specifications

### PM-Facing Agent (Context & Session Setup)

System prompt pattern:
```
You are a product discovery assistant helping a Product Manager set up research.
Your job is to help them clearly define:
- What product they're researching
- What they want to learn
- Who their target users are
- How the agent should behave during user interviews

Ask clarifying questions. Be structured but conversational.
When the PM seems ready, offer to save/structure what you've gathered.
```

### User-Facing Agent (Discovery Conversations)

System prompt pattern (dynamically constructed per session):
```
You are a user research agent conducting a discovery conversation.

PRODUCT CONTEXT:
{product_context.description}
{product_context.documentation}
{product_context.current_state}

DISCOVERY SESSION:
Objective: {session.objective}
Scope: {session.scope}
Target persona for this user: {link.user_role}

BEHAVIOR:
Research depth: {session.agent_behavior.research_depth}
- "deep_researcher": Ask probing follow-ups, dig into edge cases, ask "why" frequently
- "balanced": Mix of probing and listening, follow the user's lead but redirect when needed
- "listener": Primarily listen and categorize, minimal follow-ups, let user talk

Clarification mode: {session.agent_behavior.clarification_mode}
- "realtime": When you detect contradictions with known insights, gently probe: "Some users have described this differently — they mentioned X. Does that match your experience?"
- "flagged": Don't bring up contradictions during conversation. Flag them internally.
- "balanced": Only bring up significant contradictions, flag minor ones.

Focus areas: {session.agent_behavior.focus_areas}
Avoid areas: {session.agent_behavior.avoid_areas}
Max questions: {session.agent_behavior.max_questions or "no limit, but wrap up naturally after 15-20 exchanges"}

ACCUMULATED INSIGHTS (for question refinement, NOT for biasing):
{session.accumulated_insights — used to identify gaps to explore, not to lead the user}

INSTRUCTIONS:
1. Start fresh with each user. Don't assume anything.
2. Begin with open-ended questions about their role and what they do.
3. Gradually explore their workflows, use cases, and pain points.
4. Ask about expectations for the product/feature.
5. If they mention something that conflicts with the product context, note it internally.
6. Keep the conversation natural and bounded.
7. When wrapping up, summarize what you learned and ask the user to confirm.
8. Throughout, track: journey steps, pain points, expectations, discrepancies, workflows.
```

### Analysis Agent (Insight Generation)

System prompt pattern:
```
You are an expert user research analyst. Given the following conversations from a discovery session, extract and synthesize:

1. USER JOURNEYS: Identify the steps users go through. Note:
   - Multiple users may describe different paths for the same journey
   - Some users may only know part of the journey
   - Don't merge conflicting paths — document them as alternatives
   - Mark confidence levels based on how many users confirmed each path

2. PAIN POINTS: Group by journey stage. Include severity based on user language.

3. EXPECTATIONS: What do users want? Tag by:
   - Persona
   - Journey stage
   - Priority (based on frequency and emphasis)

4. DISCREPANCIES:
   - user_vs_user: Where different users describe the same thing differently
   - user_vs_product: Where user descriptions conflict with the product context

5. CONTEXT IMPROVEMENTS: Based on what you learned, what should the PM update in their product context?

PRODUCT CONTEXT:
{product_context}

DISCOVERY SESSION:
{session details}

CONVERSATIONS:
{all conversation transcripts}

Respond with structured JSON matching the insight/discrepancy/journey schemas.
```

---

## Key Implementation Details

### Conversation Flow Management

The agent should use a state machine for user conversations:

```
States:
  GREETING → ROLE_EXPLORATION → WORKFLOW_DEEP_DIVE → PAIN_POINTS → EXPECTATIONS → WRAP_UP → SUMMARY

Transitions:
  - GREETING: 1-2 messages, then auto-transition
  - ROLE_EXPLORATION: Until user's role/context is clear (2-4 messages)
  - WORKFLOW_DEEP_DIVE: Core of the conversation (5-10 messages)
  - PAIN_POINTS: If not naturally covered (2-4 messages)
  - EXPECTATIONS: 2-4 messages
  - WRAP_UP: 1-2 messages, signal conversation ending
  - SUMMARY: Generate and present summary, ask for confirmation
```

The agent tracks which state it's in and uses this to calibrate questions. The state machine should be soft (the agent can go back if the user brings up something relevant to a prior state).

### Real-Time Discrepancy Detection

During user conversations (when clarification_mode is "realtime" or "balanced"):
1. After each user message, compare key claims against accumulated_insights
2. If a contradiction is detected, formulate a neutral clarifying question
3. NEVER reveal what other specific users said — use phrasing like:
   - "Interesting — I've heard some people describe this differently. They mentioned X. How does that compare to your experience?"
   - "That's helpful. Just to make sure I understand — would you say X or Y is more accurate?"
4. In "balanced" mode, only surface contradictions that are significant (different workflow steps, conflicting pain points) — not minor wording differences

### Link Generation & Expiry

- Links use the pattern: `{base_url}?page=chat&token={uuid}`
- Tokens are UUIDs stored in the database
- Expiry is checked on page load — if expired, show expiry message
- When a user completes a conversation, mark the link as "completed"

### Insight Accumulation Without Bias

After each completed conversation:
1. Extract key findings using the Analysis Agent
2. Store in accumulated_insights on the discovery session
3. When the NEXT user starts a conversation:
   - The agent uses accumulated_insights to identify GAPS — things not yet explored
   - The agent does NOT use them to lead the user ("Other users said X, do you agree?")
   - The agent DOES use them to ask better questions ("Can you tell me about how you handle X?" where X is something that was mentioned as important by others but with conflicting descriptions)
4. The discovery session's question strategy improves over time without biasing individual conversations

### Journey Accumulation

User journeys are NOT overwritten. The system:
1. After each conversation, extracts journey steps mentioned by that user
2. Compares against existing journeys in the session
3. If a new path is identified, creates an alternative_path
4. If a user only knew part of the journey, marks it as is_partial
5. Confidence increases as more users confirm the same path
6. The final report shows ALL paths, with confidence levels

---

## File Structure

```
discovery_agent/
├── app.py                          # Main entry point, page routing
├── requirements.txt
├── .env.example                    # ANTHROPIC_API_KEY=
├── config.py                       # App config, constants
├── database/
│   ├── __init__.py
│   ├── db.py                       # SQLite connection, init, migrations
│   └── models.py                   # CRUD operations for all tables
├── agents/
│   ├── __init__.py
│   ├── pm_agent.py                 # PM-facing conversational agent (context/session setup)
│   ├── user_agent.py               # User-facing discovery agent
│   ├── analysis_agent.py           # Insight extraction & synthesis
│   └── prompts.py                  # All system prompt templates
├── pages/
│   ├── 1_Home.py                   # Product context list
│   ├── 2_Product_Context.py        # Product context detail + discovery sessions
│   ├── 3_Discovery_Session.py      # Session config, link generation, conversations
│   ├── 4_User_Chat.py              # User-facing chat (accessed via token link)
│   └── 5_Reports.py                # Report generation (session-level and cross-session)
├── components/
│   ├── __init__.py
│   ├── chat_ui.py                  # Reusable chat interface component
│   ├── journey_visualizer.py       # Renders user journey maps (uses streamlit components or mermaid)
│   └── insight_cards.py            # Reusable insight display cards
└── utils/
    ├── __init__.py
    ├── link_manager.py             # Link generation, validation, expiry
    └── export.py                   # Export reports to markdown/PDF
```

---

## Dependencies (requirements.txt)

```
streamlit>=1.30.0
anthropic>=0.40.0
python-dotenv>=1.0.0
uuid
```

---

## Environment Variables

```
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_PATH=./discovery_agent.db
BASE_URL=http://localhost:8501
```

---

## Implementation Order (Suggested Phases)

### Phase 1: Foundation
1. Database setup (all tables, CRUD operations)
2. Config and environment setup
3. Basic Streamlit app structure with page routing

### Phase 2: PM Flow
4. Product context creation (conversational)
5. Discovery session creation (conversational)
6. Agent behavior configuration UI
7. Link generation with expiry

### Phase 3: User Flow
8. User chat page (accessed via token)
9. User-facing agent with conversation state machine
10. Link expiry checking
11. Conversation summary generation

### Phase 4: Analysis
12. Insight extraction after conversations
13. Discrepancy detection (user-vs-user, user-vs-product)
14. User journey extraction and accumulation
15. Expectation tagging and aggregation
16. Context improvement suggestions

### Phase 5: Reports
17. Discovery session report generation
18. Cross-session (product context level) report
19. Journey visualization
20. Export capabilities

### Phase 6: Refinement
21. Accumulated insights feeding into question refinement
22. Real-time discrepancy clarification during conversations
23. PM ability to update product context from insights
24. Polish UI/UX

---

## Important Behavioral Rules

1. **No bias propagation**: Each user conversation starts fresh. Accumulated insights improve questions but don't lead answers.
2. **Journey paths are additive**: Never overwrite a journey path. Add alternatives, mark partials, track confidence.
3. **Discrepancies are surfaced, not resolved**: The agent flags contradictions. The PM decides what's true.
4. **Conversation boundaries**: Conversations should end naturally. Use max_questions as a soft limit, not a hard cutoff.
5. **Context improvements are suggestions**: The PM explicitly accepts or rejects each suggestion. Auto-updating the product context is not allowed.
6. **Expiry is enforced**: Expired links cannot be used. Period.
7. **Neutrality in clarification**: When asking about discrepancies, NEVER take sides or reveal specific user identities/quotes.

---

## Claude API Usage Pattern

All LLM calls should go through a common utility:

```python
import anthropic

client = anthropic.Anthropic()

def call_claude(system_prompt: str, messages: list[dict], max_tokens: int = 4096) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=max_tokens,
        system=system_prompt,
        messages=messages
    )
    return response.content[0].text
```

For structured output (insights, journeys), instruct Claude to return JSON and parse it:

```python
def call_claude_json(system_prompt: str, messages: list[dict]) -> dict:
    response = call_claude(
        system_prompt + "\n\nRespond ONLY with valid JSON. No markdown, no explanation.",
        messages,
        max_tokens=8192
    )
    return json.loads(response)
```

---

## UI/UX Notes

- Use `st.chat_message` and `st.chat_input` for all conversational interfaces
- Use `st.sidebar` for navigation on PM pages, hide sidebar on user chat page
- Use `st.expander` for conversation transcripts
- Use `st.columns` for layout (e.g., config panel + chat side by side)
- Use `st.metric` for insight counts
- Use `st.tabs` for switching between views within a page
- Use `st.status` for long-running operations (insight generation, report generation)
- Color code discrepancy types (user-vs-user = orange, user-vs-product = red)
- Show confidence levels on journeys with color coding (high=green, medium=yellow, low=red)
