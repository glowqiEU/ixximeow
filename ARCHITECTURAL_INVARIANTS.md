# architectural invariants

These invariants define boundaries the system must preserve while the architecture evolves.

## 1. reasoning and execution are separate

LLM reasoning may propose, evaluate, or decide. Deterministic code executes operations and preserves system integrity.

## 2. one source of truth per runtime fact

A runtime fact must have one authoritative source. Consumers read that source rather than maintaining imported or duplicated mutable copies.

## 3. permissions are enforced before execution

The executor must not perform an action unless the task's required autonomy is available or a valid persisted approval authorizes the execution.

## 4. persisted approval is authoritative

An approval object supplied to execution is not sufficient by itself when approval is required. The persisted approval must match the task, required permission, identity, and approved status.

## 5. task state changes through lifecycle rules

Task status transitions must go through the task lifecycle contract. Callers must not silently manufacture invalid state transitions.

## 6. execution success and objective success are different

A successful execution means the requested operation completed. It does not by itself prove that the underlying objective was achieved.

## 7. important execution produces traceable results

An executed action must produce a Result with enough lineage to connect task, action, and execution. Verification remains a distinct boundary.

## 8. history is not current state

History records what happened. State records what is happening now. Memory records what the system has learned. These representations must not silently become interchangeable.

## 9. personality behavior precedes expression

The system chooses a typed behavior action before producing language. Expression must not silently choose or change the behavior.

## 10. identity quality and goal quality are separate gates

IdentityCritic evaluates whether an expression remains recognizably IXXIMEOW. GoalCritic evaluates whether the behavior serves the interpreted situation. Neither score substitutes for the other.

## 11. personality decisions do not grant execution authority

`TAKE_ACTION` is a proposed behavior, never permission to execute. External action continues through the existing task, permission, persisted approval, executor, and verification boundaries.

## 12. personality learning is typed and provenance-bearing

Semantic, episodic, relationship, and learned-preference memories remain distinguishable. A correction becomes a structured learning signal; it does not become permanent identity truth merely because it occurred once.

## 13. situation inference never becomes an observed fact

Raw interaction fields are recorded as observed facts. Intent and motive are uncertain inferences with confidence and evidence references. Inference may cite observations, history, or memory; it may not manufacture a new observed fact.

## 14. interpretation failure cannot authorize behavior

Malformed or failed situation interpretation produces no `SituationModel` and no action authority. Low-confidence interpretation fails closed to `WAIT` until evidence or human judgment resolves it.

## 15. relationship behavior requires explicit policy

Relationship state may change a behavior only through an inspectable configured rule. The default relationship-aware policy contains no guessed personality thresholds. Low-confidence relationship identity cannot trigger a relationship rule.

## 16. decision basis is metadata, not hidden reasoning

Every personality decision records concise situation signals, relationship signals, personality principles, boundary state, uncertainty, and chosen action. It must not store private chain-of-thought or an unbounded reasoning transcript.

## 17. learning promotion cannot mutate personality core

A single correction is an evidence candidate. Repeated consistent and deduplicated corrections may become a proposed learned preference. Neither status can modify `PersonalityCore`; durable principles require a future explicit approval boundary.

## 18. benchmark provenance determines evidence authority

Only a case explicitly marked `user_confirmed_real_case` may enter the real-user ground-truth store. Synthetic fixtures and inferred examples remain useful for infrastructure tests but have no personality-learning authority.

## 19. personality core contains no situation-specific truths

One-off behavior, temporary state, contextual preference, relationship preference, and channel expression preference remain scoped. A durable candidate requires compatible evidence across distinct contexts and relationship types, and still cannot enter `PersonalityCore` without explicit approval.

## 20. mirror ratings do not erase decision structure

`ME`, `CLOSE`, and `NOT_ME` feedback identifies a candidate while preserving its behavior action separately from its expression. Corrections to action, relationship, boundary, and wording remain separately auditable.

## 21. benchmark comparison is regression-aware

Repeated benchmark runs preserve per-case results. Aggregate improvement cannot hide a case that became less IXXIMEOW-like.

## testing rule

Every invariant that protects a meaningful system boundary should have a regression test. A passing implementation test is not enough when a boundary can be bypassed through another entry point.
