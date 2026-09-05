# ixximeow architecture

## 1. system model

ixximeow is an autonomous content operating system.

it is composed of specialized layers rather than one large agent.

the system follows:

observe
→ retrieve context
→ understand
→ decide
→ plan
→ execute
→ verify
→ record
→ learn

the llm is the reasoning engine.

deterministic software is responsible for execution and system integrity.

---

## 2. high-level architecture

```text
                    ┌─────────────────────┐
                    │      scheduler      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    orchestrator     │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
        ┌───────────┐   ┌─────────────┐   ┌─────────────┐
        │  context  │   │   decision  │   │   planner   │
        │  engine   │   │   engine    │   │             │
        └─────┬─────┘   └──────┬──────┘   └──────┬──────┘
              │                │                 │
              └────────────────┼─────────────────┘
                               ▼
                    ┌─────────────────────┐
                    │    action engine    │
                    └──────────┬──────────┘
                               │
          ┌────────────┬───────┼──────────┬────────────┐
          ▼            ▼       ▼          ▼            ▼
      content       visual   platform   analytics    tools
       engine       engine   adapters
          │            │       │          │
          └────────────┴───────┼──────────┴────────────┘
                               ▼
                    ┌─────────────────────┐
                    │ verification layer │
                    └──────────┬──────────┘
                               ▼
                    ┌─────────────────────┐
                    │ state / memory /    │
                    │ history / database  │
                    └─────────────────────┘
