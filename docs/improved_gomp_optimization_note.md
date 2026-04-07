# Improved-gOMP Design Notes

## Overview

`Improved-gOMP` is an engineering extension of the `gOMP` recovery loop. The goal of this implementation is not to replace the baseline family with a universally dominant variant, but to provide a clearer design space for experimenting with candidate screening, tail refinement, rescue behavior, and incremental least-squares solvers.

This note summarizes the current implementation status, the explored directions, and the default choices retained in the repository.

## Why the Algorithm Was Reworked

Early versions of `Improved-gOMP` showed a recurring pattern:

- support precision was often strong
- false positives were low
- recall could become too conservative
- NMSE gains were not uniform
- runtime did not improve relative to `gOMP`

That pattern suggested a practical issue: the method was acting more like an overly cautious selector than a balanced recovery procedure.

## Implemented Improvements

The current codebase keeps the method within the greedy group-selection family and introduces the following engineering modules:

- adaptive screening pool sizing
- adaptive group sizing under a fixed support budget
- candidate reranking with raw-correlation and debiased scores
- optional gain-aware shortlist reranking
- optional tail refinement for late-stage support decisions
- optional local forward-backward swap near the target support size
- optional two-phase tail policy
- incremental Gram and Cholesky-based support solvers
- rescue logic with solver snapshot and restore

The baseline consistency fixes introduced alongside this work are also important:

- `OMP` and `gOMP` now follow more consistent support-budget semantics
- `gOMP` no longer overshoots the target sparsity budget when selecting a final group

## Default Choices Retained

Not every implemented module improved the aggregate results. The repository therefore keeps a conservative default profile:

- `Improved-gOMP` uses its own `improved_group_size` setting instead of silently changing the `gOMP` baseline
- incremental Cholesky-based solving is enabled by default
- aggressive tail modules remain configurable, but are not all enabled by default at the same time

This keeps the public benchmark stable while preserving the exploratory paths for ablation or follow-up work.

## Code Structure

The algorithm was also refactored to reduce coupling between concerns:

- configuration is assembled explicitly before entering the main recovery loop
- runtime state is stored separately from static options
- rescue, tail swap, candidate selection, and solver management are split into helper functions
- experiment-side parameter mapping is centralized in `experiments/common.py`

This makes it easier to review the recovery loop and to expose new modules without turning the experiment runner into a large block of ad hoc parameter plumbing.

## Current Interpretation of Results

The repository's current results support a narrow and defensible interpretation:

- `OMP` remains the strongest accuracy-oriented baseline in many settings
- `gOMP` remains the runtime-oriented group baseline
- `Improved-gOMP` is best understood as a precision-oriented tradeoff variant

In other words, the implementation is useful because it exposes a recoverable tradeoff region, not because it is globally dominant.

## Guidance for Public Presentation

For a public repository, the safest framing is:

> `Improved-gOMP` is a modular engineering variant of `gOMP` that explores precision-oriented support updates and incremental solver strategies under a reproducible sparse recovery benchmark.

Avoid framing it as:

- a universal replacement for `OMP`
- a universal replacement for `gOMP`
- a stable runtime winner

## Where to Look Next

If further work is needed, the most natural follow-up directions are:

- tighter forward-backward support pruning
- more selective tail-only lookahead policies
- stronger numerical updates for incremental least squares
- cleaner separation between algorithm modules and experiment configuration
