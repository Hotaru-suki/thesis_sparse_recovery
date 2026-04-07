# Contributing

## Scope

This repository is a compact sparse-recovery experiment project. Contributions should preserve that focus. Large framework-style changes, unrelated algorithm families, or broad dependency growth are usually a poor fit unless they clearly improve reproducibility or benchmark quality.

## Recommended Workflow

1. Create a small, focused branch.
2. Keep changes scoped to one concern when possible: algorithm behavior, experiment plumbing, documentation, or reproducibility.
3. Update tests or add targeted coverage when algorithm behavior changes.
4. Document any new config fields, metrics, or output files.

## Coding Notes

- Prefer small helper functions over expanding experiment runners or algorithm loops inline.
- Keep baseline semantics explicit. Do not silently retune `OMP` or `gOMP` while presenting the change as an `Improved-gOMP` modification.
- Avoid adding heavy dependencies unless they are necessary for reproducibility or core functionality.

## Validation

Before submitting changes, run:

```bash
python -m unittest tests.test_algorithms tests.test_config_and_main -q
```

If you modify experiment output structure or plotting behavior, also run the relevant experiment or sweep and verify that generated CSV and figure names remain coherent.

## Documentation

Update the following when relevant:

- `README.md` for repository positioning or usage changes
- `configs/README.md` for config field changes
- `results/README.md` for output layout changes
- `docs/` notes for algorithm boundary or traceability changes
