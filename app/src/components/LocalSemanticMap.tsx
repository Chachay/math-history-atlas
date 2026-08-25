import React, { useMemo, useState } from 'react';
import { GraphEdge, GraphNode, SemanticGraph, getNode } from '../lib/graphQueries';
import './localSemanticMap.css';

type StoryStepLike = { ref:string; assertion_refs?:string[]; temporal_anchor?:{from?:number;to?:number|null} };
type StoryLike = { id:string; title:string; steps:StoryStepLike[] };
type LegacyAssertion = { id:string; subject:string; object:string };

type Props = {
  graph: SemanticGraph;
  story?: StoryLike;
  legacyAssertions?: LegacyAssertion[];
  initialFocusId?: string;
  mode?: 'story'|'network';
  onFocusChange?: (id:string)=>void;
};

const KIND_LABEL:Record<string,string>={Work:'Work',Problem:'Problem',Result:'Result',Concept:'Concept',ConceptState:'Concept state',Person:'Person',Event:'Event'};

function year(node:GraphNode){ return node.period?.from ?? node.start_year; }
function edgeKey(edge:GraphEdge){ return `${edge.subject}:${edge.predicate}:${edge.object}`; }

function storySeeds(graph:SemanticGraph, story:StoryLike|undefined, legacyAssertions:LegacyAssertion[]){
  const ids=new Set<string>();
  if(!story) return ids;
  const nodeIds=new Set(graph.nodes.map(n=>n.id));
  const assertionMap=new Map(legacyAssertions.map(a=>[a.id,a]));
  for(const step of story.steps){
    if(nodeIds.has(step.ref)) ids.add(step.ref);
    for(const ref of step.assertion_refs||[]){
      const a=assertionMap.get(ref);
      if(!a) continue;
      if(nodeIds.has(a.subject)) ids.add(a.subject);
      if(nodeIds.has(a.object)) ids.add(a.object);
    }
  }
  return ids;
}

function incidentEdges(graph:SemanticGraph, ids:Set<string>){
  const defaults=new Set(graph.default_edge_ids);
  return [...graph.claims.filter(e=>defaults.has(e.id)),...graph.structural_edges].filter(e=>ids.has(e.subject)||ids.has(e.object));
}

function expandConceptWindows(graph:SemanticGraph, ids:Set<string>){
  const conceptIds=new Set<string>();
  for(const id of ids){
    const node=getNode(graph,id);
    if(!node) continue;
    if(node.node_kind==='Concept') conceptIds.add(node.id);
    if(node.node_kind==='ConceptState'&&node.concept_id) conceptIds.add(node.concept_id);
  }
  const expanded=new Set(ids);
  for(const conceptId of conceptIds){
    expanded.add(conceptId);
    graph.nodes.filter(n=>n.node_kind==='ConceptState'&&n.concept_id===conceptId).forEach(n=>expanded.add(n.id));
  }
  return expanded;
}

function nodeOrder(a:GraphNode,b:GraphNode){
  const ay=year(a)??999999, by=year(b)??999999;
  if(ay!==by)return ay-by;
  const order:Record<string,number>={Work:1,Problem:2,Result:3,ConceptState:4,Concept:5,Person:6};
  return (order[a.node_kind]??9)-(order[b.node_kind]??9)||a.name.localeCompare(b.name);
}

export function LocalSemanticMap({graph,story,legacyAssertions=[],initialFocusId,mode='story',onFocusChange}:Props){
  const baseSeeds=useMemo(()=>storySeeds(graph,story,legacyAssertions),[graph,story,legacyAssertions]);
  const seeds=useMemo(()=>expandConceptWindows(graph,baseSeeds),[graph,baseSeeds]);
  const edges=useMemo(()=>incidentEdges(graph,seeds),[graph,seeds]);
  const localIds=useMemo(()=>{ const ids=new Set(seeds); edges.forEach(e=>{ids.add(e.subject);ids.add(e.object)}); return ids; },[seeds,edges]);
  const localNodes=useMemo(()=>graph.nodes.filter(n=>localIds.has(n.id)).sort(nodeOrder),[graph,localIds]);
  const first=initialFocusId&&localIds.has(initialFocusId)?initialFocusId:(localNodes.find(n=>seeds.has(n.id))?.id||localNodes[0]?.id);
  const [focusId,setFocusId]=useState(first);
  const focus=focusId?getNode(graph,focusId):undefined;

  const focusNode=(id:string)=>{setFocusId(id);onFocusChange?.(id)};
  const conceptId=focus?.node_kind==='Concept'?focus.id:focus?.concept_id;
  const conceptStates=conceptId?graph.nodes.filter(n=>n.node_kind==='ConceptState'&&n.concept_id===conceptId).sort(nodeOrder):[];
  const direct=focus?edges.filter(e=>e.subject===focus.id||e.object===focus.id):[];
  const branchNodes=direct.flatMap(e=>{const id=e.subject===focus?.id?e.object:e.subject;const n=getNode(graph,id);return n?[n]:[]}).filter((n,i,arr)=>arr.findIndex(x=>x.id===n.id)===i);

  if(!localNodes.length)return <section className="local-map empty"><p>No reviewed semantic material is projected for this Story yet.</p></section>;

  return <section className={`local-map mode-${mode}`} aria-label={mode==='story'?'Story semantic map':'Local semantic map'}>
    <header className="local-map-head"><div><span className="eyebrow">{mode==='story'?'STORY MAP':'LOCAL MAP'}</span><h3>{mode==='story'?'The researched path and its nearby branches':'Semantic neighborhood'}</h3></div><p>{mode==='story'?'Strong nodes belong to the Story evidence spine. Nearby branches remain available without becoming Story transitions.':'Select an object to expand its local researched context.'}</p></header>

    <div className="local-map-scroll">
      <div className="local-map-track">
        {localNodes.map(node=>{
          const active=seeds.has(node.id), focused=focus?.id===node.id;
          return <button key={node.id} className={`map-node kind-${node.node_kind.toLowerCase()} ${active?'spine':''} ${focused?'focused':''}`} onClick={()=>focusNode(node.id)}>
            <small>{KIND_LABEL[node.node_kind]||node.node_kind}{year(node)?` · ${year(node)}`:''}</small><b>{node.name}</b>
          </button>;
        })}
      </div>
    </div>

    {focus&&<div className="local-focus-panel">
      <div className="local-focus-title"><span>{KIND_LABEL[focus.node_kind]||focus.node_kind}</span><h4>{focus.name}</h4>{focus.detail&&<p>{focus.detail}</p>}</div>
      {conceptStates.length>1&&<div className="concept-window"><b>Concept evolution</b><div>{conceptStates.map(state=><button key={state.id} className={state.id===focus.id?'active':''} onClick={()=>focusNode(state.id)}><time>{year(state)||'—'}</time><span>{state.name}</span></button>)}</div><small>Chronological order groups attested states; it does not by itself assert causal development.</small></div>}
      {branchNodes.length>0&&<div className="branch-window"><b>{mode==='story'?'Nearby branches':'Connections'}</b><div>{branchNodes.slice(0,8).map(node=><button key={node.id} className={seeds.has(node.id)?'spine-branch':''} onClick={()=>focusNode(node.id)}><span>{KIND_LABEL[node.node_kind]||node.node_kind}</span><strong>{node.name}</strong></button>)}</div></div>}
    </div>}

    <footer className="local-map-legend"><span><i className="legend-spine"/>Story evidence</span><span><i/>Semantic context</span><span>{edges.length} researched connections</span></footer>
  </section>;
}
