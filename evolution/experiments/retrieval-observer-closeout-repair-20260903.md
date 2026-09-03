# Retrieval observation closeout repair

Status: **Accepted — observation repair only**

Iteration 2 has completed and its runtime candidate is rejected and rolled back. This is bounded observation maintenance in response to the user's repair request; it is not a third runtime candidate or permission to restart the terminated model loop.

- Evidence: the frozen v1.1 candidate matrix records `.\\mvnw.cmd` test executions as `other`; the largest is 20,980 bytes in a non-tail cell. Tail audit also shows real source reads through `$root='module'; Get-Content "$root/src/Example.java"` that do not establish the first-read flag because v1.1 requires the complete path to appear literally.
- Exact scope: `benchmarks/retrieval_metrics.py`, `benchmarks/test_retrieval_metrics.py`, observation receipts and maintainer documentation only.
- General changes: recognize `.cmd`, `.bat`, `.exe` suffixes on existing build/test command families; resolve only statically known, local literal string interpolation for source-path detection. Do not execute shell code or infer environment/dynamic values. Preserve quoted command-payload negative controls.
- Excluded: runtime Skill, topology, references, cases, answer scorers, task prompts, quality decisions, original manifests/results/transcripts, candidate rule and acceptance thresholds. Archive extraction and arbitrary shell evaluation remain outside this small repair.
- Version: bump observation metadata to 1.2. Test generic positive and negative shapes, including unbound variables and literal single-quoted strings.
- Validation: focused deterministic tests and tree self-test; replay both complete 54-cell transcripts with their original tracked source paths into a new `benchmark-results/retrieval-observer-closeout-replay/` directory. Preserve every non-observation result field and all direct output/token/tool/duration measurements. Report category/convergence differences explicitly; do not claim these derived counters were unchanged.
- Decision boundary: observation repair may be retained only if deterministic contract tests and paired replay invariants pass. The iteration-2 cost rejection is already determined by unchanged direct metrics. No n=3 or further runtime candidate is authorized by this repair.

## Results

- 48 deterministic tests and the tree self-test pass. Positive/negative tests cover platform launchers, quoted command payloads, local literal interpolation, unbound/dynamic variables and single-quoted strings.
- Offline replay: `benchmark-results/retrieval-observer-closeout-replay/`, 54 baseline and 54 candidate records. Recalculation with the frozen v1.1 implementation exactly reproduces every original observational field, validating the transcript/path inputs. Version 1.2 preserves all non-observational fields, output hashes, command hashes, direct costs, duplicate counts, whole-file/dependency byte totals and large-output counts.
- Build classifications change from 18 to 30 events in baseline and 22 to 37 in candidate; build-attributed bytes change from 38,377 to 122,931 and 68,780 to 160,886 respectively. These are category repairs, not new model behavior or reduced output.
- Frozen-tail broad-after-first-read totals change from v1.1's 0/1 to v1.2's **1/3** (baseline/candidate). The derived mechanism still fails the original non-increase/halving requirement; it is a post-hoc diagnostic, not a replacement frozen qualification result.
- Manual audit finds both sensitive-content arms already return project source in event 3, but each compound command ends with a failed search. The conservative event-success rule establishes the first read at event 4 instead. Counts therefore remain command-shape estimates rather than a complete shell execution trace. This limitation is retained explicitly, not repaired by treating every failed read as successful.
- Original results hashes remain `affd7d952fd76b0b885e1a2b35c00d32c377460ff6f5a4b8bb455e90fd06d9cb` and `ffcea417ddfc70a546475015d3339076efb1a53e757b899ef33eff32664738f3`. Raw artifacts were not rewritten and no model was rerun.
- The direct input-token and tool-call regressions independently preserve the rejected decision. Timing is now telemetry only under the user's subsequent instruction; removing its gate does not change the decision.
