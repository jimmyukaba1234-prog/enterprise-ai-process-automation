"""
Shared schemas for the AI Customer Operations Agent.
"""

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class CustomerComplaint:
    """
    Standard input object for every customer complaint/request.
    This is what enters the AI agent pipeline first.
    """
    customer_id: str
    complaint_text: str
    channel: str = "web_app"
    session_id: Optional[str] = None
    created_at: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)



@dataclass
class IntentResult:
    intent: str
    confidence: float

    category: str
    sentiment: str
    priority: str

    requires_api: bool

    requires_confirmation: bool = False
    requires_knowledge_base: bool = True
    requires_escalation: bool = False

    required_entities: list[str] = field(default_factory=list)
    missing_information: list[str] = field(default_factory=list)

    extracted_entities: dict[str, Any] = field(default_factory=dict)

    needs_clarification: bool = False
    clarification_question: str | None = None

    ready_to_resolve: bool = False

    recommended_action: str | None = None

    customer_response: str | None = None




@dataclass
class KnowledgeChunk:
    chunk_id: int
    source: str
    content: str
    score: float


@dataclass
class RetrievalResult:
    query: str
    chunks: list[KnowledgeChunk]
    combined_context: str


@dataclass
class APICallResult:
    api_name: str
    function_name: str
    success: bool
    action_completed: bool
    source_system: str
    response: dict[str, Any]


@dataclass
class ResolutionResult:
    status: str
    customer_response: str
    assigned_department: str
    priority: str
    escalation_required: bool
    escalation_reason: Optional[str] = None
    actions_taken: list[str] = field(default_factory=list)
    api_results: list[APICallResult] = field(default_factory=list)


@dataclass
class EscalationSummary:
    ticket_id: str
    customer_id: str
    issue_type: str
    priority: str
    assigned_department: str
    summary: str
    actions_taken: list[str]
    outstanding_items: list[str]
    recommended_next_steps: list[str]


@dataclass
class AgentResponse:
    """
    Final output returned to Streamlit UI and ticket writer.
    """
    ticket_id: str
    customer_id: str
    original_message: str
    intent: str
    sentiment: str
    assigned_department: str
    priority: str
    status: str
    customer_response: str
    escalation_required: bool
    escalation_summary: Optional[str]
    api_called: list[str]
    knowledge_sources: list[str]
    created_at: str
    raw: dict[str, Any] = field(default_factory=dict)