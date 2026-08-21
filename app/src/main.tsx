import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';

type View = 'Atlas' | 'Network' | 'Story' | 'Person';
type Entity = { id: string; type: string; name: string; start_year?: number; end_year?: number | null; fields?: string[] };
type Question = { id: string; question: string; period?: { from?: number; to?: number | null }; fields?: string[] };
type Assertion = { id: string; subject: string; predicate: string; object: string; period?: { from?: number; to?: number | null }; status?: string; perspective?: string };
type StoryStep = { id: string; ref: string; role: string; narrative?: string; assertion_refs?: string[]; perspective?: string; temporal_anchor?: { from?: number; to?: number | null } };
type Story = { id: string; title: string; fields?: string[]; steps: StoryStep[]; links: { from: string; to: string; type: string }[] };
type StoryTransition = { id: string; from_story: string; from_step: string; to_story: string; to_step: string; type: string; perspective: string; assertion_refs: string[]; rationale?: string };
type Intersection = { entity: string; story_count: number; stories: string[] };
type AtlasField = { id: string; name: string; parents: string[] };
type PersonIndex = { person: string; name: string; assertions: string[]; stories: string[] };
type Dataset = {
  graph: { entities: Entity[]; questions: Question[]; assertions: Assertion[] };
  stories: Story[];
  transitions: StoryTransition[];
  intersections: Intersection[];
  atlas: { fields: AtlasField[] };
  people: PersonIndex[];
};
type RouteState = { view: View; storyId?: string; personId?: string; networkStory?: string; networkField?: string };
type NetworkPoint = { x: number; y: number; year: number; ref: string; storyIds: string[] };
type NetworkLayout = { positions: Record<string, NetworkPoint>; stepKeys: Record<string, string>; yearRows: { year: number; y: number }[]; minYear: number; maxYear: number; height: number };

const views: View[] = ['Atlas', 'Network', 'Story', 'Person'];

function storyColor(id: string) {
  let hash = 2166136261;
  for (let i = 0; i < id.length; i += 1) { hash ^= id.charCodeAt(i); hash = Math.imul(hash, 16777619); }
  return `hsl(${Math.abs(hash) % 360} 58% 44%)`;
}

async function loadJson<T>(name: string) {
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
    const params = new URLSearchParams(query);
    return { view: 'Network', networkStory: params.get('story') || 'all', networkField: params.get('field') || undefined };
  }
  return { view: 'Atlas' };
}

function routeHash(route: RouteState) {
  if (route.view === 'Story') return `#/story/${encodeURIComponent(route.storyId || 'story-rigor')}`;
  if (route.view === 'Person') return `#/person/${encodeURIComponent(route.personId || 'person-euler')}`;
  if (route.view === 'Network') {
    const params = new URLSearchParams();
    if (route.networkStory && route.networkStory !== 'all') params.set('story', route.networkStory);
    if (route.networkField) params.set('field', route.networkField);
    const query = params.toString();
    return query ? `#/network?${query}` : '#/network';
  }
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
      loadJson<Dataset['graph']>('graph.json'), loadJson<Story[]>('story-index.json'), loadJson<StoryTransition[]>('story-transitions.json'),
      loadJson<Intersection[]>('intersections.json'), loadJson<Dataset['atlas']>('atlas.json'), loadJson<PersonIndex[]>('person-index.json'),
    ]).then(([graph, stories, transitions, intersections, atlas, people]) => setData({ graph, stories, transitions, intersections, atlas, people }))
      .catch(e => setError(String(e)));
  }, []);

  const selectedStory = route.view === 'Story' ? (route.storyId || 'story-rigor') : (route.networkStory || 'all');
  const selectedPerson = route.personId || data?.graph.entities.find(e => e.type === 'Person')?.id || 'person-euler';
  const navigate = (next: RouteState) => { window.location.hash = routeHash(next).slice(1); };
  const go = (v: View) => {
    if (v === 'Story') navigate({ view: 'Story', storyId: selectedStory === 'all' ? (data?.stories[0]?.id || 'story-rigor') : selectedStory });
    else if (v === 'Person') navigate({ view: 'Person', personId: selectedPerson });
    else if (v === 'Network') navigate({ view: 'Network', networkStory: selectedStory, networkField: route.networkField });
    else navigate({ view: 'Atlas' });
  };

  if (error) return <main className="shell"><section className="load-error">Could not load generated data: {error}</section></main>;
  if (!data) return <main className="shell"><section className="loading">Loading atlas…</section></main>;

  return <div className="shell">
    <header className="app-header"><div className="brand-row"><div><h1>Why Mathematics Changed</h1><p>Fields evolve; Stories cross the historical graph.</p></div><span className="version-badge">V5 UI</span></div>
      <nav className="top-tabs">{views.map(v => <button key={v} className={route.view === v ? 'active' : ''} onClick={() => go(v)}>{letter(v)} · {v}</button>)}</nav></header>
    <main className="content">
      {route.view === 'Atlas' && <AtlasView data={data} onEnterNetwork={fieldId => navigate({ view: 'Network', networkStory: 'all', networkField: fieldId })} />}
      {route.view === 'Network' && <NetworkView data={data} selectedStory={route.networkStory || 'all'} selectedField={route.networkField} setSelectedStory={id => navigate({ view: 'Network', networkStory: id, networkField: route.networkField })} setSelectedField={fieldId => navigate({ view: 'Network', networkStory: 'all', networkField: fieldId })} onOpenStory={id => navigate({ view: 'Story', storyId: id })} onOpenPerson={id => navigate({ view: 'Person', personId: id })} onSheet={setSheet} />}
      {route.view === 'Story' && <StoryView data={data} storyId={selectedStory} onNetwork={() => navigate({ view: 'Network', networkStory: selectedStory })} onOpenPerson={id => navigate({ view: 'Person', personId: id })} onSheet={setSheet} />}
      {route.view === 'Person' && <PersonView data={data} personId={selectedPerson} onStory={id => navigate({ view: 'Story', storyId: id })} />}
    </main>
    <nav className="bottom-nav">{views.map(v => <button key={v} className={route.view === v ? 'active' : ''} onClick={() => go(v)}><b>{icon(v)}</b>{v}</button>)}</nav>
    {sheet && <div className="sheet-backdrop" onClick={() => setSheet(null)}><div className="sheet" onClick={e => e.stopPropagation()}><div className="sheet-handle" />{sheet}</div></div>}
  </div>;
}

function AtlasView({ data, onEnterNetwork }: { data: Dataset; onEnterNetwork: (fieldId?: string) => void }) {
  const field = (id: string) => data.atlas.fields.find(f => f.id === id)?.name || id;
  const rootFields = data.atlas.fields.filter(f => f.parents.includes('mathematics'));
  const storyCount = (fieldId: string) => data.stories.filter(s => s.fields?.includes(fieldId)).length;
  return <><section className="hero-card"><h2>Atlas — How mathematical fields branch and recombine</h2><p>This view is about field evolution. Field branches below are derived from canonical field data; choose one to frame its reviewed Network cluster.</p></section>
    <section className="panel atlas-panel">
      <div className="story-filter"><button onClick={() => onEnterNetwork(undefined)}>All researched paths</button>{rootFields.map(f => <button key={f.id} onClick={() => onEnterNetwork(f.id)}>{f.name} · {storyCount(f.id)} Stories</button>)}</div>
      <svg className="atlas-svg" viewBox="0 0 360 650"><line x1="36" y1="30" x2="36" y2="620" className="time-axis" />
      {[['1600',38],['1750',170],['1850',310],['1950',455],['2020',610]].map(([t,y]) => <text key={t} x="7" y={Number(y)} className="year-label">{t}</text>)}
      <path d="M80 55 C80 120 95 150 110 190 C120 230 120 270 120 330 C125 390 132 455 140 590" className="field-path analysis" />
      <path d="M80 55 C95 120 155 135 168 190 C175 245 182 295 190 350 C205 410 222 490 230 590" className="field-path algebra" />
      <path d="M80 55 C65 125 55 165 62 230 C68 305 80 390 86 590" className="field-path geometry" />
      <path d="M168 190 C208 230 225 265 242 315 C257 375 270 455 278 590" className="field-path topology" />
      <AtlasNode x={80} y={55} label="Calculus / Geometry / Algebra" sub="17th-century starting cluster" onClick={() => onEnterNetwork(undefined)} />
      <AtlasNode x={110} y={190} label={field('analysis')} sub="limits · series · functions" onClick={() => onEnterNetwork('analysis')} />
      <AtlasNode x={168} y={190} label={field('algebra')} sub="equations → structures" onClick={() => onEnterNetwork('algebra')} />
      <AtlasNode x={242} y={315} label={field('topology')} onClick={() => onEnterNetwork('topology')} />
      <AtlasNode x={278} y={470} label="Harmonic analysis" onClick={() => onEnterNetwork('analysis')} />
    </svg></section></>;
}

function AtlasNode({ x, y, label, sub, onClick }: { x: number; y: number; label: string; sub?: string; onClick: () => void }) {
  return <g className="atlas-node" onClick={onClick}><circle cx={x} cy={y} r="8" /><text x={x + 12} y={y - 3} className="atlas-node-label">{label}</text>{sub && <text x={x + 12} y={y + 10} className="atlas-node-sub">{sub}</text>}</g>;
}

function stableFraction(id: string) { let hash = 0; for (let i = 0; i < id.length; i += 1) hash = (Math.imul(hash, 31) + id.charCodeAt(i)) | 0; return (Math.abs(hash) % 1000) / 1000; }
function stepYear(step: StoryStep, item?: Entity | Question) { if (typeof step.temporal_anchor?.from === 'number') return step.temporal_anchor.from; if (!item) return 1800; return 'type' in item ? (item.start_year || 1800) : (item.period?.from || 1800); }

function buildNetworkLayout(stories: Story[], lookup: Record<string, Entity | Question>): NetworkLayout {
  const storyIndex = new Map(stories.map((story, index) => [story.id, index]));
  const laneMin = 76, laneMax = 285, laneStep = stories.length > 1 ? (laneMax - laneMin) / (stories.length - 1) : 0;
  const groups = new Map<string, { ref: string; year: number; storyIds: string[] }>();
  const stepKeys: Record<string, string> = {};
  stories.forEach(story => story.steps.forEach(step => {
    const item = lookup[step.ref]; if (!item) return;
    const year = stepYear(step, item), key = `${step.ref}@${year}`;
    const group = groups.get(key) || { ref: step.ref, year, storyIds: [] };
    if (!group.storyIds.includes(story.id)) group.storyIds.push(story.id);
    groups.set(key, group); stepKeys[`${story.id}:${step.id}`] = key;
  }));
  const byYear = new Map<number, string[]>();
  groups.forEach((g,key) => { const xs = byYear.get(g.year) || []; xs.push(key); byYear.set(g.year, xs); });
  const years = [...byYear.keys()].sort((a,b) => a-b), positions: Record<string, NetworkPoint> = {}, yearRows: {year:number;y:number}[] = [];
  let cursor = 52;
  years.forEach(year => {
    const keys = (byYear.get(year) || []).sort(); const firstY = cursor;
    keys.forEach((key,index) => { const g = groups.get(key)!; const lanes = g.storyIds.map(id => storyIndex.get(id) || 0); let x = laneMin + (lanes.reduce((a,b)=>a+b,0)/Math.max(1,lanes.length))*laneStep; if (g.storyIds.length===1) x += (stableFraction(key)-0.5)*22; positions[key] = { x: Math.max(62,Math.min(292,x)), y: cursor + index*42, year, ref:g.ref, storyIds:g.storyIds }; });
    yearRows.push({year,y:firstY}); cursor += Math.max(1,keys.length)*42 + 34;
  });
  return { positions, stepKeys, yearRows, minYear: years[0] || 1750, maxYear: years[years.length-1] || 1860, height: Math.max(640,cursor+20) };
}

function NetworkView({ data, selectedStory, selectedField, setSelectedStory, setSelectedField, onOpenStory, onOpenPerson, onSheet }: { data: Dataset; selectedStory: string; selectedField?: string; setSelectedStory:(x:string)=>void; setSelectedField:(x?:string)=>void; onOpenStory:(x:string)=>void; onOpenPerson:(x:string)=>void; onSheet:(n:React.ReactNode)=>void }) {
  const lookup = useMemo(() => buildLookup(data), [data]);
  const fieldStories = useMemo(() => selectedField ? data.stories.filter(s => s.fields?.includes(selectedField)) : data.stories, [data, selectedField]);
  const layout = useMemo(() => buildNetworkLayout(fieldStories, lookup), [fieldStories, lookup]);
  const intersections = new Map(data.intersections.map(i => [i.entity, i]));
  const storyIds = ['all', ...fieldStories.map(s=>s.id)];
  const storyMap = new Map(data.stories.map(s=>[s.id,s]));
  const point = (storyId:string, stepId:string) => { const key = layout.stepKeys[`${storyId}:${stepId}`]; return key ? layout.positions[key] : undefined; };
  const curve = (a?:NetworkPoint,b?:NetworkPoint) => { if (!a || !b) return ''; const mid=(a.y+b.y)/2; return `M${a.x} ${a.y} C${a.x} ${mid} ${b.x} ${mid} ${b.x} ${b.y}`; };
  const selectedStories = selectedStory === 'all' ? fieldStories : fieldStories.filter(s=>s.id===selectedStory);
  const people = peopleForStories(data, selectedStories);
  const fieldName = selectedField ? data.atlas.fields.find(f=>f.id===selectedField)?.name || selectedField : 'All fields';
  const rootFields = data.atlas.fields.filter(f=>f.parents.includes('mathematics'));
  const visibleIds = new Set(fieldStories.map(s=>s.id));

  return <><section className="hero-card"><h2>Network — {layout.minYear}–{layout.maxYear} · {fieldName}</h2><p>Solid colored paths are links inside one Story. Dashed neutral connectors are separately reviewed handoffs between Stories; field framing is derived from Story field metadata.</p></section>
    <section className="panel network-panel">
      <div className="story-filter"><button className={!selectedField?'active':''} onClick={()=>setSelectedField(undefined)}>All fields</button>{rootFields.map(f=><button key={f.id} className={selectedField===f.id?'active':''} onClick={()=>setSelectedField(f.id)}>{f.name}</button>)}</div>
      <div className="story-filter">{storyIds.map(id => <button key={id} className={selectedStory===id?'active':''} onClick={()=>setSelectedStory(id)}>{id!=='all' && <i className="story-dot" style={{background:storyColor(id)}} />}{id==='all'?'All paths':storyMap.get(id)?.title}</button>)}</div>
      <div className="story-filter">{people.map(p => <button key={p.id} onClick={()=>onOpenPerson(p.id)}>● {p.name}</button>)}</div>
      <svg className="network-svg" viewBox={`0 0 360 ${layout.height}`}>
        <line x1="38" y1="30" x2="38" y2={layout.height-20} className="time-axis" />
        {layout.yearRows.map(r => <g key={r.year}><text x="7" y={r.y} className="year-label">{r.year}</text><line x1="34" y1={r.y-4} x2="42" y2={r.y-4} className="year-tick" /></g>)}
        {fieldStories.flatMap(story => story.links.map(link => <path key={`${story.id}:${link.from}:${link.to}`} d={curve(point(story.id,link.from),point(story.id,link.to))} className={`story-overlay ${selectedStory!=='all' && selectedStory!==story.id?'dim':''}`} style={{stroke:storyColor(story.id)}} />))}
        {data.transitions.filter(t=>visibleIds.has(t.from_story)&&visibleIds.has(t.to_story)).map(t => <path key={t.id} d={curve(point(t.from_story,t.from_step),point(t.to_story,t.to_step))} fill="none" stroke="currentColor" strokeWidth="2" strokeDasharray="6 5" opacity={selectedStory==='all' || selectedStory===t.from_story || selectedStory===t.to_story ? 0.7 : 0.12} />)}
        {Object.entries(layout.positions).map(([key,p]) => { const item=lookup[p.ref]; if(!item) return null; const canonical=intersections.get(p.ref); const temporal=p.storyIds.length>1&&canonical?{...canonical,story_count:p.storyIds.length,stories:p.storyIds}:undefined; return <NetworkNode key={key} item={item} x={p.x} y={p.y} intersection={temporal} onClick={()=>{ if(canonical) onSheet(<IntersectionSheet intersection={canonical} data={data} onOpen={onOpenStory}/>); else if('type' in item && item.type==='Person') onOpenPerson(item.id); }} />; })}
      </svg>
    </section></>;
}

function NetworkNode({ item, x, y, intersection, onClick }: { item:Entity|Question; x:number; y:number; intersection?:Intersection; onClick:()=>void }) {
  const isQuestion=!('type' in item), type=isQuestion?'Question':item.type, label=isQuestion?item.question:item.name;
  return <g className="network-node" onClick={onClick}>{type==='Person'&&<circle cx={x} cy={y} r="9" className="node-person"/>}{type==='Concept'&&<polygon points={`${x},${y-11} ${x+11},${y} ${x},${y+11} ${x-11},${y}`} className="node-concept"/>}{type==='Work'&&<rect x={x-10} y={y-10} width="20" height="20" rx="4" className="node-work"/>}{!isQuestion&&!['Person','Concept','Work'].includes(type)&&<circle cx={x} cy={y} r="9" className="node-other"/>}{isQuestion&&<rect x={x-12} y={y-9} width="24" height="18" rx="9" className="node-question"/>}{intersection&&<><circle cx={x} cy={y} r="20" className="intersection-ring"/><circle cx={x+18} cy={y-18} r="10" className="intersection-count-bg"/><text x={x+15} y={y-15} className="intersection-count">{intersection.story_count}</text></>}<text x={x+15} y={y-3} className="node-label">{short(label,24)}</text><text x={x+15} y={y+10} className="node-sub">{intersection?`${intersection.story_count} Stories intersect`:type}</text></g>;
}

function IntersectionSheet({ intersection, data, onOpen }: { intersection:Intersection; data:Dataset; onOpen:(x:string)=>void }) {
  const item = data.graph.entities.find(e=>e.id===intersection.entity) || data.graph.questions.find(q=>q.id===intersection.entity);
  const name = item ? ('type' in item ? item.name : item.question) : intersection.entity;
  return <><span className="sheet-badge">INTERSECTION · {intersection.story_count} STORIES</span><h3>{name}</h3><p>The same canonical item appears in several curated readings.</p><div className="sheet-story-list">{intersection.stories.map(id=><button key={id} onClick={()=>onOpen(id)}><i style={{background:storyColor(id)}}/>{data.stories.find(s=>s.id===id)?.title||id}</button>)}</div></>;
}

function StoryView({ data, storyId, onNetwork, onOpenPerson, onSheet }: { data:Dataset; storyId:string; onNetwork:()=>void; onOpenPerson:(id:string)=>void; onSheet:(n:React.ReactNode)=>void }) {
  const story=data.stories.find(s=>s.id===storyId)||data.stories[0], lookup=buildLookup(data), intersections=new Map(data.intersections.map(i=>[i.entity,i]));
  return <><section className="hero-card"><span className="eyebrow">CURRENT STORY</span><h2>{story.title}</h2><p>Read one editorial path vertically. Person links are derived from the assertions supporting each step, not only from direct Person steps.</p></section>
    <div className="story-layout"><div>{[...story.steps].sort((a,b)=>(a.temporal_anchor?.from??9999)-(b.temporal_anchor?.from??9999)||story.steps.indexOf(a)-story.steps.indexOf(b)).map((step,idx)=>{ const item=lookup[step.ref], inter=intersections.get(step.ref), label=item?('type' in item?item.name:item.question):step.ref, people=peopleForStep(data,step); return <article key={step.id} className={`story-card panel ${/problem|gap/i.test(step.role)?'problem':''} ${inter?'crossing':''}`}><div className="story-index">{idx+1}</div><div className="story-meta"><span>{step.role.toUpperCase()}</span><span>{step.temporal_anchor?.from||yearFor(item)}</span></div><h3>{label}</h3>{step.narrative&&<p>{step.narrative}</p>}<div className="story-actions">{inter&&<button onClick={onNetwork}>See crossing in Network</button>}{people.map(p=><button key={p.id} onClick={()=>onOpenPerson(p.id)}>Open {short(p.name,18)}</button>)}{inter&&<button onClick={()=>onSheet(<IntersectionSheet intersection={inter} data={data} onOpen={()=>{}}/>)}>Other Stories</button>}</div></article>; })}</div><aside className="parallel-rail"><div className="rail-line">{data.stories.slice(0,4).map((s,i)=><span key={s.id} style={{top:`${15+i*22}%`,background:storyColor(s.id)}} title={s.title}/>)}</div></aside></div></>;
}

function PersonView({ data, personId, onStory }: { data:Dataset; personId:string; onStory:(id:string)=>void }) {
  const person=data.graph.entities.find(e=>e.id===personId&&e.type==='Person')||data.graph.entities.find(e=>e.type==='Person')!;
  const assertions=data.graph.assertions.filter(a=>a.subject===person.id||a.object===person.id);
  const relevantStories=data.stories.filter(s=>storyMentionsPerson(data,s,person.id));
  const initials=person.name.split(' ').map(x=>x[0]).slice(0,2).join('');
  return <section className="panel person-card"><div className="person-head"><div className="avatar">{initials}</div><div><h2>{person.name}</h2><p>{person.start_year}–{person.end_year||''} · {(person.fields||[]).join(' · ')}</p></div></div><div className="metrics"><div><b>{relevantStories.length}</b><span>Story appearances</span></div><div><b>{assertions.length}</b><span>accepted links</span></div><div><b>{person.fields?.length||0}</b><span>fields</span></div></div><h3 className="section-title">Contribution history</h3><div className="contribution-list">{assertions.map(a=><div key={a.id}><span>{a.perspective||'historical'}</span><b>{humanize(a.predicate)}</b><p>{a.subject===person.id?a.object:a.subject}</p></div>)}</div><h3 className="section-title">Stories</h3><div className="story-chips">{relevantStories.length?relevantStories.map(s=><button key={s.id} onClick={()=>onStory(s.id)}>{s.title}</button>):<span className="muted">No reviewed Story currently connects to this person.</span>}</div></section>;
}

function assertionPeople(data:Dataset, refs:string[] = []) {
  const assertionMap=new Map(data.graph.assertions.map(a=>[a.id,a])); const personIds=new Set(data.graph.entities.filter(e=>e.type==='Person').map(e=>e.id)); const ids=new Set<string>();
  refs.forEach(ref=>{ const a=assertionMap.get(ref); if(!a) return; if(personIds.has(a.subject)) ids.add(a.subject); if(personIds.has(a.object)) ids.add(a.object); });
  return data.graph.entities.filter(e=>ids.has(e.id));
}
function peopleForStep(data:Dataset, step:StoryStep) { return assertionPeople(data,step.assertion_refs||[]); }
function peopleForStories(data:Dataset, stories:Story[]) { const ids=new Set<string>(); stories.forEach(s=>s.steps.forEach(st=>peopleForStep(data,st).forEach(p=>ids.add(p.id)))); return data.graph.entities.filter(e=>ids.has(e.id)); }
function storyMentionsPerson(data:Dataset, story:Story, personId:string) { return story.steps.some(st=>st.ref===personId || peopleForStep(data,st).some(p=>p.id===personId)); }
function buildLookup(data:Dataset):Record<string,Entity|Question> { return Object.fromEntries([...data.graph.entities,...data.graph.questions].map(x=>[x.id,x])); }
function short(s:string,n:number){return s.length>n?s.slice(0,n-1)+'…':s;}
function yearFor(item?:Entity|Question){if(!item)return'';return'type'in item?String(item.start_year||''):String(item.period?.from||'');}
function humanize(s:string){return s.replaceAll('_',' ');}
function letter(v:View){return({Atlas:'A',Network:'B',Story:'C',Person:'D'} as const)[v];}
function icon(v:View){return({Atlas:'⌘',Network:'⋈',Story:'↧',Person:'●'} as const)[v];}

createRoot(document.getElementById('root')!).render(<App />);