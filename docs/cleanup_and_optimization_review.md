# Cleanup and Optimization Review

Generated after aligning the project with the current experiment code and CSV
outputs. The thesis `.docx` file is intentionally out of scope here.

Experiment scope is now locked: main experiments and supplementary clean/noise
experiments should be retained and included in the thesis where possible. The
main chapter should carry the central comparisons; appendix or supplemental
analysis can carry lower-priority figures.

## Current State

- Main experiment CSV files are structurally usable and match current configs.
- `deepseek_ready/` has been regenerated from the current CSV files.
- All 35 PNG figures have matching text summaries.
- The formal insertion plan uses 20 main-text candidate figures.
- 15 additional PNG files are appendix or supplementary candidate figures.
- Pytest-based validation currently passes.

## Cleanup Candidates

### Keep

- `results/raw/*.csv`
- `results/aggregated/*.csv`
- official figures listed in `deepseek_ready/insertion_plan.md`
- `deepseek_ready/`
- supplementary clean/noise CSV files that are explicitly documented
- `results/logs/` if run provenance is needed locally

### Include as Appendix or Supplementary Where Possible

These should be included where possible, preferably in appendix or supplemental
analysis if they do not fit the main result narrative:

- `figures/ablation_clean_*.png`
- `figures/ablation_noise_*.png`
- `figures/sparsity_easy_*.png`
- `figures/sparsity_m96_*.png`
- `figures/*_backup.png`

### Can Be Removed or Archived Later

Do not delete automatically without confirmation. These are scratch comparison
outputs and are already ignored by git:

- `tmp_balance_check*/`
- `tmp_memory_check/`
- `tmp_release_check/`
- `tmp_runtime_release/`
- `tmp_speedup_check*/`
- `tmp_speedup_final*/`

### Final Deliverable Scope

The worktree contains many modified and untracked result artifacts. The final
deliverable should include:

- main experiment outputs
- supplementary clean/noise outputs
- current raw/aggregated breakdown files that support runtime and memory claims
- `deepseek_ready/` as a thesis handoff artifact
- appendix/supplementary figure explanations

## Fixed During Review

- `README.md` now follows the current code and CSV outputs.
- `docs/experiment_protocol.md` now lists current row counts and implementation
  behavior.
- `docs/experiment_figure_index.md` now distinguishes official candidate
  figures from auxiliary figures.
- `deepseek_ready/generate_summaries.py` now generates summaries from current
  CSV files instead of hard-coded old results.
- `experiments/run_param_sensitivity.py` now maps scanned parameters to the
  actual `Improved-gOMP` kwargs:
  - `screening_ratio` also sets `improved_screening_ratio` and
    `optimized_screening_ratio`
  - `group_size` also sets `improved_group_size`
  - full profiling is enabled so `screening_pool_size_avg` is meaningful
- `param_sensitivity.csv`, its summary, and its two figures were regenerated.
- Tests were extended to catch the parameter-sensitivity mapping issue.
- Config and dispatch tests were converted to pytest-style parameterized tests.
- `pytest.ini` was added, and `python -m pytest` is now the primary validation command.

## Remaining Code Optimization Opportunities

These are worth considering, but should be done before final experiment
freezing because they may change outputs or timings.

1. **Consolidate repeated algorithm info dictionaries**

   `algorithms/omp.py`, `algorithms/gomp.py`, and `algorithms/rmp.py` each have
   a local `_build_info()` function with nearly identical fields. A shared
   helper in `utils/` would reduce drift in exported metrics.

2. **Deduplicate incremental solver cache logic**

   `IncrementalGramSolver` and `IncrementalCholeskySolver` share `support`,
   `gram`, `rhs`, `snapshot`, `restore`, and `extend` behavior. A small base
   cache class would make solver changes safer.

3. **Split `experiments/common.py`**

   The file currently handles algorithm specs, trial execution, summaries,
   speedups, memory exports, runtime breakdowns, and plotting dispatch. A later
   cleanup could split it into:

   - `algorithm_specs.py`
   - `runner.py`
   - `summaries.py`
   - `exports.py`

4. **Make supplementary experiments first-class**

   Files such as `ablation_clean.csv` and `sparsity_clean_m96.csv` are useful,
   but they are not reachable through `main.py --all`. A future cleanup could
   add explicit entry points or a `--supplementary` mode.

5. **Improve figure naming**

   Official and auxiliary figures currently share the same directory. A cleaner
   layout would be:

   ```text
   figures/official/
   figures/supplementary/
   figures/archive/
   ```

   This would require updating paths in summaries and insertion plans.

6. **Reduce RMP ambiguity**

   RMP is exploratory and often performs poorly in ESR under current settings.
   Keep it clearly described as exploratory, or move it to supplementary
   comparisons if the thesis narrative focuses on OMP/gOMP/Improved-gOMP.

## Remaining Experiment Optimization Opportunities

1. **Add confidence intervals or standard deviations**

   Current summaries mostly report means. Adding std/CI columns would make
   claims about differences more defensible.

2. **Add `support_overlap_ratio`**

   `CLAUDE.md` recommends this metric. It is not currently exported directly.
   It can be computed from support sets during trials or approximated from
   precision/recall and false-positive/false-negative counts.

3. **Stabilize final figure set**

   Before thesis insertion, choose whether official figures should use the
   noisy sparsity experiment (`sparsity.csv`) or a clean supplementary sparsity
   experiment. The current insertion plan uses `sparsity.csv`.

4. **Run one final full benchmark after code freeze**

   Because code and parameter-sensitivity behavior changed, a final
   reproducibility pass should be run after all code decisions are settled.

5. **Clarify speed-quality tradeoffs**

   Optimized implementations improve runtime/memory, but recovery quality can
   differ from baseline because implementation options are not purely mechanical
   in every case. Thesis text must explicitly separate implementation speedups
   from algorithmic recovery claims.

## Recommended Next Step

Before editing the thesis body, freeze the project scope:

1. Keep supplementary outputs in the final deliverable unless a specific file is
   shown to be obsolete.
2. Decide whether appendix/supplementary figures stay in `figures/` or move to a
   subdirectory.
3. Run the final selected experiments once.
4. Regenerate `deepseek_ready/`.
5. Only then begin thesis `.docx` verification and revision.
