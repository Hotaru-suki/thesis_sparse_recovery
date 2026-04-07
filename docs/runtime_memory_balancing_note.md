# Runtime-Memory Balancing Note

This project now treats space optimization under the same comparison standard as runtime optimization:

- each experimental algorithm exposes `baseline` and `optimized` implementations
- runtime claims are supported by `summary_speedup_<algorithm>.csv`
- memory claims are supported by `summary_memory_speedup_<algorithm>.csv`

## Optimization Rule

The repository does not accept a memory optimization that simply shifts cost into a large runtime regression, and it does not accept a runtime optimization that silently inflates working memory without documenting the tradeoff.

The practical rule used in code is:

- optimize dominant runtime kernels first
- remove avoidable working-set overhead second
- keep final recovery metrics comparable to baseline
- record both runtime and estimated working-set deltas in the experiment outputs

## Current Code Directions

### OMP

- optimized path uses an incremental Cholesky solver
- full-iteration `x_hat` working buffers are avoided during the solve loop
- light profiling trims support-history storage while preserving final metrics

### gOMP

- optimized path solves only the current support-sized Gram system
- support-history storage is reduced in light profiling mode
- this currently gives both runtime and memory savings against baseline

### Improved-gOMP

- optimized path keeps the speed-first candidate caps and reduced refinement frequency
- light profiling mode trims candidate and support history storage
- this method is still primarily a runtime-first tradeoff variant; memory may remain above baseline because of incremental solver state

### RMP

- optimized path uses an incremental Gram solver
- the loop avoids keeping a persistent full-length coefficient buffer during intermediate steps
- light profiling mode trims support-history storage

## Output Files

For runtime experiments, the repository generates:

- `results/aggregated/summary_speedup_<algorithm>.csv`
- `results/aggregated/summary_runtime_breakdown_<algorithm>.csv`
- `results/aggregated/summary_memory_breakdown_<algorithm>.csv`
- `results/aggregated/summary_memory_speedup_<algorithm>.csv`

These files are intended to support thesis statements about both computational cost and working-memory tradeoffs.
