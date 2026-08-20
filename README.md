# Math History Atlas

A mobile-first SPA and research pipeline for representing modern mathematical history as a **historical graph + curated stories + derived story intersections**, rather than as a single timeline.

## Architecture

- `research/`: candidate packets, critic reviews, research gaps, and reusable LLM prompts.
- `data/`: canonical historical entities, assertions, questions, concept states, and field polyhierarchy.
- `editorial/`: revisable story DAGs and collections.
- `generated/`: compiler output consumed by the SPA.
- `scripts/`: validation and build/compiler steps.
- `app/`: React/TypeScript/Vite prototype with Atlas, Network, Story, and Person views.

Core separation: **historical facts != historical interpretation != story narrative**. UI projections are also separate from the full graph.

## Data flow

```text
Research
→ Candidate Packet
→ Historical Critic
→ Human review
→ Accepted canonical data
→ Build
→ Generated JSON
→ SPA
```

## Local setup (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/validate.py
pytest
python scripts/build.py
cd app
npm install
npm run dev
```

Use Python 3.12+ and Node.js 22+.

## Validation and build

```powershell
python scripts/validate.py
pytest
python scripts/build.py
```

The validator checks duplicate IDs, dangling references, source coverage, predicates, field parents, periods, story references, and DAG cycles. Invalid data returns a non-zero exit code.

## Research Packet workflow

1. Run `research/prompts/cluster-research-v1.md` for a bounded cluster.
2. Save output under `research/packets/`; it is not canonical yet.
3. Review it with `historical-critic-v1.md`.
4. Human-check high-impact causal/motivational claims and sources.
5. Promote accepted entities/questions/assertions into `data/`.
6. Run validation/build.
7. Use `story-editor-v1.md` only against accepted data; unsupported narrative transitions become `RESEARCH_GAP` items.

## GitHub PR review workflow

Keep review units small (roughly 5–15 assertions). PRs should summarize the proposed question transition, evidence, perspective, and expected story/network effect. CI runs tests, validation, generated-data build, and SPA build before merge. GitHub Mobile can then serve as the human approval surface.

## Sample data

The PoC sample is in `data/**/core.yaml`, `editorial/stories/core.yaml`, and `sources/core.yaml`. It covers Euler, Fourier, Cauchy, Riemann, early analysis concepts, and three intersecting stories. Interpretive claims are deliberately marked as candidates where specialist verification is still required.

## Next steps

1. Replace sample candidate claims with source-verified research packets for Fourier/convergence/function.
2. Add a PR-summary generator optimized for mobile review.
3. Expand through Cantor, Lebesgue, Hilbert, topology/cohomology, Serre, and Grothendieck.
4. Improve Atlas projection and interactive graph rendering without changing canonical graph semantics.

## V5 mobile UI

The React SPA now follows the V5 interaction mock more closely:

- **Atlas** — chronological field evolution with branching and recombination.
- **Network** — historical nodes with multiple Story paths overlaid; shared nodes become intersections.
- **Story** — vertical editorial reading with a parallel-Story rail.
- **Person** — contribution/profile index generated from canonical data.

`scripts/build.py` also mirrors generated JSON into `app/public/data/`, so the SPA consumes build products rather than hard-coded mock objects.
