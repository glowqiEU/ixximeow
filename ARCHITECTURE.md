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

## personality decision vertical slice

The personality subsystem is an isolated decision layer:

```text
interaction input
→ interpreted SituationModel
→ RelationshipState + PersonalityState + PersonalityCore
→ BehaviorDecision
→ optional Expression
→ IdentityCritic + GoalCritic
→ reply / no response / action proposal
→ typed memory + LearningSignal
```

`PersonalityCore` is stable identity knowledge. `PersonalityState` is temporary.
`RelationshipState` is person-specific. None of them may be silently substituted
for another.

The current slice begins at an already interpreted `SituationModel`. A future LLM
adapter may produce an interpretation payload. `SituationUnderstandingAdapter`
validates that payload into `SituationModel`; malformed output produces no
situation and no action authority. Observed facts and uncertain inferences remain
separate.

`ResponseDisposition` owns deterministic non-response and boundary semantics.
The relationship-aware policy can modify a behavior only through named configured
rules. It intentionally ships without guessed IXXIMEOW relationship rules.

Each decision exposes a bounded `DecisionBasis`: situation signals, applicable
relationship rules, relevant personality principles, boundary state, uncertainty,
and chosen action. This is audit metadata, not chain-of-thought.

`TAKE_ACTION` ends at an action proposal. It does not call the executor or bypass
the existing persisted approval boundary.

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
