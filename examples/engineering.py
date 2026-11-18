"""Provider-neutral examples for EL's Prompt Engineering.

Educational only: the in-memory service is not a production security boundary.
"""
from dataclasses import dataclass
from decimal import Decimal
from uuid import uuid4


def build_prompt(question: str, language: str) -> list[dict[str, str]]:
    if language not in ("English", "Arabic"):
        raise ValueError("Unsupported language")
    if not question.strip():
        raise ValueError("Empty question")
    return [
        {"role": "developer", "content": f"Tutor in {language}. Do not invent facts."},
        {"role": "user", "content": question},
    ]


def estimate_cost(input_tokens: int, output_tokens: int,
                  input_rate: Decimal, output_rate: Decimal) -> Decimal:
    if (type(input_tokens) is not int or type(output_tokens) is not int
            or input_tokens < 0 or output_tokens < 0):
        raise ValueError("Token counts must be nonnegative integers")
    if (not input_rate.is_finite() or not output_rate.is_finite()
            or input_rate < 0 or output_rate < 0):
        raise ValueError("Rates must be finite and nonnegative")
    return (Decimal(input_tokens) * input_rate +
            Decimal(output_tokens) * output_rate) / Decimal(1_000_000)


@dataclass(frozen=True)
class Draft:
    title: str
    description: str


@dataclass(frozen=True)
class Ticket:
    id: str
    owner: str
    draft: Draft


class MockTicketService:
    """Single-process teaching example; production requires durable atomic writes."""
    def __init__(self):
        self._approved: dict[str, tuple[str, Draft]] = {}
        self._completed: dict[str, Ticket] = {}
        self._tickets: dict[str, Ticket] = {}

    def approve(self, authenticated_user: str, draft: Draft) -> str:
        # Call only after a real user approves the exact draft in a trusted UI.
        if not authenticated_user or not draft.title.strip() or not draft.description.strip():
            raise ValueError("Missing approval data")
        key = str(uuid4())
        self._approved[key] = (authenticated_user, draft)
        return key

    def create(self, authenticated_user: str, key: str, draft: Draft) -> Ticket:
        if self._approved.get(key) != (authenticated_user, draft):
            raise PermissionError("No matching approval")
        if key in self._completed:
            return self._completed[key]
        ticket = Ticket(str(uuid4()), authenticated_user, draft)
        self._tickets[ticket.id] = ticket
        self._completed[key] = ticket
        return ticket

    def get(self, authenticated_user: str, ticket_id: str) -> Ticket:
        ticket = self._tickets.get(ticket_id)
        if ticket is None or ticket.owner != authenticated_user:
            raise LookupError("Ticket unavailable")
        return ticket
