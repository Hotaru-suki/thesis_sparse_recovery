# Reproducibility

## Environment

Recommended minimum environment:

- Python 3.10+
- dependencies from `requirements.txt`

Create an environment and install dependencies:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows:

```powershell
py -m venv .venv
.\.venv\Scripts\activate
python -m pip install -r requirements.txt
```

## Core Validation

Run the unit tests:

```bash
python -m unittest tests.test_algorithms tests.test_config_and_main -q
```

## Regenerating Results

Run a single experiment:

```bash
python main.py --exp snr
python main.py --exp runtime
```

Run the full benchmark set:

```bash
python main.py --all
```

Optional overrides:

```bash
python main.py --exp snr --seed 20260408 --trials 10 --outdir .
```

## Output Locations

- trial data: `results/raw/`
- aggregated summaries: `results/aggregated/`
- run metadata: `results/logs/`
- figures: `figures/`

For the runtime experiment, the repository now also emits:

- `summary_speedup_<algorithm>.csv`
- `summary_runtime_breakdown_<algorithm>.csv`
- `summary_memory_breakdown_<algorithm>.csv`
- `summary_memory_speedup_<algorithm>.csv`

## Practical Notes

- The repository includes tracked result artifacts. If you regenerate outputs, expect CSV and figure diffs.
- If you work in WSL, create a Linux virtual environment instead of reusing a Windows virtual environment directly.
- The benchmark is seed-controlled, but floating-point behavior and linear algebra backends can still introduce small numerical differences across platforms.
