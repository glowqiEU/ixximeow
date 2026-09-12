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

## testing rule

Every invariant that protects a meaningful system boundary should have a regression test. A passing implementation test is not enough when a boundary can be bypassed through another entry point.
