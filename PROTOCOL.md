# ixximeow protocol

## 1. purpose

ixximeow is a personal autonomous content operating system.

it exists to reduce the amount of manual decision-making required to build, maintain, and evolve the ixximeow identity across platforms.

the system does not exist to generate content for the sake of generating content.

its job is to determine what is worth doing.

---

## 2. core loop

the system operates through a continuous loop:

observe
→ understand
→ decide
→ plan
→ act
→ verify
→ record
→ learn

every meaningful action should belong to this loop.

---

## 3. fundamental object

the fundamental object of ixximeow is the decision.

the system should continuously answer:

- what is happening?
- what matters?
- what are the available options?
- what is the best action now?
- should the action be taken automatically?
- what happened after the action?
- what should change because of the result?

---

## 4. separation of responsibilities

the llm is the reasoning layer.

code is the execution layer.

the llm should decide what should happen.

deterministic code should perform actions, manage state, validate outputs, communicate with external systems, and record results.

the llm must not be treated as the filesystem, database, scheduler, or source of truth.

---

## 5. state, memory, history

state describes what is happening now.

memory describes what the system has learned and should remember.

history describes what happened.

these concepts must remain separate.

state may change frequently.

memory should change deliberately.

history should be append-oriented and traceable.

---

## 6. decisions

important decisions must be explicit.

a decision should contain:

- objective
- current context
- available options
- constraints
- selected action
- reasoning summary
- confidence
- execution status
- result
- learning

the system should be able to explain why an important action happened.

---

## 7. autonomy

ixximeow supports three autonomy levels.

### advisor

the system analyzes and recommends.

the human decides.

### executor

the system prepares and executes approved actions.

publication or sensitive actions may still require approval.

### autonomous

the system may independently plan, create, execute, and learn within explicitly defined permissions.

autonomy must never be broader than the permissions granted to the system.

---

## 8. human checkpoints

human approval should remain available for:

- final identity-sensitive visual approval
- sensitive personal communication
- major changes to identity
- high-risk publication decisions
- actions outside defined permissions

automation should remove repetitive work, not remove judgment where judgment matters.

---

## 9. content principle

content should originate from objectives, observations, experiments, hypotheses, and opportunities.

the system must not optimize for posting frequency alone.

quality, distinctiveness, continuity, and relevance take priority over volume.

---

## 10. identity continuity

the system must preserve the established ixximeow identity across outputs.

identity includes:

- visual appearance
- visual atmosphere
- personality
- language
- humor
- behavioral patterns
- platform-specific expression

generated content must not gradually drift into generic influencer behavior.

---

## 11. platform separation

each platform is a different environment.

x
= thoughts, psychology, observations, provocation, humor.

instagram
= curated visual archive.

tiktok
= personality, reactions, spontaneity.

snapchat
= everyday life and closeness.

onlyfans
= intimate and sensual access.

the same identity may appear differently across platforms without becoming inconsistent.

---

## 12. verification

the system must verify important outputs before considering an action complete.

verification may include:

- technical validity
- identity consistency
- platform compatibility
- policy constraints
- duplication
- quality
- expected objective

successful execution does not necessarily mean successful outcome.

---

## 13. learning

every meaningful action should produce a result.

results should be evaluated against the original objective.

the system should distinguish between:

- observation
- correlation
- hypothesis
- evidence
- conclusion

the system must not turn one successful or unsuccessful result into an unjustified permanent rule.

---

## 14. anti-patterns

ixximeow must avoid:

- random content generation
- fake autonomy
- unnecessary llm calls
- using the llm for deterministic operations
- storing everything as memory
- treating engagement as the only objective
- generic influencer behavior
- identity drift
- blind automation
- unexplained important decisions
- optimizing complexity instead of usefulness

---

## 15. engineering principle

build the smallest system that can make the next correct decision.

do not build infrastructure merely because it looks impressive.

every component must have a reason to exist.

complexity must be earned.

---

## 16. source of truth

github is the source of truth for the project architecture and code.

important architectural changes must be documented and versioned.

temporary experiments must not silently become permanent architecture.

---

## 17. guiding question

at any moment, ixximeow should be able to answer:

what is worth doing now?
