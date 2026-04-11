import sqlite3
import os
from config import DATABASE_PATH


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS product_contexts (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT DEFAULT '',
            documentation TEXT DEFAULT '',
            current_state TEXT DEFAULT '',
            case_history TEXT DEFAULT '[]',
            summary TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            context_conversation_history TEXT DEFAULT '[]'
        );

        CREATE TABLE IF NOT EXISTS discovery_sessions (
            id TEXT PRIMARY KEY,
            product_context_id TEXT NOT NULL,
            name TEXT NOT NULL,
            objective TEXT DEFAULT '',
            target_personas TEXT DEFAULT '[]',
            scope TEXT DEFAULT '',
            agent_behavior TEXT DEFAULT '{}',
            status TEXT DEFAULT 'draft' CHECK(status IN ('draft', 'active', 'completed')),
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            context_conversation_history TEXT DEFAULT '[]',
            accumulated_insights TEXT DEFAULT '[]',
            FOREIGN KEY (product_context_id) REFERENCES product_contexts(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS user_session_links (
            id TEXT PRIMARY KEY,
            discovery_session_id TEXT NOT NULL,
            user_name TEXT NOT NULL,
            user_role TEXT DEFAULT '',
            user_department TEXT DEFAULT '',
            token TEXT UNIQUE NOT NULL,
            expires_at TEXT NOT NULL,
            status TEXT DEFAULT 'active' CHECK(status IN ('active', 'expired', 'completed')),
            created_at TEXT NOT NULL,
            FOREIGN KEY (discovery_session_id) REFERENCES discovery_sessions(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            user_session_link_id TEXT NOT NULL,
            discovery_session_id TEXT NOT NULL,
            messages TEXT DEFAULT '[]',
            status TEXT DEFAULT 'in_progress' CHECK(status IN ('in_progress', 'completed')),
            user_summary TEXT DEFAULT '',
            started_at TEXT NOT NULL,
            completed_at TEXT,
            FOREIGN KEY (user_session_link_id) REFERENCES user_session_links(id) ON DELETE CASCADE,
            FOREIGN KEY (discovery_session_id) REFERENCES discovery_sessions(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS insights (
            id TEXT PRIMARY KEY,
            discovery_session_id TEXT NOT NULL,
            conversation_id TEXT,
            type TEXT NOT NULL CHECK(type IN (
                'user_journey_step', 'pain_point', 'expectation', 'workflow',
                'discrepancy', 'feature_request', 'behavior_pattern'
            )),
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            evidence TEXT DEFAULT '[]',
            persona_tags TEXT DEFAULT '[]',
            journey_stage TEXT,
            priority TEXT DEFAULT 'medium' CHECK(priority IN ('high', 'medium', 'low')),
            status TEXT DEFAULT 'new' CHECK(status IN ('new', 'validated', 'conflicting', 'rejected')),
            created_at TEXT NOT NULL,
            FOREIGN KEY (discovery_session_id) REFERENCES discovery_sessions(id) ON DELETE CASCADE,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS discrepancies (
            id TEXT PRIMARY KEY,
            discovery_session_id TEXT NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('user_vs_user', 'user_vs_product')),
            description TEXT DEFAULT '',
            side_a TEXT DEFAULT '{}',
            side_b TEXT DEFAULT '{}',
            resolution_status TEXT DEFAULT 'unresolved' CHECK(resolution_status IN (
                'unresolved', 'clarified_in_session', 'flagged_for_pm', 'resolved'
            )),
            resolution_notes TEXT,
            related_conversation_ids TEXT DEFAULT '[]',
            created_at TEXT NOT NULL,
            FOREIGN KEY (discovery_session_id) REFERENCES discovery_sessions(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS user_journeys (
            id TEXT PRIMARY KEY,
            discovery_session_id TEXT NOT NULL,
            product_context_id TEXT NOT NULL,
            persona TEXT DEFAULT '',
            journey_name TEXT NOT NULL,
            stages TEXT DEFAULT '[]',
            alternative_paths TEXT DEFAULT '[]',
            source_conversations TEXT DEFAULT '[]',
            confidence TEXT DEFAULT 'low' CHECK(confidence IN ('high', 'medium', 'low')),
            is_partial INTEGER DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (discovery_session_id) REFERENCES discovery_sessions(id) ON DELETE CASCADE,
            FOREIGN KEY (product_context_id) REFERENCES product_contexts(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS expectations (
            id TEXT PRIMARY KEY,
            discovery_session_id TEXT NOT NULL,
            product_context_id TEXT NOT NULL,
            description TEXT DEFAULT '',
            persona_tags TEXT DEFAULT '[]',
            journey_stage TEXT,
            priority TEXT DEFAULT 'medium' CHECK(priority IN ('critical', 'high', 'medium', 'low')),
            frequency INTEGER DEFAULT 1,
            source_conversations TEXT DEFAULT '[]',
            status TEXT DEFAULT 'new' CHECK(status IN ('new', 'acknowledged', 'planned', 'rejected')),
            created_at TEXT NOT NULL,
            FOREIGN KEY (discovery_session_id) REFERENCES discovery_sessions(id) ON DELETE CASCADE,
            FOREIGN KEY (product_context_id) REFERENCES product_contexts(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS context_improvements (
            id TEXT PRIMARY KEY,
            product_context_id TEXT NOT NULL,
            discovery_session_id TEXT NOT NULL,
            suggestion_type TEXT NOT NULL CHECK(suggestion_type IN (
                'new_info', 'correction', 'gap', 'conflicting_assumption'
            )),
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            evidence TEXT DEFAULT '[]',
            status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'accepted', 'rejected')),
            created_at TEXT NOT NULL,
            FOREIGN KEY (product_context_id) REFERENCES product_contexts(id) ON DELETE CASCADE,
            FOREIGN KEY (discovery_session_id) REFERENCES discovery_sessions(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_sessions_context ON discovery_sessions(product_context_id);
        CREATE INDEX IF NOT EXISTS idx_links_session ON user_session_links(discovery_session_id);
        CREATE INDEX IF NOT EXISTS idx_links_token ON user_session_links(token);
        CREATE INDEX IF NOT EXISTS idx_conversations_link ON conversations(user_session_link_id);
        CREATE INDEX IF NOT EXISTS idx_conversations_session ON conversations(discovery_session_id);
        CREATE INDEX IF NOT EXISTS idx_insights_session ON insights(discovery_session_id);
        CREATE INDEX IF NOT EXISTS idx_discrepancies_session ON discrepancies(discovery_session_id);
        CREATE INDEX IF NOT EXISTS idx_journeys_session ON user_journeys(discovery_session_id);
        CREATE INDEX IF NOT EXISTS idx_expectations_session ON expectations(discovery_session_id);
        CREATE INDEX IF NOT EXISTS idx_improvements_context ON context_improvements(product_context_id);

        CREATE TABLE IF NOT EXISTS artifacts (
            id TEXT PRIMARY KEY,
            product_context_id TEXT NOT NULL,
            name TEXT NOT NULL,
            artifact_type TEXT NOT NULL CHECK(artifact_type IN ('document', 'flowchart', 'presentation', 'markdown')),
            content TEXT DEFAULT '',
            parent_artifact_id TEXT,
            version INTEGER DEFAULT 1,
            conversation_history TEXT DEFAULT '[]',
            status TEXT DEFAULT 'draft' CHECK(status IN ('draft', 'final')),
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (product_context_id) REFERENCES product_contexts(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_artifacts_context ON artifacts(product_context_id);
    """)

    # Migrations for existing databases
    try:
        cursor.execute("ALTER TABLE product_contexts ADD COLUMN case_history TEXT DEFAULT '[]'")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE product_contexts ADD COLUMN summary TEXT DEFAULT ''")
    except Exception:
        pass

    conn.commit()
    conn.close()
