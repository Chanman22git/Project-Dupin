from __future__ import annotations
import json
import uuid
from datetime import datetime, timezone
from typing import Optional
from database.db import get_connection


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id() -> str:
    return str(uuid.uuid4())


def _parse_row(row) -> dict | None:
    if row is None:
        return None
    d = dict(row)
    # Auto-parse JSON fields
    for key, val in d.items():
        if isinstance(val, str) and val and val[0] in ("[", "{"):
            try:
                d[key] = json.loads(val)
            except (json.JSONDecodeError, ValueError):
                pass
    return d


def _parse_rows(rows) -> list[dict]:
    return [_parse_row(r) for r in rows]


# ──────────────────────────────────────────────
# Product Contexts
# ──────────────────────────────────────────────

class ProductContextDB:
    @staticmethod
    def create(name: str, description: str = "", documentation: str = "",
               current_state: str = "") -> dict:
        conn = get_connection()
        ctx_id = _new_id()
        now = _now()
        conn.execute(
            """INSERT INTO product_contexts
               (id, name, description, documentation, current_state, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (ctx_id, name, description, documentation, current_state, now, now),
        )
        conn.commit()
        conn.close()
        return ProductContextDB.get(ctx_id)

    @staticmethod
    def get(ctx_id: str) -> dict | None:
        conn = get_connection()
        row = conn.execute("SELECT * FROM product_contexts WHERE id = ?", (ctx_id,)).fetchone()
        conn.close()
        return _parse_row(row)

    @staticmethod
    def list_all() -> list[dict]:
        conn = get_connection()
        rows = conn.execute("SELECT * FROM product_contexts ORDER BY updated_at DESC").fetchall()
        conn.close()
        return _parse_rows(rows)

    @staticmethod
    def update(ctx_id: str, **kwargs) -> dict | None:
        conn = get_connection()
        allowed = {"name", "description", "documentation", "current_state",
                    "context_conversation_history"}
        updates = []
        values = []
        for k, v in kwargs.items():
            if k in allowed:
                updates.append(f"{k} = ?")
                values.append(json.dumps(v) if isinstance(v, (list, dict)) else v)
        if not updates:
            conn.close()
            return ProductContextDB.get(ctx_id)
        updates.append("updated_at = ?")
        values.append(_now())
        values.append(ctx_id)
        conn.execute(
            f"UPDATE product_contexts SET {', '.join(updates)} WHERE id = ?", values
        )
        conn.commit()
        conn.close()
        return ProductContextDB.get(ctx_id)

    @staticmethod
    def delete(ctx_id: str) -> bool:
        conn = get_connection()
        cursor = conn.execute("DELETE FROM product_contexts WHERE id = ?", (ctx_id,))
        conn.commit()
        conn.close()
        return cursor.rowcount > 0

    @staticmethod
    def count_sessions(ctx_id: str) -> int:
        conn = get_connection()
        row = conn.execute(
            "SELECT COUNT(*) as cnt FROM discovery_sessions WHERE product_context_id = ?",
            (ctx_id,),
        ).fetchone()
        conn.close()
        return row["cnt"] if row else 0


# ──────────────────────────────────────────────
# Discovery Sessions
# ──────────────────────────────────────────────

class DiscoverySessionDB:
    @staticmethod
    def create(product_context_id: str, name: str, objective: str = "",
               target_personas: list = None, scope: str = "",
               agent_behavior: dict = None) -> dict:
        conn = get_connection()
        session_id = _new_id()
        now = _now()
        default_behavior = {
            "research_depth": "balanced",
            "clarification_mode": "balanced",
            "max_questions": None,
            "focus_areas": [],
            "avoid_areas": [],
        }
        behavior = {**default_behavior, **(agent_behavior or {})}
        conn.execute(
            """INSERT INTO discovery_sessions
               (id, product_context_id, name, objective, target_personas, scope,
                agent_behavior, status, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, 'draft', ?, ?)""",
            (session_id, product_context_id, name, objective,
             json.dumps(target_personas or []), scope,
             json.dumps(behavior), now, now),
        )
        conn.commit()
        conn.close()
        return DiscoverySessionDB.get(session_id)

    @staticmethod
    def get(session_id: str) -> dict | None:
        conn = get_connection()
        row = conn.execute("SELECT * FROM discovery_sessions WHERE id = ?", (session_id,)).fetchone()
        conn.close()
        return _parse_row(row)

    @staticmethod
    def list_by_context(product_context_id: str) -> list[dict]:
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM discovery_sessions WHERE product_context_id = ? ORDER BY updated_at DESC",
            (product_context_id,),
        ).fetchall()
        conn.close()
        return _parse_rows(rows)

    @staticmethod
    def update(session_id: str, **kwargs) -> dict | None:
        conn = get_connection()
        allowed = {"name", "objective", "target_personas", "scope", "agent_behavior",
                    "status", "context_conversation_history", "accumulated_insights"}
        updates = []
        values = []
        for k, v in kwargs.items():
            if k in allowed:
                updates.append(f"{k} = ?")
                values.append(json.dumps(v) if isinstance(v, (list, dict)) else v)
        if not updates:
            conn.close()
            return DiscoverySessionDB.get(session_id)
        updates.append("updated_at = ?")
        values.append(_now())
        values.append(session_id)
        conn.execute(
            f"UPDATE discovery_sessions SET {', '.join(updates)} WHERE id = ?", values
        )
        conn.commit()
        conn.close()
        return DiscoverySessionDB.get(session_id)

    @staticmethod
    def delete(session_id: str) -> bool:
        conn = get_connection()
        cursor = conn.execute("DELETE FROM discovery_sessions WHERE id = ?", (session_id,))
        conn.commit()
        conn.close()
        return cursor.rowcount > 0


# ──────────────────────────────────────────────
# User Session Links
# ──────────────────────────────────────────────

class UserSessionLinkDB:
    @staticmethod
    def create(discovery_session_id: str, user_name: str, user_role: str = "",
               user_department: str = "", expires_at: str = "") -> dict:
        conn = get_connection()
        link_id = _new_id()
        token = str(uuid.uuid4())
        now = _now()
        conn.execute(
            """INSERT INTO user_session_links
               (id, discovery_session_id, user_name, user_role, user_department,
                token, expires_at, status, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, 'active', ?)""",
            (link_id, discovery_session_id, user_name, user_role,
             user_department, token, expires_at, now),
        )
        conn.commit()
        conn.close()
        return UserSessionLinkDB.get(link_id)

    @staticmethod
    def get(link_id: str) -> dict | None:
        conn = get_connection()
        row = conn.execute("SELECT * FROM user_session_links WHERE id = ?", (link_id,)).fetchone()
        conn.close()
        return _parse_row(row)

    @staticmethod
    def get_by_token(token: str) -> dict | None:
        conn = get_connection()
        row = conn.execute("SELECT * FROM user_session_links WHERE token = ?", (token,)).fetchone()
        conn.close()
        return _parse_row(row)

    @staticmethod
    def list_by_session(discovery_session_id: str) -> list[dict]:
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM user_session_links WHERE discovery_session_id = ? ORDER BY created_at DESC",
            (discovery_session_id,),
        ).fetchall()
        conn.close()
        return _parse_rows(rows)

    @staticmethod
    def update_status(link_id: str, status: str) -> dict | None:
        conn = get_connection()
        conn.execute("UPDATE user_session_links SET status = ? WHERE id = ?", (status, link_id))
        conn.commit()
        conn.close()
        return UserSessionLinkDB.get(link_id)

    @staticmethod
    def expire_old_links():
        conn = get_connection()
        now = _now()
        conn.execute(
            "UPDATE user_session_links SET status = 'expired' WHERE expires_at < ? AND status = 'active'",
            (now,),
        )
        conn.commit()
        conn.close()


# ──────────────────────────────────────────────
# Conversations
# ──────────────────────────────────────────────

class ConversationDB:
    @staticmethod
    def create(user_session_link_id: str, discovery_session_id: str) -> dict:
        conn = get_connection()
        conv_id = _new_id()
        now = _now()
        conn.execute(
            """INSERT INTO conversations
               (id, user_session_link_id, discovery_session_id, messages, status, started_at)
               VALUES (?, ?, ?, '[]', 'in_progress', ?)""",
            (conv_id, user_session_link_id, discovery_session_id, now),
        )
        conn.commit()
        conn.close()
        return ConversationDB.get(conv_id)

    @staticmethod
    def get(conv_id: str) -> dict | None:
        conn = get_connection()
        row = conn.execute("SELECT * FROM conversations WHERE id = ?", (conv_id,)).fetchone()
        conn.close()
        return _parse_row(row)

    @staticmethod
    def get_by_link(user_session_link_id: str) -> dict | None:
        conn = get_connection()
        row = conn.execute(
            "SELECT * FROM conversations WHERE user_session_link_id = ? ORDER BY started_at DESC LIMIT 1",
            (user_session_link_id,),
        ).fetchone()
        conn.close()
        return _parse_row(row)

    @staticmethod
    def list_by_session(discovery_session_id: str) -> list[dict]:
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM conversations WHERE discovery_session_id = ? ORDER BY started_at DESC",
            (discovery_session_id,),
        ).fetchall()
        conn.close()
        return _parse_rows(rows)

    @staticmethod
    def add_message(conv_id: str, role: str, content: str) -> dict:
        conn = get_connection()
        row = conn.execute("SELECT messages FROM conversations WHERE id = ?", (conv_id,)).fetchone()
        messages = json.loads(row["messages"]) if row else []
        messages.append({"role": role, "content": content, "timestamp": _now()})
        conn.execute(
            "UPDATE conversations SET messages = ? WHERE id = ?",
            (json.dumps(messages), conv_id),
        )
        conn.commit()
        conn.close()
        return ConversationDB.get(conv_id)

    @staticmethod
    def complete(conv_id: str, user_summary: str = "") -> dict:
        conn = get_connection()
        conn.execute(
            "UPDATE conversations SET status = 'completed', user_summary = ?, completed_at = ? WHERE id = ?",
            (user_summary, _now(), conv_id),
        )
        conn.commit()
        conn.close()
        return ConversationDB.get(conv_id)


# ──────────────────────────────────────────────
# Insights
# ──────────────────────────────────────────────

class InsightDB:
    @staticmethod
    def create(discovery_session_id: str, type: str, title: str,
               description: str = "", conversation_id: str = None,
               evidence: list = None, persona_tags: list = None,
               journey_stage: str = None, priority: str = "medium") -> dict:
        conn = get_connection()
        insight_id = _new_id()
        now = _now()
        conn.execute(
            """INSERT INTO insights
               (id, discovery_session_id, conversation_id, type, title, description,
                evidence, persona_tags, journey_stage, priority, status, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'new', ?)""",
            (insight_id, discovery_session_id, conversation_id, type, title,
             description, json.dumps(evidence or []), json.dumps(persona_tags or []),
             journey_stage, priority, now),
        )
        conn.commit()
        conn.close()
        return InsightDB.get(insight_id)

    @staticmethod
    def get(insight_id: str) -> dict | None:
        conn = get_connection()
        row = conn.execute("SELECT * FROM insights WHERE id = ?", (insight_id,)).fetchone()
        conn.close()
        return _parse_row(row)

    @staticmethod
    def list_by_session(discovery_session_id: str) -> list[dict]:
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM insights WHERE discovery_session_id = ? ORDER BY created_at DESC",
            (discovery_session_id,),
        ).fetchall()
        conn.close()
        return _parse_rows(rows)

    @staticmethod
    def list_by_type(discovery_session_id: str, type: str) -> list[dict]:
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM insights WHERE discovery_session_id = ? AND type = ? ORDER BY created_at DESC",
            (discovery_session_id, type),
        ).fetchall()
        conn.close()
        return _parse_rows(rows)

    @staticmethod
    def update_status(insight_id: str, status: str) -> dict | None:
        conn = get_connection()
        conn.execute("UPDATE insights SET status = ? WHERE id = ?", (status, insight_id))
        conn.commit()
        conn.close()
        return InsightDB.get(insight_id)


# ──────────────────────────────────────────────
# Discrepancies
# ──────────────────────────────────────────────

class DiscrepancyDB:
    @staticmethod
    def create(discovery_session_id: str, type: str, description: str = "",
               side_a: dict = None, side_b: dict = None,
               related_conversation_ids: list = None) -> dict:
        conn = get_connection()
        disc_id = _new_id()
        now = _now()
        conn.execute(
            """INSERT INTO discrepancies
               (id, discovery_session_id, type, description, side_a, side_b,
                resolution_status, related_conversation_ids, created_at)
               VALUES (?, ?, ?, ?, ?, ?, 'unresolved', ?, ?)""",
            (disc_id, discovery_session_id, type, description,
             json.dumps(side_a or {}), json.dumps(side_b or {}),
             json.dumps(related_conversation_ids or []), now),
        )
        conn.commit()
        conn.close()
        return DiscrepancyDB.get(disc_id)

    @staticmethod
    def get(disc_id: str) -> dict | None:
        conn = get_connection()
        row = conn.execute("SELECT * FROM discrepancies WHERE id = ?", (disc_id,)).fetchone()
        conn.close()
        return _parse_row(row)

    @staticmethod
    def list_by_session(discovery_session_id: str) -> list[dict]:
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM discrepancies WHERE discovery_session_id = ? ORDER BY created_at DESC",
            (discovery_session_id,),
        ).fetchall()
        conn.close()
        return _parse_rows(rows)

    @staticmethod
    def update_resolution(disc_id: str, resolution_status: str,
                          resolution_notes: str = None) -> dict | None:
        conn = get_connection()
        conn.execute(
            "UPDATE discrepancies SET resolution_status = ?, resolution_notes = ? WHERE id = ?",
            (resolution_status, resolution_notes, disc_id),
        )
        conn.commit()
        conn.close()
        return DiscrepancyDB.get(disc_id)


# ──────────────────────────────────────────────
# User Journeys
# ──────────────────────────────────────────────

class UserJourneyDB:
    @staticmethod
    def create(discovery_session_id: str, product_context_id: str,
               journey_name: str, persona: str = "", stages: list = None,
               source_conversations: list = None, confidence: str = "low",
               is_partial: bool = True) -> dict:
        conn = get_connection()
        journey_id = _new_id()
        now = _now()
        conn.execute(
            """INSERT INTO user_journeys
               (id, discovery_session_id, product_context_id, persona, journey_name,
                stages, source_conversations, confidence, is_partial, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (journey_id, discovery_session_id, product_context_id, persona,
             journey_name, json.dumps(stages or []),
             json.dumps(source_conversations or []), confidence,
             1 if is_partial else 0, now, now),
        )
        conn.commit()
        conn.close()
        return UserJourneyDB.get(journey_id)

    @staticmethod
    def get(journey_id: str) -> dict | None:
        conn = get_connection()
        row = conn.execute("SELECT * FROM user_journeys WHERE id = ?", (journey_id,)).fetchone()
        conn.close()
        return _parse_row(row)

    @staticmethod
    def list_by_session(discovery_session_id: str) -> list[dict]:
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM user_journeys WHERE discovery_session_id = ? ORDER BY updated_at DESC",
            (discovery_session_id,),
        ).fetchall()
        conn.close()
        return _parse_rows(rows)

    @staticmethod
    def update(journey_id: str, **kwargs) -> dict | None:
        conn = get_connection()
        allowed = {"persona", "journey_name", "stages", "alternative_paths",
                    "source_conversations", "confidence", "is_partial"}
        updates = []
        values = []
        for k, v in kwargs.items():
            if k in allowed:
                updates.append(f"{k} = ?")
                if k == "is_partial":
                    values.append(1 if v else 0)
                elif isinstance(v, (list, dict)):
                    values.append(json.dumps(v))
                else:
                    values.append(v)
        if not updates:
            conn.close()
            return UserJourneyDB.get(journey_id)
        updates.append("updated_at = ?")
        values.append(_now())
        values.append(journey_id)
        conn.execute(
            f"UPDATE user_journeys SET {', '.join(updates)} WHERE id = ?", values
        )
        conn.commit()
        conn.close()
        return UserJourneyDB.get(journey_id)


# ──────────────────────────────────────────────
# Expectations
# ──────────────────────────────────────────────

class ExpectationDB:
    @staticmethod
    def create(discovery_session_id: str, product_context_id: str,
               description: str, persona_tags: list = None,
               journey_stage: str = None, priority: str = "medium",
               source_conversations: list = None) -> dict:
        conn = get_connection()
        exp_id = _new_id()
        now = _now()
        conn.execute(
            """INSERT INTO expectations
               (id, discovery_session_id, product_context_id, description,
                persona_tags, journey_stage, priority, frequency, source_conversations,
                status, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, 'new', ?)""",
            (exp_id, discovery_session_id, product_context_id, description,
             json.dumps(persona_tags or []), journey_stage, priority,
             json.dumps(source_conversations or []), now),
        )
        conn.commit()
        conn.close()
        return ExpectationDB.get(exp_id)

    @staticmethod
    def get(exp_id: str) -> dict | None:
        conn = get_connection()
        row = conn.execute("SELECT * FROM expectations WHERE id = ?", (exp_id,)).fetchone()
        conn.close()
        return _parse_row(row)

    @staticmethod
    def list_by_session(discovery_session_id: str) -> list[dict]:
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM expectations WHERE discovery_session_id = ? ORDER BY priority, created_at DESC",
            (discovery_session_id,),
        ).fetchall()
        conn.close()
        return _parse_rows(rows)

    @staticmethod
    def increment_frequency(exp_id: str) -> dict | None:
        conn = get_connection()
        conn.execute("UPDATE expectations SET frequency = frequency + 1 WHERE id = ?", (exp_id,))
        conn.commit()
        conn.close()
        return ExpectationDB.get(exp_id)

    @staticmethod
    def update_status(exp_id: str, status: str) -> dict | None:
        conn = get_connection()
        conn.execute("UPDATE expectations SET status = ? WHERE id = ?", (status, exp_id))
        conn.commit()
        conn.close()
        return ExpectationDB.get(exp_id)


# ──────────────────────────────────────────────
# Context Improvements
# ──────────────────────────────────────────────

class ContextImprovementDB:
    @staticmethod
    def create(product_context_id: str, discovery_session_id: str,
               suggestion_type: str, title: str, description: str = "",
               evidence: list = None) -> dict:
        conn = get_connection()
        imp_id = _new_id()
        now = _now()
        conn.execute(
            """INSERT INTO context_improvements
               (id, product_context_id, discovery_session_id, suggestion_type,
                title, description, evidence, status, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', ?)""",
            (imp_id, product_context_id, discovery_session_id, suggestion_type,
             title, description, json.dumps(evidence or []), now),
        )
        conn.commit()
        conn.close()
        return ContextImprovementDB.get(imp_id)

    @staticmethod
    def get(imp_id: str) -> dict | None:
        conn = get_connection()
        row = conn.execute("SELECT * FROM context_improvements WHERE id = ?", (imp_id,)).fetchone()
        conn.close()
        return _parse_row(row)

    @staticmethod
    def list_by_context(product_context_id: str) -> list[dict]:
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM context_improvements WHERE product_context_id = ? ORDER BY created_at DESC",
            (product_context_id,),
        ).fetchall()
        conn.close()
        return _parse_rows(rows)

    @staticmethod
    def update_status(imp_id: str, status: str) -> dict | None:
        conn = get_connection()
        conn.execute("UPDATE context_improvements SET status = ? WHERE id = ?", (status, imp_id))
        conn.commit()
        conn.close()
        return ContextImprovementDB.get(imp_id)
