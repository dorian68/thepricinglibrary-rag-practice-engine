# Backend Agent Instructions

Follow the root two-agent protocol.

Technical RL priority:
- Keep changes backend-first, deterministic, and CLI-testable.
- Prefer existing primitives: `ToolRegistry`, `ConversationLedger`, `TplMcpAdapter`, `AgentInteractionGateway`, `LocalStore`.
- Add or update smoke scripts under `scripts/` when behavior changes.
- Run focused `pytest` for Python changes and the narrowest relevant smoke before broader audits.

Business Client Mystere priority:
- Verify that API/CLI outputs are understandable to a paid quant-learning or pricing-workflow user.
- Do not accept fake finance numbers, untraceable generated results, or silent mutation.

Production guard:
- Generation and agent routes remain guarded by billing/auth/rate-limit policies before public exposure.
