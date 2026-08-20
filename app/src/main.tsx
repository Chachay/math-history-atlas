import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';

type View = 'Atlas' | 'Network' | 'Story' | 'Person';
type Entity = { id: string; type: string; name: string; start_year?: number; end_year?: number | null; fields?: string[] };
type Question = { id: string; question: string; period?: { from?: number; to?: number | null }; fields?: string[] };
type Assertion = { id: string; subject: string; predicate: string; object: string; status?: string; perspective?: string };
type StoryStep = { id: string; ref: string; role: string };
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

const views: View[] = ['Atlas', 'Network', 'Story', 'Person'];
const storyPalette: Record<string, string> = {
  'story-rigor': '#2b78d0',
  'story-function': '#7759c8',
  'story-frequency': '#2d9163',
};

async function loadJson<T>(name: string): Promise<T> {
  const r = await fetch(`./data/${name}`);
  if (!r.ok) throw new Error(`${name}: ${r.status}`);
  return r.json() as Promise<T>;
}

function App() {
  const [view, setView] = useState<View>('Atlas');
  const [data, setData] = useState<Dataset | null>(null);
  const [error, setError] = useState('');
  const [selectedStory, setSelectedStory] = useState('story-rigor');
  const [selectedPerson, setSelectedPerson] = useState('person-euler');
  const [sheet, setSheet] = useState<React.ReactNode | null>(null);

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

  const go = (v: View) => { setView(v); window.scrollTo({ top: 0, behavior: 'smooth' }); };
  const openPerson = (id: string) => { setSelectedPerson(id); go('Person'); };

  if (error) return <main className="shell"><section className="load-error">Could not load generated data: {error}</section></main>;
  if (!data) return <main className="shell"><section className="loading">Loading atlas…</section></main>;

  return <div className="shell">
    <header className="app-header">
      <div className="brand-row">
        <div><h1>Why Mathematics Changed</h1><p>Fields evolve; Stories cross the historical graph.</p></div>
        <span className="version-badge">V5 UI</span>
      </div>
      <nav className="top-tabs">{views.map(v => <button key={v} className={view === v ? 'active' : ''} onClick={() => go(v)}>{letter(v)} · {v}</button>)}</nav>
    </header>

    <main className="content">
      {view === 'Atlas' && <AtlasView data={data} onEnterNetwork={() => go('Network')} />}
      {view === 'Network' && <NetworkView data={data} selectedStory={selectedStory} setSelectedStory={setSelectedStory} onOpenStory={id => { setSelectedStory(id); go('Story'); }} onOpenPerson={openPerson} onSheet={setSheet} />}
      {view === 'Story' && <StoryView data={data} storyId={selectedStory} onNetwork={() => go('Network')} onOpenPerson={openPerson} onSheet={setSheet} />}
      {view === 'Person' && <PersonView data={data} personId={selectedPerson} onStory={id => { setSelectedStory(id); go('Story'); }} />}
    </main>

    <nav className="bottom-nav">{views.map(v => <button key={v} className={view === v ? 'active' : ''} onClick={() => go(v)}><b>{icon(v)}</b>{v}</button>)}</nav>

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

const positions: Record<string, { x: number; y: number }> = {
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

function NetworkView({ data, selectedStory, setSelectedStory, onOpenStory, onOpenPerson, onSheet }: {
  data: Dataset; selectedStory: string; setSelectedStory: (x: string) => void; onOpenStory: (x: string) => void; onOpenPerson: (x: string) => void; onSheet: (n: React.ReactNode) => void;
}) {
  const lookup = useMemo(() => buildLookup(data), [data]);
  const intersections = new Map(data.intersections.map(i => [i.entity, i]));
  const storyIds = ['all', ...data.stories.map(s => s.id)];

  const storyPath = (story: Story) => {
    const pts = story.steps.map(s => positions[s.ref]).filter(Boolean);
    if (pts.length < 2) return '';
    return pts.map((p, i) => `${i ? 'L' : 'M'}${p.x} ${p.y}`).join(' ');
  };

  return <>
    <section className="hero-card"><h2>Network — 1700–1860 · Analysis</h2><p>Historical entities remain the graph. Story paths are overlays. When several Stories pass through the same node, the intersection becomes visible without creating a separate “Junction” screen.</p><div className="entity-legend"><span><i className="person-mark" />Person</span><span><i className="concept-mark" />Concept</span><span><i className="work-mark" />Work</span></div></section>
    <section className="panel network-panel">
      <div className="story-filter">{storyIds.map(id => <button key={id} className={selectedStory === id ? 'active' : ''} onClick={() => setSelectedStory(id)}>{id === 'all' ? 'All paths' : data.stories.find(s => s.id === id)?.title}</button>)}</div>
      <svg className="network-svg" viewBox="0 0 360 640">
        <line x1="38" y1="30" x2="38" y2="610" className="time-axis" />
        {[['1700', 50], ['1800', 145], ['1820', 300], ['1840', 445], ['1860', 590]].map(([t,y]) => <text key={t} x="7" y={Number(y)} className="year-label">{t}</text>)}
        {data.stories.map(s => <path key={s.id} d={storyPath(s)} className={`story-overlay ${selectedStory !== 'all' && selectedStory !== s.id ? 'dim' : ''}`} style={{ stroke: storyPalette[s.id] || '#888' }} />)}
        {Object.entries(positions).map(([id,p]) => {
          const item = lookup[id]; if (!item) return null;
          const inter = intersections.get(id);
          return <NetworkNode key={id} id={id} item={item} x={p.x} y={p.y} intersection={inter} onClick={() => {
            if (inter) onSheet(<IntersectionSheet intersection={inter} data={data} onOpen={onOpenStory} />);
            else if ('type' in item && item.type === 'Person') onOpenPerson(id);
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
    {isQuestion && <rect x={x-12} y={y-9} width="24" height="18" rx="9" className="node-question" />}
    {intersection && <><circle cx={x} cy={y} r="20" className="intersection-ring" /><circle cx={x+18} cy={y-18} r="10" className="intersection-count-bg" /><text x={x+15} y={y-15} className="intersection-count">{intersection.story_count}</text></>}
    <text x={x+15} y={y-3} className="node-label">{short(label, 24)}</text>
    <text x={x+15} y={y+10} className="node-sub">{intersection ? `${intersection.story_count} Stories intersect` : type}</text>
  </g>;
}

function IntersectionSheet({ intersection, data, onOpen }: { intersection: Intersection; data: Dataset; onOpen: (x: string) => void }) {
  const entity = data.graph.entities.find(e => e.id === intersection.entity);
  return <><span className="sheet-badge">INTERSECTION · {intersection.story_count} STORIES</span><h3>{entity?.name || intersection.entity}</h3><p>The same historical entity is part of several curated readings:</p><div className="sheet-story-list">{intersection.stories.map(id => <button key={id} onClick={() => onOpen(id)}><i style={{ background: storyPalette[id] }} />{data.stories.find(s => s.id === id)?.title || id}</button>)}</div></>;
}

function StoryView({ data, storyId, onNetwork, onOpenPerson, onSheet }: { data: Dataset; storyId: string; onNetwork: () => void; onOpenPerson: (id: string) => void; onSheet: (n: React.ReactNode) => void }) {
  const story = data.stories.find(s => s.id === storyId) || data.stories[0];
  const lookup = buildLookup(data);
  const intersections = new Map(data.intersections.map(i => [i.entity, i]));
  return <>
    <section className="hero-card"><span className="eyebrow">CURRENT STORY</span><h2>{story.title}</h2><p>Read one editorial path vertically while parallel paths remain perceptible. Crossings return you to the Network.</p></section>
    <div className="story-layout"><div>
      {story.steps.map((step, idx) => {
        const item = lookup[step.ref]; const inter = intersections.get(step.ref); const label = item ? ('type' in item ? item.name : item.question) : step.ref;
        const isProblem = /problem|gap/i.test(step.role);
        return <article key={step.id} className={`story-card panel ${isProblem ? 'problem' : ''} ${inter ? 'crossing' : ''}`}>
          <div className="story-meta"><span>{step.role.toUpperCase()}</span><span>{yearFor(item)}</span></div>
          <h3>{label}</h3>
          <p>{storyText(story.id, step.ref, step.role)}</p>
          <div className="story-actions">
            {inter && <button onClick={onNetwork}>See the crossing in Network</button>}
            {item && 'type' in item && item.type === 'Person' && <button onClick={() => onOpenPerson(item.id)}>Open person</button>}
            {inter && <button onClick={() => onSheet(<IntersectionSheet intersection={inter} data={data} onOpen={() => {}} />)}>Other Stories</button>}
          </div>
        </article>;
      })}
    </div><aside className="parallel-rail"><div className="rail-line">{data.stories.slice(0,3).map((s,i) => <span key={s.id} style={{ top: `${18+i*28}%`, background: storyPalette[s.id] || '#999' }} title={s.title} />)}</div></aside></div>
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
function storyText(storyId: string, ref: string, role: string) {
  const keyed: Record<string, string> = {
    'concept-infinite-series': 'Infinite processes were powerful, but finite-operation intuition could not simply be assumed to survive an infinite limit.',
    'concept-fourier-series': 'A concrete mathematical object became a shared node for questions about convergence, the meaning of function, and frequency decomposition.',
    'concept-convergence': 'The difficulty shifts from writing a series to specifying what it means for a sequence or series to approach a limit.',
    'concept-function': 'The class of objects admitted as “functions” becomes part of the mathematical problem rather than a settled background assumption.',
    'concept-continuity': 'Continuity must be separated from nearby notions and stated in a form that survives increasingly pathological examples.',
    'work-fourier-theorie': 'A landmark work provides a historical anchor; editorial interpretations are kept separate from claims about the author’s own motivations.',
  };
  return keyed[ref] || '';
}

createRoot(document.getElementById('root')!).render(<App />);
