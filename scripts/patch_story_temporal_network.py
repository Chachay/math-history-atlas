from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]

# 1) Extend Story schema with explicit temporal anchors and an explicit retrospective edge.
models_path = ROOT / 'scripts/models.py'
models = models_path.read_text(encoding='utf-8')
models = models.replace(
"""class StoryStep(BaseModel):
    id: str; ref: str; role: str
    narrative: str | None = None
    assertion_refs: list[str] = []
    perspective: Perspective | None = None
""",
"""class StoryStep(BaseModel):
    id: str; ref: str; role: str
    narrative: str | None = None
    assertion_refs: list[str] = []
    perspective: Perspective | None = None
    temporal_anchor: Period | None = None
""",
)
models = models.replace(
"type: Literal['continues','branches','converges','alternative']",
"type: Literal['continues','branches','converges','alternative','retrospective']",
)
models_path.write_text(models, encoding='utf-8', newline='\n')

# 2) Validate chronology on reviewed narrative Stories. Backward edges must be explicit retrospective links.
validate_path = ROOT / 'scripts/validate.py'
validate = validate_path.read_text(encoding='utf-8')
old = """        for step in story.steps:
            if step.ref not in ref_ids: errors.append(f'invalid StoryStep ref {step.ref} in {story.id}')
            if step.narrative and not step.assertion_refs:
                errors.append(f'narrative without assertion_refs on {step.id} in {story.id}')
            for assertion_id in step.assertion_refs:
                if assertion_id not in assertion_ids:
                    errors.append(f'unknown StoryStep assertion_ref {assertion_id} on {step.id} in {story.id}')
"""
new = """        for step in story.steps:
            if step.ref not in ref_ids: errors.append(f'invalid StoryStep ref {step.ref} in {story.id}')
            if step.narrative and not step.assertion_refs:
                errors.append(f'narrative without assertion_refs on {step.id} in {story.id}')
            if step.narrative and step.temporal_anchor is None:
                errors.append(f'narrative StoryStep missing temporal_anchor on {step.id} in {story.id}')
            for assertion_id in step.assertion_refs:
                if assertion_id not in assertion_ids:
                    errors.append(f'unknown StoryStep assertion_ref {assertion_id} on {step.id} in {story.id}')
"""
if old not in validate:
    raise RuntimeError('validate StoryStep block not found')
validate = validate.replace(old, new, 1)
old = """        g=nx.DiGraph(); g.add_nodes_from(step_ids)
        for link in story.links:
            if link.from_ not in step_ids or link.to not in step_ids: errors.append(f'invalid StoryLink in {story.id}')
            else: g.add_edge(link.from_,link.to)
        if not nx.is_directed_acyclic_graph(g): errors.append(f'Story DAG cycle detected: {story.id}')
"""
new = """        by_step={x.id:x for x in story.steps}
        g=nx.DiGraph(); g.add_nodes_from(step_ids)
        for link in story.links:
            if link.from_ not in step_ids or link.to not in step_ids: errors.append(f'invalid StoryLink in {story.id}')
            else:
                g.add_edge(link.from_,link.to)
                source=by_step[link.from_].temporal_anchor
                target=by_step[link.to].temporal_anchor
                if source and target and source.from_ is not None and target.from_ is not None:
                    if target.from_ < source.from_ and link.type != 'retrospective':
                        errors.append(f'backward StoryLink requires retrospective type: {story.id} {link.from_}->{link.to}')
        if not nx.is_directed_acyclic_graph(g): errors.append(f'Story DAG cycle detected: {story.id}')
"""
if old not in validate:
    raise RuntimeError('validate StoryLink block not found')
validate = validate.replace(old, new, 1)
validate_path.write_text(validate, encoding='utf-8', newline='\n')

# 3) Add Story-local temporal anchors to researched Stories.
def load_story(path):
    rows = yaml.safe_load(path.read_text(encoding='utf-8'))
    return rows

def save_story(path, rows):
    path.write_text(yaml.safe_dump(rows, sort_keys=False, allow_unicode=True, width=120), encoding='utf-8', newline='\n')

r001_path = ROOT / 'editorial/stories/r001-fourier.yaml'
r001 = load_story(r001_path)
anchors1 = {
    'r001-story-1': (1807, 1822),
    'r001-story-2': (1807, 1822),
    'r001-story-3': (1807, 1822),
    'r001-story-4': (1807, 1822),
    'r001-story-5': (1807, 1822),
    'r001-story-6': (1822, 1829),
    'r001-story-7': (1829, 1829),
    'r001-story-8': (1830, 1850),
}
for step in r001[0]['steps']:
    a, b = anchors1[step['id']]
    step['temporal_anchor'] = {'from': a, 'to': b}
save_story(r001_path, r001)

r002_path = ROOT / 'editorial/stories/r002-cauchy.yaml'
r002 = load_story(r002_path)
story = r002[0]
anchors2 = {
    'r002-story-1': (1821, 1821),
    'r002-story-2': (1821, 1821),
    'r002-story-3': (1821, 1821),
    'r002-story-4': (1821, 1821),
    'r002-story-5': (1827, 1827),
    'r002-story-6': (1826, 1826),
    'r002-story-7': (1853, 1853),
    'r002-story-8': (1853, 1860),
}
for step in story['steps']:
    a, b = anchors2[step['id']]
    step['temporal_anchor'] = {'from': a, 'to': b}
# The 1826 continuity problem and 1827 periodic-series memoir are parallel branches from the 1821 convergence problem.
story['links'] = [
    {'from': 'r002-story-1', 'to': 'r002-story-2', 'type': 'continues'},
    {'from': 'r002-story-2', 'to': 'r002-story-3', 'type': 'continues'},
    {'from': 'r002-story-3', 'to': 'r002-story-4', 'type': 'continues'},
    {'from': 'r002-story-4', 'to': 'r002-story-5', 'type': 'branches'},
    {'from': 'r002-story-4', 'to': 'r002-story-6', 'type': 'branches'},
    {'from': 'r002-story-6', 'to': 'r002-story-7', 'type': 'continues'},
    {'from': 'r002-story-7', 'to': 'r002-story-8', 'type': 'branches'},
]
save_story(r002_path, r002)

# Mark the previous Story review as needing a transition-only re-review because the DAG links changed.
review_path = ROOT / 'editorial/reviews/R002-cauchy-story-review.yaml'
review = yaml.safe_load(review_path.read_text(encoding='utf-8'))
review['review']['status'] = 'needs_transition_re_review'
review.setdefault('resolution', {})['note'] = (
    'Narrative findings remain resolved. After temporal anchors were introduced, the Story DAG was changed so the 1826 '
    'continuity problem and 1827 periodic-series memoir are parallel branches from the 1821 convergence problem. '
    'The revised transition structure requires a focused Story-link re-review before final editorial acceptance.'
)
review_path.write_text(yaml.safe_dump(review, sort_keys=False, allow_unicode=True, width=120), encoding='utf-8', newline='\n')

# 4) Replace Network geometry with temporal Story occurrences. Same ref+year merges; same-year groups stack vertically.
main_path = ROOT / 'app/src/main.tsx'
main = main_path.read_text(encoding='utf-8')
main = main.replace(
"type StoryStep = { id: string; ref: string; role: string; narrative?: string; assertion_refs?: string[]; perspective?: string };",
"type StoryStep = { id: string; ref: string; role: string; narrative?: string; assertion_refs?: string[]; perspective?: string; temporal_anchor?: { from?: number; to?: number | null } };",
)
start = main.index('type NetworkPoint = ')
end = main.index('\nfunction NetworkView(', start)
replacement = r'''type NetworkPoint = { x: number; y: number; year: number; ref: string; storyIds: string[] };
type NetworkLayout = {
  positions: Record<string, NetworkPoint>;
  stepKeys: Record<string, string>;
  yearRows: { year: number; y: number }[];
  minYear: number;
  maxYear: number;
  height: number;
};

function stableFraction(id: string) {
  let hash = 0;
  for (let i = 0; i < id.length; i += 1) hash = (Math.imul(hash, 31) + id.charCodeAt(i)) | 0;
  return (Math.abs(hash) % 1000) / 1000;
}

function stepYear(step: StoryStep, item?: Entity | Question) {
  const explicit = step.temporal_anchor?.from;
  if (typeof explicit === 'number') return explicit;
  if (!item) return 1800;
  return 'type' in item ? (item.start_year || 1800) : (item.period?.from || 1800);
}

function buildNetworkLayout(data: Dataset, lookup: Record<string, Entity | Question>): NetworkLayout {
  const storyIndex = new Map(data.stories.map((story, index) => [story.id, index]));
  const laneMin = 76;
  const laneMax = 285;
  const laneStep = data.stories.length > 1 ? (laneMax - laneMin) / (data.stories.length - 1) : 0;

  // A Network point is a temporal occurrence, not a timeless entity. Occurrences merge only when ref+year match.
  const groups = new Map<string, { ref: string; year: number; storyIds: string[]; stepIds: string[] }>();
  const stepKeys: Record<string, string> = {};
  data.stories.forEach(story => story.steps.forEach(step => {
    const item = lookup[step.ref];
    if (!item) return;
    const year = stepYear(step, item);
    const key = `${step.ref}@${year}`;
    const group = groups.get(key) || { ref: step.ref, year, storyIds: [], stepIds: [] };
    if (!group.storyIds.includes(story.id)) group.storyIds.push(story.id);
    group.stepIds.push(`${story.id}:${step.id}`);
    groups.set(key, group);
    stepKeys[`${story.id}:${step.id}`] = key;
  }));

  const byYear = new Map<number, string[]>();
  groups.forEach((group, key) => {
    const rows = byYear.get(group.year) || [];
    rows.push(key);
    byYear.set(group.year, rows);
  });
  const years = [...byYear.keys()].sort((a, b) => a - b);
  const minYear = years[0] || 1750;
  const maxYear = years[years.length - 1] || 1860;
  const positions: Record<string, NetworkPoint> = {};
  const yearRows: { year: number; y: number }[] = [];
  let cursor = 52;
  const rowGap = 42;
  const yearGap = 34;

  years.forEach(year => {
    const keys = (byYear.get(year) || []).sort((a, b) => a.localeCompare(b));
    const firstY = cursor;
    keys.forEach((key, index) => {
      const group = groups.get(key)!;
      const lanes = group.storyIds.map(id => storyIndex.get(id) || 0);
      let x = laneMin + (lanes.reduce((a, b) => a + b, 0) / Math.max(1, lanes.length)) * laneStep;
      if (group.storyIds.length === 1) x += (stableFraction(key) - 0.5) * 22;
      positions[key] = {
        x: Math.max(62, Math.min(292, x)),
        y: cursor + index * rowGap,
        year,
        ref: group.ref,
        storyIds: group.storyIds,
      };
    });
    yearRows.push({ year, y: firstY });
    cursor += Math.max(1, keys.length) * rowGap + yearGap;
  });

  return { positions, stepKeys, yearRows, minYear, maxYear, height: Math.max(640, cursor + 20) };
}
'''
main = main[:start] + replacement + main[end:]

# Replace NetworkView body with link-segment rendering instead of a single polyline through step array.
fn_start = main.index('function NetworkView(')
fn_end = main.index('\nfunction NetworkNode(', fn_start)
network_fn = r'''function NetworkView({ data, selectedStory, setSelectedStory, onOpenStory, onOpenPerson, onSheet }: {
  data: Dataset; selectedStory: string; setSelectedStory: (x: string) => void; onOpenStory: (x: string) => void; onOpenPerson: (x: string) => void; onSheet: (n: React.ReactNode) => void;
}) {
  const lookup = useMemo(() => buildLookup(data), [data]);
  const canonicalIntersections = new Map(data.intersections.map(i => [i.entity, i]));
  const storyIds = ['all', ...data.stories.map(s => s.id)];
  const layout = useMemo(() => buildNetworkLayout(data, lookup), [data, lookup]);

  const pointForStep = (story: Story, stepId: string) => {
    const key = layout.stepKeys[`${story.id}:${stepId}`];
    return key ? layout.positions[key] : undefined;
  };
  const segmentPath = (story: Story, from: string, to: string) => {
    const a = pointForStep(story, from); const b = pointForStep(story, to);
    if (!a || !b) return '';
    const mid = (a.y + b.y) / 2;
    return `M${a.x} ${a.y} C${a.x} ${mid} ${b.x} ${mid} ${b.x} ${b.y}`;
  };

  return <>
    <section className="hero-card"><h2>Network — {layout.minYear}–{layout.maxYear} · chronological Story graph</h2><p>Years define order, not proportional distance. Same-year events are stacked inside a year band. Story lines follow explicit DAG links, so parallel branches split and later continuations do not imply a trip backward in time.</p><div className="entity-legend"><span><i className="person-mark" />Person</span><span><i className="concept-mark" />Concept</span><span><i className="work-mark" />Work</span></div></section>
    <section className="panel network-panel">
      <div className="story-filter">{storyIds.map(id => <button key={id} className={selectedStory === id ? 'active' : ''} onClick={() => setSelectedStory(id)}>{id !== 'all' && <i className="story-dot" style={{ background: storyColor(id) }} />}{id === 'all' ? 'All paths' : data.stories.find(s => s.id === id)?.title}</button>)}</div>
      <svg className="network-svg" viewBox={`0 0 360 ${layout.height}`}>
        <line x1="38" y1="30" x2="38" y2={layout.height - 20} className="time-axis" />
        {layout.yearRows.map(row => <g key={row.year}><text x="7" y={row.y} className="year-label">{row.year}</text><line x1="34" y1={row.y - 4} x2="42" y2={row.y - 4} className="year-tick" /></g>)}
        {data.stories.flatMap(story => story.links.map(link => <path key={`${story.id}:${link.from}:${link.to}`} d={segmentPath(story, link.from, link.to)} className={`story-overlay ${link.type === 'retrospective' ? 'retrospective' : ''} ${selectedStory !== 'all' && selectedStory !== story.id ? 'dim' : ''}`} style={{ stroke: storyColor(story.id) }} />))}
        {Object.entries(layout.positions).map(([key,p]) => {
          const item = lookup[p.ref]; if (!item) return null;
          const canonical = canonicalIntersections.get(p.ref);
          const temporalIntersection = p.storyIds.length > 1 && canonical
            ? { ...canonical, story_count: p.storyIds.length, stories: p.storyIds }
            : undefined;
          return <NetworkNode key={key} id={p.ref} item={item} x={p.x} y={p.y} intersection={temporalIntersection} onClick={() => {
            if (canonical) onSheet(<IntersectionSheet intersection={canonical} data={data} onOpen={onOpenStory} />);
            else if ('type' in item && item.type === 'Person') onOpenPerson(p.ref);
          }} />;
        })}
      </svg>
    </section>
  </>;
}
'''
main = main[:fn_start] + network_fn + main[fn_end:]

# Story reading order is chronological by temporal anchor, stable within the same year.
main = main.replace(
"""      {story.steps.map((step, idx) => {
""",
"""      {[...story.steps].sort((a, b) => (a.temporal_anchor?.from ?? 9999) - (b.temporal_anchor?.from ?? 9999) || story.steps.indexOf(a) - story.steps.indexOf(b)).map((step, idx) => {
""",
1,
)
main_path.write_text(main, encoding='utf-8', newline='\n')

# CSS support for year bands and explicit retrospective edges.
css_path = ROOT / 'app/src/style.css'
css = css_path.read_text(encoding='utf-8')
if '.year-tick' not in css:
    css += '\n.year-tick{stroke:#cfd6df;stroke-width:1}.story-overlay.retrospective{stroke-dasharray:5 4;opacity:.55}\n'
css_path.write_text(css, encoding='utf-8', newline='\n')

print('Applied temporal Story anchors, chronology validation, DAG link rendering, and same-year stacking.')
