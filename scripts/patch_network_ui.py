from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if text.count(old) != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {text.count(old)}")
    return text.replace(old, new, 1)


root = Path(__file__).resolve().parents[1]
main_path = root / "app/src/main.tsx"
css_path = root / "app/src/style.css"
main = main_path.read_text(encoding="utf-8")
css = css_path.read_text(encoding="utf-8")

main = replace_once(
    main,
    "type Assertion = { id: string; subject: string; predicate: string; object: string; status?: string; perspective?: string };",
    "type Assertion = { id: string; subject: string; predicate: string; object: string; period?: { from?: number; to?: number | null }; status?: string; perspective?: string };",
    "assertion period type",
)

main = replace_once(
    main,
    """const storyPalette: Record<string, string> = {
  'story-rigor': '#2b78d0',
  'story-function': '#7759c8',
  'story-frequency': '#2d9163',
};
""",
    """function storyColor(id: string) {
  let hash = 2166136261;
  for (let i = 0; i < id.length; i += 1) {
    hash ^= id.charCodeAt(i);
    hash = Math.imul(hash, 16777619);
  }
  const hue = Math.abs(hash) % 360;
  return `hsl(${hue} 58% 44%)`;
}
""",
    "story palette",
)

old_positions = """const positions: Record<string, { x: number; y: number }> = {
  'person-euler': { x: 82, y: 58 },
  'person-fourier': { x: 96, y: 135 },
  'q-heat-propagation': { x: 258, y: 110 },
  'concept-infinite-series': { x: 155, y: 75 },
  'concept-fourier-series': { x: 155, y: 215 },
  'work-fourier-theorie': { x: 272, y: 265 },
  'person-cauchy': { x: 96, y: 330 },
  'work-cauchy-cours': { x: 128, y: 390 },
  'concept-convergence': { x: 84, y: 455 },
  'concept-function': { x: 210, y: 340 },
  'concept-continuity': { x: 202, y: 445 },
  'concept-uniform-convergence': { x: 88, y: 565 },
  'q-rigorous-limit-continuity': { x: 185, y: 555 },
  'q-what-is-function': { x: 268, y: 390 },
  'person-riemann': { x: 260, y: 525 },
};
"""
new_positions = """type NetworkPoint = { x: number; y: number; year: number };
type NetworkLayout = { positions: Record<string, NetworkPoint>; minYear: number; maxYear: number; ticks: number[] };

function stableFraction(id: string) {
  let hash = 0;
  for (let i = 0; i < id.length; i += 1) hash = (Math.imul(hash, 31) + id.charCodeAt(i)) | 0;
  return (Math.abs(hash) % 1000) / 1000;
}

function median(values: number[]) {
  const sorted = [...values].sort((a, b) => a - b);
  const middle = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[middle] : Math.round((sorted[middle - 1] + sorted[middle]) / 2);
}

function networkYear(id: string, item: Entity | Question, data: Dataset) {
  const assertionYears = data.graph.assertions
    .filter(a => a.subject === id || a.object === id)
    .map(a => a.period?.from)
    .filter((year): year is number => typeof year === 'number');
  if (assertionYears.length) return median(assertionYears);
  if ('type' in item) return item.start_year || 1800;
  return item.period?.from || 1800;
}

function niceTicks(minYear: number, maxYear: number) {
  const span = Math.max(20, maxYear - minYear);
  const raw = span / 4;
  const step = raw <= 10 ? 10 : raw <= 20 ? 20 : raw <= 25 ? 25 : raw <= 50 ? 50 : 100;
  const first = Math.ceil(minYear / step) * step;
  const ticks: number[] = [];
  for (let y = first; y <= maxYear; y += step) ticks.push(y);
  return ticks.length >= 2 ? ticks : [minYear, maxYear];
}

function buildNetworkLayout(data: Dataset, lookup: Record<string, Entity | Question>): NetworkLayout {
  const storyRefs = [...new Set(data.stories.flatMap(story => story.steps.map(step => step.ref)))].filter(id => lookup[id]);
  const years = storyRefs.map(id => networkYear(id, lookup[id], data));
  const rawMin = years.length ? Math.min(...years) : 1750;
  const rawMax = years.length ? Math.max(...years) : 1860;
  const padding = Math.max(10, Math.round((rawMax - rawMin) * 0.08));
  const minYear = Math.floor((rawMin - padding) / 10) * 10;
  const maxYear = Math.ceil((rawMax + padding) / 10) * 10;
  const storyIndex = new Map(data.stories.map((story, index) => [story.id, index]));
  const memberships = new Map<string, string[]>();
  data.stories.forEach(story => story.steps.forEach(step => {
    const current = memberships.get(step.ref) || [];
    if (!current.includes(story.id)) current.push(story.id);
    memberships.set(step.ref, current);
  }));
  const laneMin = 76;
  const laneMax = 285;
  const laneStep = data.stories.length > 1 ? (laneMax - laneMin) / (data.stories.length - 1) : 0;
  const yFor = (year: number) => 45 + ((year - minYear) / Math.max(1, maxYear - minYear)) * 550;
  const positions: Record<string, NetworkPoint> = {};
  storyRefs.forEach(id => {
    const memberStories = memberships.get(id) || [];
    const year = networkYear(id, lookup[id], data);
    let x = 180;
    if (memberStories.length === 1) {
      const lane = storyIndex.get(memberStories[0]) || 0;
      x = laneMin + lane * laneStep;
      x += (stableFraction(id) - 0.5) * 26;
    } else if (memberStories.length > 1) {
      const lanes = memberStories.map(story => storyIndex.get(story) || 0);
      x = laneMin + (lanes.reduce((a, b) => a + b, 0) / lanes.length) * laneStep;
    }
    positions[id] = { x: Math.max(62, Math.min(292, x)), y: yFor(year), year };
  });
  return { positions, minYear, maxYear, ticks: niceTicks(minYear, maxYear) };
}
"""
main = replace_once(main, old_positions, new_positions, "network positions")

old_network_setup = """  const intersections = new Map(data.intersections.map(i => [i.entity, i]));
  const storyIds = ['all', ...data.stories.map(s => s.id)];

  const storyPath = (story: Story) => {
    const pts = story.steps.map(s => positions[s.ref]).filter(Boolean);
    if (pts.length < 2) return '';
    return pts.map((p, i) => `${i ? 'L' : 'M'}${p.x} ${p.y}`).join(' ');
  };
"""
new_network_setup = """  const intersections = new Map(data.intersections.map(i => [i.entity, i]));
  const storyIds = ['all', ...data.stories.map(s => s.id)];
  const layout = useMemo(() => buildNetworkLayout(data, lookup), [data, lookup]);

  const storyPath = (story: Story) => {
    const pts = story.steps.map(s => layout.positions[s.ref]).filter(Boolean);
    if (pts.length < 2) return '';
    return pts.map((p, i) => `${i ? 'L' : 'M'}${p.x} ${p.y}`).join(' ');
  };
  const yForYear = (year: number) => 45 + ((year - layout.minYear) / Math.max(1, layout.maxYear - layout.minYear)) * 550;
"""
main = replace_once(main, old_network_setup, new_network_setup, "network setup")

old_network_render = """    <section className=\"hero-card\"><h2>Network — 1700–1860 · Analysis</h2><p>Historical entities remain the graph. Story paths are overlays. When several Stories pass through the same node, the intersection becomes visible without creating a separate “Junction” screen.</p><div className=\"entity-legend\"><span><i className=\"person-mark\" />Person</span><span><i className=\"concept-mark\" />Concept</span><span><i className=\"work-mark\" />Work</span></div></section>
    <section className=\"panel network-panel\">
      <div className=\"story-filter\">{storyIds.map(id => <button key={id} className={selectedStory === id ? 'active' : ''} onClick={() => setSelectedStory(id)}>{id === 'all' ? 'All paths' : data.stories.find(s => s.id === id)?.title}</button>)}</div>
      <svg className=\"network-svg\" viewBox=\"0 0 360 640\">
        <line x1=\"38\" y1=\"30\" x2=\"38\" y2=\"610\" className=\"time-axis\" />
        {[['1700', 50], ['1800', 145], ['1820', 300], ['1840', 445], ['1860', 590]].map(([t,y]) => <text key={t} x=\"7\" y={Number(y)} className=\"year-label\">{t}</text>)}
        {data.stories.map(s => <path key={s.id} d={storyPath(s)} className={`story-overlay ${selectedStory !== 'all' && selectedStory !== s.id ? 'dim' : ''}`} style={{ stroke: storyPalette[s.id] || '#888' }} />)}
        {Object.entries(positions).map(([id,p]) => {
"""
new_network_render = """    <section className=\"hero-card\"><h2>Network — {layout.minYear}–{layout.maxYear} · local Story graph</h2><p>Historical entities remain the graph. Story paths are overlays. Vertical position is chronological; horizontal lanes are derived from Story membership, with shared nodes literally shared between paths.</p><div className=\"entity-legend\"><span><i className=\"person-mark\" />Person</span><span><i className=\"concept-mark\" />Concept</span><span><i className=\"work-mark\" />Work</span></div></section>
    <section className=\"panel network-panel\">
      <div className=\"story-filter\">{storyIds.map(id => <button key={id} className={selectedStory === id ? 'active' : ''} onClick={() => setSelectedStory(id)}>{id !== 'all' && <i className=\"story-dot\" style={{ background: storyColor(id) }} />}{id === 'all' ? 'All paths' : data.stories.find(s => s.id === id)?.title}</button>)}</div>
      <svg className=\"network-svg\" viewBox=\"0 0 360 640\">
        <line x1=\"38\" y1=\"30\" x2=\"38\" y2=\"610\" className=\"time-axis\" />
        {layout.ticks.map(year => <text key={year} x=\"7\" y={yForYear(year)} className=\"year-label\">{year}</text>)}
        {data.stories.map(s => <path key={s.id} d={storyPath(s)} className={`story-overlay ${selectedStory !== 'all' && selectedStory !== s.id ? 'dim' : ''}`} style={{ stroke: storyColor(s.id) }} />)}
        {Object.entries(layout.positions).map(([id,p]) => {
"""
main = replace_once(main, old_network_render, new_network_render, "network render")

main = replace_once(
    main,
    """    {type === 'Work' && <rect x={x-10} y={y-10} width=\"20\" height=\"20\" rx=\"4\" className=\"node-work\" />}
    {isQuestion && <rect x={x-12} y={y-9} width=\"24\" height=\"18\" rx=\"9\" className=\"node-question\" />}
""",
    """    {type === 'Work' && <rect x={x-10} y={y-10} width=\"20\" height=\"20\" rx=\"4\" className=\"node-work\" />}
    {!isQuestion && !['Person', 'Concept', 'Work'].includes(type) && <circle cx={x} cy={y} r=\"9\" className=\"node-other\" />}
    {isQuestion && <rect x={x-12} y={y-9} width=\"24\" height=\"18\" rx=\"9\" className=\"node-question\" />}
""",
    "other entity node",
)

main = replace_once(
    main,
    "<i style={{ background: storyPalette[id] }} />",
    "<i style={{ background: storyColor(id) }} />",
    "intersection story color",
)
main = replace_once(
    main,
    "background: storyPalette[s.id] || '#999'",
    "background: storyColor(s.id)",
    "story rail color",
)

css += """
/* Data-driven Network additions */
.story-filter .story-dot{display:inline-block;width:7px;height:7px;border-radius:50%;margin-right:5px;vertical-align:1px}
.node-other{fill:#fff;stroke:#8a6f3f;stroke-width:2}
"""

main_path.write_text(main, encoding="utf-8", newline="\n")
css_path.write_text(css, encoding="utf-8", newline="\n")
print("Patched data-driven Network layout and deterministic Story colors.")
