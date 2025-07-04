from pydantic import (
    BaseModel,
    Field,
)

from app.session import Session


class State(BaseModel):
    """Application state of mcp-anon server"""
    # TODO: Support multiple session.
    # Needed if MCP server is a remote service with multiple users.
    session: Session = Field(default_factory = Session)

