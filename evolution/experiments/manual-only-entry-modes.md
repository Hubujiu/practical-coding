# Experiment: manual-only interaction modes

Status: **candidate implemented; validation pending**

## Observation

A previous candidate placed requirements clarification (`grill-me` style) and Decision before Core as model-selected gates. That makes interaction-heavy behavior part of every task's control policy and lets the model infer when to question or seek a choice.

## Hypothesis

Clarification and Decision are useful when explicitly requested, but should not compete with Core/E0 in adaptive routing. Moving them outside the tree should reduce unnecessary questioning and preserve user control without removing the capabilities.

## Candidate change

- default entry is Core/E0;
- remove automatic Intent/Clarification and Decision gates;
- move both references under `references/manual/`;
- require an explicit current user request for activation;
- prohibit one manual mode from automatically routing to another;
- exclude manual modes from adaptive `capability_path` and minimum-sufficient depth;
- add a negative benchmark target: spontaneous manual-mode activation on ordinary tasks = 0.

## Validation

Compare ordinary coding tasks before/after for quality, interaction turns, tokens, and spontaneous manual activation. Separately run explicit opt-in clarification/decision tasks to ensure the moved capabilities still add value when requested.

## Result

Pending fresh benchmark and real-project evidence.