## Requirements

- [`uv`](https://docs.astral.sh/uv/getting-started/installation/)
- CSV data files ( may be named as `〜.dat` in repeated_daq )

## Development

### clone

```sh
git clone https://github.com/kanarus/SystemEngineeringExperiment2025
```

### run

```sh
cd FlexibleLink
uv run ./src/cmd/graphviz.py ./path/to/data_file
```

### options

- `-n <int>` : number of repetition of `filter_by_y_increase_continuity`
  - at most 3-4 will be enough for data from long-runs
- `-a` : amplify valley of Bode Gain plot
  - will not be needed for data from long-runs
- `-p <float * 5>` : hand-estimated optimal parameters of the model
  - assigned to `a3`, `a2`, `a1`, `b2`, `b0` in this order
  - model: `P(s) = (b2*s^2 + b0) / (s^4 + a3*s^3 + a3*s^2 + a1*s)`

### example

```sh
uv run ./src/cmd/graphviz.py ./data/SKE2024_data11-Apr-2025_1445.dat
```

`FlexibleLink/data` directory is git-ignored.
