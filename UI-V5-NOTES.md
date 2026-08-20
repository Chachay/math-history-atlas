# V5 UI integration notes

This revision ports the V5 mobile mock's visual grammar into the React SPA while keeping the canonical data pipeline intact.

## Views

- **Atlas**: responsive SVG field evolution; branching and recombination are the primary visual language.
- **Network**: entities are rendered as typed nodes and curated Story paths are overlaid on top of the same historical graph.
- **Story**: vertical card reading with a sticky parallel-story rail.
- **Person**: profile and contribution index fed from generated data.

## Data boundary

Run `python scripts/build.py` before starting the SPA. The build synchronizes `generated/*.json` to `app/public/data/`. The React application fetches those files at runtime.

## Deliberate prototype limits

The current sample dataset is still small. Some Network coordinates and Atlas projection geometry are seed-layout definitions for the PoC; they are not intended to be the V10 layout engine.
