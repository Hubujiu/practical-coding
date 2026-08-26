# Quality-gated skill scorecard

This repository does not rank Skills by adding quality and cost into one unconstrained sum. That would let a cheap unsafe result compensate for a safety failure, or let a tiny quality gain justify an arbitrarily expensive workflow.

## Evidence behind the design

- [HELM](https://arxiv.org/abs/2211.09110) evaluates accuracy and efficiency as separate metrics so trade-offs remain visible rather than disappearing into one headline.
- [MLCommons](https://mlcommons.org/benchmarks/) describes performance relative to a target quality metric and treats reproducibility and affordability as benchmark goals. The corresponding pattern here is quality first, performance second.
- [Efficient Benchmarking of Language Models](https://arxiv.org/abs/2308.11696) shows that rankings can be sensitive to benchmark composition. This is why the scorecard retains per-suite and per-case results, requires repeated paired runs, and does not treat a smoke profile as a ranking.
- [ENAMEL](https://arxiv.org/abs/2406.06647) extends correctness-oriented evaluation with an explicit efficiency measure. The project uses the same separation of functional qualification from efficiency, but its cost index below is project-specific rather than copied from `eff@k`.

## Gate, frontier, and diagnostic index

For Practical `p` and comparator `b`, first require:

1. every paired case has at least three determinate repetitions;
2. `pass_p >= pass_b - 0.03` at suite level;
3. no lower suite safety or build rate;
4. no case-level safety regression.

The three-point pass margin encodes the project's explicit tolerance for a small general-quality difference. Safety has zero margin. Infrastructure failures make the sample provisional; cost never repairs a failed quality gate.

The report then preserves the Pareto result over pass/correct/safe/build quality dimensions and uncached-input/output-token/time/tool-call/LOC cost dimensions. One arm dominates only when it is no worse on every available dimension and strictly better on at least one.

For a quality-qualified pair, relative efficiency is:

`E = exp(sum_i(w_i * ln(C_b,i / C_p,i)))`

with weights 0.35 uncached input tokens, 0.15 output tokens, 0.35 model time, and 0.15 tool calls. Available weights are renormalized if a metric is absent. `E > 1` favors Practical. Cached input and total tokens remain reported but are excluded because cache reuse makes them less portable across runs.

The optional diagnostic index is:

`U = ((Q_p + 0.01) / (Q_b + 0.01))^2 * E`

where `Q` is suite pass rate. Squaring makes quality differences matter more than any single cost dimension, while the prior gate prevents the formula from buying away safety or material quality loss. `U` is a relative sensitivity summary, not an absolute score and not a substitute for the Pareto table.

The weights and three-point margin are declared project policy, not constants claimed by the cited papers. Release reports must publish the component ratios, so a reader can recompute the result with different weights. A final release judgment should remain unchanged under reasonable weight perturbations; otherwise the honest result is “trade-off,” not a winner.
