# ixximeow decisions

this document records important architectural decisions.

decisions should explain not only what was chosen, but why.

---

## D001 — decision-first architecture

### decision

the fundamental object of ixximeow is the decision.

### why

ixximeow is not primarily a chatbot or content generator.

its purpose is to determine what is worth doing now and then move that decision toward execution.

content, tasks, experiments, and publications are consequences of decisions.

---

## D002 — llm is the reasoning layer

### decision

the llm is responsible for reasoning, interpretation, prioritization, planning, and judgment.

deterministic code is responsible for execution.

### why

using an llm for filesystem operations, state management, scheduling, validation, or other deterministic work increases cost and decreases reliability.

the llm should decide.

the system should execute.

---

## D003 — state, memory, and history are separate

### decision

state, memory, and history must be represented separately.

### why

mixing them creates an opaque system.

state answers:

"what is happening now?"

memory answers:

"what should the system remember?"

history answers:

"what happened?"

these have different lifecycles and should not become one generic data store.

---

## D004 — context must be selective

### decision

the system should retrieve relevant context rather than automatically sending the entire history to the llm.

### why

full-history prompting increases cost, noise, latency, and the probability of irrelevant reasoning.

context should be assembled for the current decision.

---

## D005 — decisions must be inspectable

### decision

important decisions must have structured records.

### why

an autonomous system that cannot explain which objective, context, constraints, and reasoning produced an action is difficult to debug and difficult to trust.

important actions must remain traceable to their originating decision.

---

## D006 — execution and outcome are different

### decision

successful execution must not automatically be interpreted as successful outcome.

### why

an action can execute perfectly and still fail its objective.

example:

a post can publish successfully while performing badly.

the system must therefore record both:

execution result
and
objective result.

---

## D007 — autonomy is permissioned

### decision

autonomy is bounded by explicit permissions.

### why

previous approval does not imply unlimited future permission.

the system must know which actions are:

- automatically allowed
- approval-required
- forbidden

---

## D008 — human checkpoints remain part of the system

### decision

human approval remains available for identity-sensitive and high-impact actions.

### why

automation should remove repetitive work without removing human judgment where identity, relationships, privacy, or meaningful consequences are involved.

---

## D009 — content is objective-driven

### decision

content should originate from objectives, observations, hypotheses, experiments, and opportunities.

### why

posting frequency is not a sufficient objective.

random generation creates volume without direction.

---

## D010 — platform logic is isolated

### decision

platform-specific behavior belongs inside platform adapters.

### why

x, instagram, tiktok, snapchat, and onlyfans have different environments and requirements.

the core system should reason about objectives and actions without becoming dependent on one platform's implementation.

---

## D011 — identity is a system constraint

### decision

identity continuity is not merely a prompt.

it is a system-level constraint.

### why

identity drift can happen gradually through generated images, captions, trends, and optimization.

identity therefore requires persistent rules, references, validation, and learning signals.

---

## D012 — verification is mandatory for important actions

### decision

important actions must have verification criteria.

### why

execution without verification creates false confidence.

the system must know whether the produced result is valid before treating the action as complete.

---

## D013 — learning requires evidence

### decision

the system must distinguish observations from hypotheses and conclusions.

### why

one successful post, one failed experiment, or one unusual result is not enough to establish a permanent rule.

learning must remain probabilistic and revisable.

---

## D014 — scheduler is event-driven

### decision

the scheduler should trigger work because something needs to happen, not because the clock happened to reach another hour.

### why

calling the llm every hour without a meaningful trigger wastes resources and creates artificial activity.

time can be an event, but time alone is not a reason to think.

---

## D015 — build the smallest useful system first

### decision

implementation begins with the smallest system capable of making and recording a useful decision.

### why

architecture should be earned by requirements.

unnecessary infrastructure creates maintenance cost before value exists.

---

## D016 — mvp begins with the decision engine

### decision

the first functional mvp should implement:

observe
→ context
→ decision
→ action
→ result
→ learning

### why

this validates the core intelligence of the system before adding complex integrations.

social platforms, image generation, scheduling, analytics, and dashboards can then become capabilities attached to a working decision system.

---

## D017 — github is the source of truth

### decision

github is the canonical source of project architecture and code.

### why

important changes must be versioned, reviewable, and recoverable.

local experiments must not silently become the architecture.

---

## D018 — architecture evolves through decisions

### decision

major architectural changes must be recorded here.

### why

the system should preserve the reasoning behind its evolution.

future decisions may invalidate earlier ones, but they should not erase the history of why the earlier choice existed.

---

## decision format

future architectural decisions should follow:

### decision

what was chosen.

### alternatives

what else was considered.

### why

why the decision was made.

### consequences

what this decision enables or prevents.

### status

proposed / accepted / superseded

---

## current architectural direction

the current direction is:

decision-first
+
tool-using
+
permissioned autonomy
+
persistent state
+
curated memory
+
traceable history
+
verification
+
learning

the system should become more autonomous without becoming less understandable.

---

## D019 — decision evaluation is separate from decision selection

### decision

candidate decisions should be evaluated before selection.

`Decision` represents a proposed action.

`DecisionEvaluation` represents an assessment of that action in the current context.

evaluation contains:

- `relevance` — how directly the decision serves the current objective and context
- `confidence` — how strongly the available evidence supports the decision
- `risk` — potential downside, uncertainty, or irreversibility
- `effort` — expected execution cost or complexity
- `reason` — explanation of the evaluation

normalized evaluation signals use a range from `0.0` to `1.0`.

### alternatives

1. select decisions using priority only
2. evaluate only after a decision has already been selected
3. evaluate candidate decisions before selection

### why

priority alone is insufficient for a system that must eventually make context-sensitive decisions.

post-hoc evaluation would explain a decision but would not improve the selection itself.

evaluating candidates before selection allows the system to compare decisions using context, evidence, risk, and expected effort.

the evaluation mechanism should remain replaceable.

possible implementations include:

- deterministic rules
- llm-assisted evaluation
- learning-based evaluation
- hybrid evaluation

### consequences

decision selection becomes a two-stage process:

candidates

→ evaluation

→ selection

the selection scoring policy must be explicitly defined and tested before it becomes part of the production decision engine.

selection score belongs to the selection layer, not to `DecisionEvaluation`.

evaluation must use available evidence and must not invent unsupported facts.

the evaluation layer should remain independent from the mechanism used to produce the evaluation.

### status

accepted

---

## D020 — decision, plan, and task are separate contracts

### decision

a selected decision must pass through an explicit plan before becoming a task.

`Decision` answers: what should be done and why.

`Plan` answers: how the selected decision is decomposed into work.

`Task` answers: what concrete unit of work is currently being executed.

`Action` remains the concrete operation executed for a task.

### alternatives

1. create a task directly from `Decision.action`
2. make `Task` responsible for both planning and execution
3. introduce an explicit `Plan` boundary

### why

directly copying `Decision.action` into `Task.title` collapses two different responsibilities and makes later multi-step planning difficult to introduce safely.

an explicit plan boundary allows the system to add real decomposition later without changing the meaning of a decision or task.

### consequences

the intended execution lineage is:

`goal → decision → plan → task → action → execution → result → outcome`

for the current MVP, `Plan` deliberately contains one step. this establishes the contract without inventing planning intelligence before it is needed.

### status

accepted
