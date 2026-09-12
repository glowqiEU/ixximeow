# Personality Benchmark v0.1

This directory contains evaluation infrastructure, not personality truth.

## case authority

- `example_fixture`: synthetic infrastructure test; never used to infer IXXIMEOW.
- `inferred_example`: unconfirmed hypothesis; never used as personality truth.
- `user_confirmed_real_case`: a separate strict record supplied or reviewed by the user.

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

## first real case

Copy `templates/real_case.template.json` and fill it with one situation. The
provenance value must remain `user_confirmed_real_case`. Use the exact incoming
message when possible, describe only relevant relationship context, select the
behavior action you would actually choose, and leave `ideal_response` null when
the correct behavior is silence.

The initial taxonomy is organizational rather than personality evidence:
casual/friends, buyers/commercial, annoying/boundary pressure, flirting,
soft/caring, serious discussion, random observation/humor, conflict, no-response,
and ambiguous situations.
