# ixximeow — master roadmap

## purpose

build ixximeow as a personal operating system for identity, content, decisions, execution, and learning.

the system should become more autonomous without becoming less understandable.

core question:

> what is worth doing now?

---

# 0. foundation

### purpose
define what the system is before building more machinery.

### components
- protocol
- architecture
- identity
- decisions
- roadmap

### status
done

### done when
- system principles are explicit
- architecture has a defined direction
- identity rules are explicit
- important architectural decisions are documented

---

# 1. data model

### purpose
define the objects the system operates on.

### components
- goal
- decision
- task
- result
- history event
- system state

### status
in progress

### done when
- objects have stable IDs
- relationships are explicit
- lifecycle rules are defined
- serialization is reliable
- tests cover the core models

---

# 2. persistence

### purpose
make the system survive restarts.

### components
- goal store
- task store
- result store
- history store
- state store

### status
in progress

### done when
- runtime state can be saved and restored
- goals/tasks/results/history persist correctly
- runtime data is separated from source code
- corrupted or missing data is handled safely

---

# 3. decision system

### purpose
make the system choose what is worth doing.

### components
- context builder
- candidate generation
- decision engine
- decision reasons
- priorities
- constraints

### status
in progress

### done when
- decisions are generated from context
- options can be compared
- decisions have explicit reasons
- constraints can reject bad actions
- every decision is traceable

---

# 4. brain / reasoning

### purpose
connect the language model to the deterministic system.

### components
- reasoning layer
- structured outputs
- model routing
- context selection
- confidence
- escalation

### status
planned

### done when
- llm is used for reasoning, not basic filesystem/state operations
- model calls are intentional and measurable
- structured decisions can be validated
- stronger models are used only when needed

---

# 5. memory

### purpose
allow ixximeow to learn without turning everything into permanent memory.

### components
- short-term context
- long-term memory
- identity memory
- preference memory
- learned patterns
- memory retrieval
- memory pruning

### status
planned

### rule

state = what is happening now.

memory = what the system has learned.

history = what happened.

these must remain separate.

### done when
- relevant memory can be retrieved
- irrelevant memory is ignored
- memories have provenance
- memory can be updated or removed
- identity-critical memory is protected

---

# 6. planner

### purpose
turn decisions into executable plans.

### components
- task decomposition
- dependencies
- sequencing
- deadlines
- priorities
- replanning

### status
in progress

### done when
- a decision can produce a valid plan
- tasks can depend on other tasks
- failed tasks can trigger replanning
- unnecessary tasks are avoided

---

# 7. action engine / tools

### purpose
allow the agent to actually do things.

### components
- filesystem tools
- web/research tools
- image tools
- browser/API tools
- publishing tools
- analytics tools

### status
planned

### done when
- tools have explicit schemas
- permissions are defined
- actions are logged
- failures are recoverable
- dangerous actions require approval

---

# 8. content engine

### purpose
make content decisions based on identity, goals, context, and evidence.

### components
- content ideas
- content states
- hypotheses
- hooks
- captions
- platform adaptation
- content calendar
- repurposing

### status
planned

### rule

content must come from the person underneath the system.

not random daily generation.

### done when
- system can identify what content is worth making
- content is platform-aware
- content remains recognizably ixximeow
- ideas can be evaluated before production
- published content can be connected to outcomes

---

# 9. visual engine

### purpose
create and evaluate visual content without identity drift.

### components
- identity reference library
- scene generation
- image generation
- visual constraints
- continuity checks
- visual quality assurance

### status
planned

### done when
- generated images preserve physical continuity
- visual DNA is enforced
- generic influencer outputs are rejected
- human approval can be required
- visual results are stored and traceable

---

# 10. platform adapters

### purpose
separate ixximeow's identity from platform-specific mechanics.

### components
- x
- instagram
- tiktok
- snapchat
- onlyfans
- future platforms

each adapter should define:

- format
- constraints
- publishing
- scheduling
- analytics
- platform-specific behavior

### status
planned

### done when
- content can be adapted without rewriting the core system
- platform rules are isolated
- publishing actions are permissioned
- results return to the learning system

---

# 11. scheduler

### purpose
decide when the system should wake up.

### components
- scheduled tasks
- event triggers
- deadlines
- state triggers
- retries
- priority queue

### rule

do not call the llm every hour just because a clock exists.

use event/state-driven execution whenever possible.

### done when
- system wakes for meaningful reasons
- recurring tasks are supported
- failed tasks can retry safely
- unnecessary model calls are avoided

---

# 12. permissions & autonomy

### purpose
control what the system is allowed to do.

### autonomy levels

#### advisor
suggests actions.

#### executor
prepares and performs approved actions.

#### autonomous
acts within predefined permissions.

### components
- permission scopes
- approval gates
- sensitive-action rules
- autonomy levels
- audit log

### status
planned

### done when
- every external action has a permission level
- sensitive actions require approval
- autonomy can be increased gradually
- every autonomous action is traceable

---

# 13. analytics

### purpose
measure what actually happened.

### components
- content metrics
- platform metrics
- task outcomes
- decision outcomes
- experiment results
- cost telemetry

### status
planned

### rule

engagement is a signal, not the entire objective.

### done when
- actions have measurable outcomes
- metrics can be connected to decisions
- cost per action is visible
- vanity metrics cannot silently become the objective

---

# 14. learning

### purpose
turn outcomes into better future decisions.

### components
- feedback
- pattern detection
- experiments
- hypothesis tracking
- decision evaluation
- memory updates

### status
planned

### done when
- the system can identify what worked
- the system can identify what failed
- learning can change future decisions
- experiments are distinguishable from assumptions

---

# 15. cost control

### purpose
keep autonomy economically sane.

### components
- token tracking
- model routing
- cached context
- image cost tracking
- search/API cost tracking
- cost budgets

### status
planned

### done when
- every meaningful model/tool call can be measured
- expensive reasoning is used selectively
- monthly budget limits can be enforced
- cost is visible to the user

---

# 16. verification

### purpose
prevent the system from confidently doing stupid things.

### components
- schema validation
- action validation
- identity validation
- content QA
- visual QA
- result verification
- failure detection

### status
planned

### done when
- actions are verified after execution
- invalid outputs are rejected
- important actions have explicit verification
- failures are recorded rather than hidden

---

# 17. dashboard

### purpose
make the system understandable to its human operator.

### components
- current goal
- current decision
- active tasks
- recent history
- memory
- approvals
- analytics
- costs
- autonomy level

### status
planned

### done when
the user can understand:

- what ixximeow is doing
- why it is doing it
- what happened
- what it learned
- what it wants permission to do
- what it costs

---

# 18. evaluation

### purpose
prove that the system actually improves.

### components
- unit tests
- integration tests
- agent evaluations
- identity tests
- decision benchmarks
- regression tests

### status
planned

### done when
- core behavior is tested
- regressions are detected
- agent decisions can be evaluated
- identity drift can be tested
- autonomy is tested before being increased

---

# 19. deployment

### purpose
move from local prototype to reliable always-on system.

### components
- environment configuration
- secrets management
- database
- scheduler service
- workers
- monitoring
- backups
- recovery

### status
planned

### done when
- system can run without the development laptop
- secrets are isolated
- failures are observable
- data can be recovered

---

# 20. final autonomous loop

the finished system should operate approximately like this:

observe
↓
retrieve relevant context
↓
understand current state
↓
identify objective
↓
generate options
↓
evaluate options
↓
choose decision
↓
create plan
↓
execute actions
↓
verify results
↓
record history
↓
update state
↓
learn
↓
repeat

the human remains in control of permissions and identity-critical decisions.

---

# definition of done

ixximeow is not "done" because it can chat.

it is done when the system can:

- understand what is happening
- understand what matters
- decide what is worth doing
- explain why
- make a plan
- execute actions
- verify results
- remember useful things
- learn from outcomes
- preserve identity
- respect permissions
- control its own costs
- know when it needs the human

---

# development rule

we build one layer at a time.

for every layer:

1. define the contract
2. implement the smallest useful version
3. write tests
4. run tests
5. inspect behavior
6. commit
7. push
8. only then move forward

complexity must be earned.

---

# current position

foundation: done

data model: in progress

persistence: in progress

decision system: in progress

planner: in progress

everything after this: planned

the next goal is not to make the system bigger.

the next goal is to make the existing core structurally correct.
