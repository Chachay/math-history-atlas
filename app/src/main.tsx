import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';

type View = 'Atlas' | 'Network' | 'Story' | 'Person';
type Entity = { id: string; type: string; name: string; start_year?: number; end_year?: number | null; fields?: string[] };
type Question = { id: string; question: string; period?: { from?: number; to?: number | null }; fields?: string[] };
type Assertion = { id: string; subject: string; predicate: string; object: string; period?: { from?: number; to?: number | null }; status?: string; perspective?: string };
type StoryStep = { id: string; ref: string; role: string; narrative?: string; assertion_refs?: string[]; perspective?: string; temporal_anchor?: { from?: number; to?: number | null } };
type Story = { id: string; title: string; steps: StoryStep[]; links: { from: string; to: string; type: string }[] };
type Intersection = { entity: string; story_count: number; stories: string[] };
type AtlasField = { id: string; name: string; parents: string[] };
type PersonIndex = { person: string; name: string; assertions: string[]; stories: string[] };
type Dataset = {
  graph: { entities: Entity[]; questions: Question[]; assertions: Assertion[] };
  stories: Story[];
  intersections: Intersection[];
  atlas: { fields: AtlasField[] };
  people: PersonIndex[];
};
type RouteState = { view: View; storyId?: string; personId?: string; networkStory?: string };

const views: View[] = ['Atlas', 'Network', 'Story', 'Person'];
function storyColor(id: string) {
  let hash = 2166136261;
  for (let i = 0; i < id.length; i += 1) {
    hash ^= id.charCodeAt(i);
    hash = Math.imul(hash, 16777619);
  }
  const hue = Math.abs(hash) % 360;
  return `hsl(${hue} 58% 44%)`;
}

async function loadJson<T>(name: string): Promise<T> {
  const r = await fetch(`./data/${name}`);
  if (!r.ok) throw new Error(`${name}: ${r.status}`);
  return r.json() as Promise<T>;
}

function parseRoute(): RouteState {
  const raw = window.location.hash.replace(/^#\/?/, '');
  const [path, query = ''] = raw.split('?');
  const parts = path.split('/').filter(Boolean).map(decodeURIComponent);
  if (parts[0] === 'story' && parts[1]) return { view: 'Story', storyId: parts[1] };
  if (parts[0] === 'person' && parts[1]) return { view: 'Person', personId: parts[1] };
  if (parts[0] === 'network') {
    const story = new URLSearchParams(query).get('story') || 'all';
    return { view: 'Network', networkStory: story };
  }
  return { view: 'Atlas' };
}

function routeHash(route: RouteState) {
  if (route.view === 'Story') return `#/story/${encodeURIComponent(route.storyId || 'story-rigor')}`;
  if (route.view === 'Person') return `#/person/${encodeURIComponent(route.personId || 'person-euler')}`;
  if (route.view === 'Network') return route.networkStory && route.networkStory !== 'all'
    ? `#/network?story=${encodeURIComponent(route.networkStory)}`
    : '#/network';
  return '#/atlas';
}

function App() {
  const [route, setRoute] = useState<RouteState>(() => parseRoute());
  const [data, setData] = useState<Dataset | null>(null);
  const [error, setError] = useState('');
  const [sheet, setSheet] = useState<React.ReactNode | null>(null);

  useEffect(() => {
    if (!window.location.hash) window.history.replaceState(null, '', `${window.location.pathname}${window.location.search}#/atlas`);
    const onHashChange = () => { setRoute(parseRoute()); setSheet(null); window.scrollTo({ top: 0, behavior: 'smooth' }); };
    window.addEventListener('hashchange', onHashChange);
    return () => window.removeEventListener('hashchange', onHashChange);
  }, []);

  useEffect(() => {
    Promise.all([
      loadJson<Dataset['graph']>('graph.json'),
      loadJson<Story[]>('story-index.json'),
      loadJson<Intersection[]>('intersections.json'),
      loadJson<Dataset['atlas']>('atlas.json'),
      loadJson<PersonIndex[]>('person-index.json'),
    ]).then(([graph, stories, intersections, atlas, people]) => {
      setData({ graph, stories, intersections, atlas, people });
    }).catch(e => setError(String(e)));
  }, []);

  const selectedStory = route.view === 'Story' ? (route.storyId || 'story-rigor') : (route.networkStory || 'story-rigor');
  const selectedPerson = route.personId || 'person-euler';
  const navigate = (next: RouteState) => { window.location.hash = routeHash(next).slice(1); };
  const go = (v: View) => {
    if (v === 'Story') navigate({ view: 'Story', storyId: selectedStory === 'all' ? 'story-rigor' : selectedStory });
    else if (v === 'Person') navigate({ view: 'Person', personId: selectedPerson });
    else if (v === 'Network') navigate({ view: 'Network', networkStory: selectedStory });
    else navigate({ view: 'Atlas' });
  };
  const openStory = (id: string) => navigate({ view: 'Story', storyId: id });
  const openPerson = (id: string) => navigate({ view: 'Person', personId: id });
  const selectNetworkStory = (id: string) => navigate({ view: 'Network', networkStory: id });

  if (error) return <main className="shell"><section className="load-error">Could not load generated data: {error}</section></main>;
  if (!data) return <main className="shell"><section className="loading">Loading atlas…</section></main>;

  return <div className="shell">
    <header className="app-header">
      <div className="brand-row">
        <div><h1>Why Mathematics Changed</h1><p>Fields evolve; Stories cross the historical graph.</p></div>
        <span className="version-badge">V5 UI</span>
      </div>
      <nav className="top-tabs">{views.map(v => <button key={v} className={route.view === v ? 'active' : ''} onClick={() => go(v)}>{letter(v)} · {v}</button>)}</nav>
    </header>

    <main className="content">
      {route.view === 'Atlas' && <AtlasView data={data} onEnterNetwork={() => go('Network')} />}
      {route.view === 'Network' && <NetworkView data={data} selectedStory={route.networkStory || 'all'} setSelectedStory={selectNetworkStory} onOpenStory={openStory} onOpenPerson={openPerson} onSheet={setSheet} />}
      {route.view === 'Story' && <StoryView data={data} storyId={selectedStory} onNetwork={() => navigate({ view: 'Network', networkStory: selectedStory })} onOpenPerson={openPerson} onSheet={setSheet} />}
      {route.view === 'Person' && <PersonView data={data} personId={selectedPerson} onStory={openStory} />}
    </main>

    <nav className="bottom-nav">{views.map(v => <button key={v} className={route.view === v ? 'active' : ''} onClick={() => go(v)}><b>{icon(v)}</b>{v}</button>)}</nav>

    {sheet && <div className="sheet-backdrop" onClick={() => setSheet(null)}><div className="sheet" onClick={e => e.stopPropagation()}><div className="sheet-handle" />{sheet}</div></div>}
  </div>;
}

function AtlasView({ data, onEnterNetwork }: { data: Dataset; onEnterNetwork: () => void }) {
  const field = (id: string) => data.atlas.fields.find(f => f.id === id)?.name || id;
  return <>
    <section className="hero-card"><h2>Atlas — How mathematical fields branch and recombine</h2><p>This view is about the evolution of fields, not the editorial Questions. Tap a field to enter a local historical Network.</p></section>
    <section className="panel atlas-panel">
      <svg className="atlas-svg" viewBox="0 0 360 650" role="img" aria-label="Field evolution atlas">
        <line x1="36" y1="30" x2="36" y2="620" className="time-axis" />
        {[['1600', 38], ['1750', 170], ['1850', 310], ['1950', 455], ['2020', 610]].map(([t,y]) => <text key={t} x="7" y={Number(y)} className="year-label">{t}</text>)}
        <path d="M80 55 C80 120 95 150 110 190 C120 230 120 270 120 330 C125 390 132 455 140 590" className="field-path analysis" />
        <path d="M80 55 C95 120 155 135 168 190 C175 245 182 295 190 350 C205 410 222 490 230 590" className="field-path algebra" />
        <path d="M80 55 C65 125 55 165 62 230 C68 305 80 390 86 590" className="field-path geometry" />
        <path d="M168 190 C208 230 225 265 242 315 C257 375 270 455 278 590" className="field-path topology" />
        <path d="M110 190 C145 240 158 285 160 335 C165 380 165 440 165 590" className="field-path probability" />
        <path d="M190 350 C220 390 236 430 242 590" className="field-path logic" />
        <path d="M140 470 C195 490 220 520 230 590" className="field-path recombine" />
        <AtlasNode x={80} y={55} label="Calculus / Geometry / Algebra" sub="17th-century starting cluster" color="#34404b" onClick={onEnterNetwork} />
        <AtlasNode x={110} y={190} label={field('analysis')} sub="limits · series · functions" color="#2b78d0" onClick={onEnterNetwork} />
        <AtlasNode x={168} y={190} label={field('algebra')} sub="equations → structures" color="#7759c8" onClick={onEnterNetwork} />
        <AtlasNode x={62} y={230} label="Geometry" color="#b8687a" onClick={onEnterNetwork} />
        <AtlasNode x={160} y={335} label="Probability" color="#e49a2c" onClick={onEnterNetwork} />
        <AtlasNode x={190} y={350} label="Logic / Foundations" color="#7f8a99" onClick={onEnterNetwork} />
        <AtlasNode x={242} y={315} label={field('topology')} color="#2d9163" onClick={onEnterNetwork} />
        <AtlasNode x={140} y={470} label="Functional analysis" color="#2b78d0" onClick={onEnterNetwork} />
        <AtlasNode x={278} y={470} label="Harmonic analysis" color="#2d9163" onClick={onEnterNetwork} />
        <AtlasNode x={230} y={590} label={field('arithmetic-geometry')} sub="recombination example" color="#7056b8" onClick={onEnterNetwork} />
      </svg>
    </section>
  </>;
}

function AtlasNode({ x, y, label, sub, color, onClick }: { x: number; y: number; label: string; sub?: string; color: string; onClick: () => void }) {
  return <g className="atlas-node" onClick={onClick}><circle cx={x} cy={y} r="8" style={{ stroke: color }} /><text x={x + 12} y={y - 3} className="atlas-node-label">{label}</text>{sub && <text x={x + 12} y={y + 10} className="atlas-node-sub">{sub}</text>}</g>;
}

type NetworkPoint = { x: number; y: number; year: number; ref: string; storyIds: string[] };
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

function NetworkView({ data, selectedStory, setSelectedStory, onOpenStory, onOpenPerson, onSheet }: {
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

function NetworkNode({ item, x, y, intersection, onClick }: { id: string; item: Entity | Question; x: number; y: number; intersection?: Intersection; onClick: () => void }) {
  const isQuestion = !('type' in item);
  const type = isQuestion ? 'Question' : item.type;
  const label = isQuestion ? item.question : item.name;
  return <g className="network-node" onClick={onClick}>
    {type === 'Person' && <circle cx={x} cy={y} r="9" className="node-person" />}
    {type === 'Concept' && <polygon points={`${x},${y-11} ${x+11},${y} ${x},${y+11} ${x-11},${y}`} className="node-concept" />}
    {type === 'Work' && <rect x={x-10} y={y-10} width="20" height="20" rx="4" className="node-work" />}
    {!isQuestion && !['Person', 'Concept', 'Work'].includes(type) && <circle cx={x} cy={y} r="9" className="node-other" />}
    {isQuestion && <rect x={x-12} y={y-9} width="24" height="18" rx="9" className="node-question" />}
    {intersection && <><circle cx={x} cy={y} r="20" className="intersection-ring" /><circle cx={x+18} cy={y-18} r="10" className="intersection-count-bg" /><text x={x+15} y={y-15} className="intersection-count">{intersection.story_count}</text></>}
    <text x={x+15} y={y-3} className="node-label">{short(label, 24)}</text>
    <text x={x+15} y={y+10} className="node-sub">{intersection ? `${intersection.story_count} Stories intersect` : type}</text>
  </g>;
}

function IntersectionSheet({ intersection, data, onOpen }: { intersection: Intersection; data: Dataset; onOpen: (x: string) => void }) {
  const entity = data.graph.entities.find(e => e.id === intersection.entity);
  return <><span className="sheet-badge">INTERSECTION · {intersection.story_count} STORIES</span><h3>{entity?.name || intersection.entity}</h3><p>The same historical entity is part of several curated readings:</p><div className="sheet-story-list">{intersection.stories.map(id => <button key={id} onClick={() => onOpen(id)}><i style={{ background: storyColor(id) }} />{data.stories.find(s => s.id === id)?.title || id}</button>)}</div></>;
}

function StoryView({ data, storyId, onNetwork, onOpenPerson, onSheet }: { data: Dataset; storyId: string; onNetwork: () => void; onOpenPerson: (id: string) => void; onSheet: (n: React.ReactNode) => void }) {
  const story = data.stories.find(s => s.id === storyId) || data.stories[0];
  const lookup = buildLookup(data);
  const intersections = new Map(data.intersections.map(i => [i.entity, i]));
  return <>
    <section className="hero-card"><span className="eyebrow">CURRENT STORY</span><h2>{story.title}</h2><p>Read one editorial path vertically while parallel paths remain perceptible. Crossings return you to the Network.</p></section>
    <div className="story-layout"><div>
      {[...story.steps].sort((a, b) => (a.temporal_anchor?.from ?? 9999) - (b.temporal_anchor?.from ?? 9999) || story.steps.indexOf(a) - story.steps.indexOf(b)).map((step, idx) => {
        const item = lookup[step.ref]; const inter = intersections.get(step.ref); const label = item ? ('type' in item ? item.name : item.question) : step.ref;
        const isProblem = /problem|gap/i.test(step.role);
        return <article key={step.id} className={`story-card panel ${isProblem ? 'problem' : ''} ${inter ? 'crossing' : ''}`}>
          <div className="story-index">{idx + 1}</div>
          <div className="story-meta"><span>{step.role.toUpperCase()}</span><span>{yearFor(item)}</span></div>
          <h3>{label}</h3>
          {step.narrative && <p>{step.narrative}</p>}
          <div className="story-actions">
            {inter && <button onClick={onNetwork}>See the crossing in Network</button>}
            {item && 'type' in item && item.type === 'Person' && <button onClick={() => onOpenPerson(item.id)}>Open person</button>}
            {inter && <button onClick={() => onSheet(<IntersectionSheet intersection={inter} data={data} onOpen={() => {}} />)}>Other Stories</button>}
          </div>
        </article>;
      })}
    </div><aside className="parallel-rail"><div className="rail-line">{data.stories.slice(0,3).map((s,i) => <span key={s.id} style={{ top: `${18+i*28}%`, background: storyColor(s.id) }} title={s.title} />)}</div></aside></div>
  </>;
}

function PersonView({ data, personId, onStory }: { data: Dataset; personId: string; onStory: (id: string) => void }) {
  const person = data.graph.entities.find(e => e.id === personId && e.type === 'Person') || data.graph.entities.find(e => e.type === 'Person')!;
  const assertions = data.graph.assertions.filter(a => a.subject === person.id || a.object === person.id);
  const relevantStories = data.stories.filter(s => s.steps.some(st => st.ref === person.id));
  const initials = person.name.split(' ').map(x => x[0]).slice(0,2).join('');
  return <section className="panel person-card">
    <div className="person-head"><div className="avatar">{initials}</div><div><h2>{person.name}</h2><p>{person.start_year}–{person.end_year || ''} · {(person.fields || []).join(' · ')}</p></div></div>
    <div className="metrics"><div><b>{relevantStories.length}</b><span>Story appearances</span></div><div><b>{assertions.length}</b><span>accepted links</span></div><div><b>{person.fields?.length || 0}</b><span>fields</span></div></div>
    <h3 className="section-title">Contribution history</h3>
    <div className="contribution-list">{assertions.length ? assertions.map(a => <div key={a.id}><span>{a.perspective || 'historical'}</span><b>{humanize(a.predicate)}</b><p>{a.subject === person.id ? a.object : a.subject}</p></div>) : <div><span>sample</span><b>Canonical assertions not yet populated for this person</b><p>As research packets are accepted, this view will be generated automatically.</p></div>}</div>
    <h3 className="section-title">Stories</h3>
    <div className="story-chips">{relevantStories.length ? relevantStories.map(s => <button key={s.id} onClick={() => onStory(s.id)}>{s.title}</button>) : <span className="muted">No Story currently references this person directly.</span>}</div>
  </section>;
}

function buildLookup(data: Dataset): Record<string, Entity | Question> {
  return Object.fromEntries([...data.graph.entities, ...data.graph.questions].map(x => [x.id, x]));
}
function short(s: string, n: number) { return s.length > n ? s.slice(0, n - 1) + '…' : s; }
function yearFor(item?: Entity | Question) { if (!item) return ''; return 'type' in item ? String(item.start_year || '') : String(item.period?.from || ''); }
function humanize(s: string) { return s.replaceAll('_', ' '); }
function letter(v: View) { return ({ Atlas:'A', Network:'B', Story:'C', Person:'D' } as const)[v]; }
function icon(v: View) { return ({ Atlas:'⌘', Network:'⋈', Story:'↧', Person:'●' } as const)[v]; }

createRoot(document.getElementById('root')!).render(<App />);