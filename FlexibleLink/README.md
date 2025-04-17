## Requirements

- [`uv`](https://docs.astral.sh/uv/getting-started/installation/)
- `.dat` files in `./FelxibleLink/data` directory

## Development

### clone

```sh
git clone https://github.com/kanarus/SystemEngineeringExperiment2025
```

### run

```sh
cd FlexibleLink
uv run ./src/cmd/graphviz.py ./data/<NAME>.dat
```

### options

- `-a` : amplify valley of Bode Gain plot
- `-n <int>` : specify repeat number of `filter_by_y_increase_continuity`
