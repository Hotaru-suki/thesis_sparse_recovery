# Algorithm Boundary Notes

## Direct Baselines

- `OMP`: retained as the classic single-atom greedy baseline.
- `gOMP`: retained as the group-selection baseline and the direct parent family for `Improved-gOMP`.

## Literature-Inspired Extensions

- The adaptive screening logic in `improved_gomp` is inspired by adaptive partial-selection ideas, but the pool sizing, reranking, and rescue rules in this repository are engineering choices rather than a line-by-line reproduction of any one paper.
- The noise-aware stopping behavior is motivated by noisy sparse recovery literature, but the concrete stop policy here is repository-specific.
- `rmp.py` is included as an exploratory implementation for comparison and code organization purposes, not as a primary benchmark baseline.

## Repository-Specific Engineering Additions

- incremental Gram and Cholesky-based support solvers
- aligned support-budget semantics across `OMP`, `gOMP`, and `Improved-gOMP`
- experiment output organization under `raw`, `aggregated`, and `logs`
- ablation and parameter-sensitivity runners
- supporting notes for traceability, experiment protocol, and design boundaries

## Deliberately Excluded Directions

- preconditioned `gOMP` variants are not part of the main implementation path
- multi-path pursuit variants are not included in the default benchmark flow
- block-sparse extensions are outside the current repository scope

The goal of these limits is to keep the project centered on a compact greedy sparse-recovery benchmark instead of expanding into multiple unrelated pursuit families.
