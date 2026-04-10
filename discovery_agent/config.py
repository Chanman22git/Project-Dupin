import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
_APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.getenv("DATABASE_PATH", os.path.join(_APP_DIR, "discovery_agent.db"))
BASE_URL = os.getenv("BASE_URL", "http://localhost:8501")

CLAUDE_MODEL = "claude-sonnet-4-20250514"
DEFAULT_MAX_TOKENS = 4096
JSON_MAX_TOKENS = 8192

# Agent behavior defaults
DEFAULT_RESEARCH_DEPTH = "balanced"
DEFAULT_CLARIFICATION_MODE = "balanced"
DEFAULT_MAX_QUESTIONS = None  # No limit, wrap up naturally after 15-20 exchanges

# Link expiry defaults
DEFAULT_LINK_EXPIRY_HOURS = 72

# Conversation states
CONVERSATION_STATES = [
    "GREETING",
    "ROLE_EXPLORATION",
    "WORKFLOW_DEEP_DIVE",
    "PAIN_POINTS",
    "EXPECTATIONS",
    "WRAP_UP",
    "SUMMARY",
]

# Insight types
INSIGHT_TYPES = [
    "user_journey_step",
    "pain_point",
    "expectation",
    "workflow",
    "discrepancy",
    "feature_request",
    "behavior_pattern",
]

# Discrepancy types
DISCREPANCY_TYPES = ["user_vs_user", "user_vs_product"]

# Priority levels
PRIORITIES = ["critical", "high", "medium", "low"]
