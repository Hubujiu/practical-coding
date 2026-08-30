# Performance

Load only for a measured performance problem or an explicit material latency, throughput, memory, query, render, or scale requirement.

## Procedure

- Define the metric, workload, and acceptable boundary before optimizing.
- Measure or use existing profiling evidence to identify the dominant cost.
- Change the narrowest dominant cause first.
- Prefer eliminating work, I/O, allocations, queries, renders, or algorithmic cost over adding caches or concurrency.
- Re-measure the same workload after the final change and check correctness first.

Do not optimize from intuition alone. Do not add caching, batching, async work, indexes, or parallelism without evidence that the targeted cost is material.

## Exit evidence

The same representative workload shows the required improvement or disproves the suspected bottleneck, with correctness preserved.
