# `mcp-anon` Anonymization Helper MCP server

- Augments LLM with knowledge specific to anomization processes.
- Give LLM controlled access to your sensitive data.
  By default, `mcp-anon` only shares column names, data types, schema and
  synthetic examples to LLM. It does not give LLM your sensitive data directly.

  This prevents your data from leaking to LLM providers which typically store
  your interactions with LLM for further training.
- LLM hallucinates and can not be trusted to operate on your data directly.
  This MCP only let LLM select limited operations to add to your anonymization
  procedure and let you review the procedure first.
- Produce reusable anonymization procedure, not just producing anonymized data once.
  - TODO: There should be an option for end user to directly build anonymization
    procedure by passing LLM if needed. This likely will requires us to work on
    MCP client side.

