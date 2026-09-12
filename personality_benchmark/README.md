# Personality Benchmark v0.1

This directory contains evaluation infrastructure, not personality truth.

## case authority

- `example_fixture`: synthetic infrastructure test; never used to infer IXXIMEOW.
- `validated`: a real situation reviewed and accepted by the user.

A real case should preserve the original context, incoming interaction,
relationship state and uncertainty. It may define multiple acceptable expressions,
but behavior actions and boundary expectations remain independently scoreable.

## supported comparisons

- same message across different relationship states (`same_message_group`)
- expected no response
- multiple acceptable and explicitly unacceptable expressions
- acceptable and unacceptable behavior actions
- expected uncertainty signals
- boundary handling
- correction-derived lesson candidates

Adding a validated case does not automatically create a learned preference or
modify `PersonalityCore`. Feedback must pass the separate learning authority flow.
